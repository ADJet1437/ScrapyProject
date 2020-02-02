# -*- coding: utf8 -*-
import StringIO

import sys

from alascrapy.items import ProductItem, CategoryItem
from alascrapy.lib.conf import get_project_conf
from alascrapy.lib.dao.brands import load_icecat_brands_by_category_id
from alascrapy.lib.mq.mq_publisher import MQPublisher
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.amazon import AmazonAPI
from alascrapy.lib.dao.categories import get_categories_to_load_from_source
from alascrapy.lib.generic import remove_prefix, first_or_empty
from lxml import etree
from scrapy.http.request import Request

from alascrapy.spiders.base_spiders.amazon import AmazonSpider

SALESRANK_LIMIT = 100000

"""
    This spider uses Neo4J database to find the whitelist categories on Amazon and then
    query Amazon Product Advertising API to get products info and reviews.
"""
class AmazonAPISpider(AlaSpider):
    custom_settings = {'DOWNLOADER_MIDDLEWARES':
                           {'alascrapy.middleware.user_agent_middleware.RotateUserAgentMiddleware': None,
                            'alascrapy.middleware.amazon_auth_middleware.AmazonAuthMiddleware': 140},
                       'HTTPCACHE_ENABLED': True}
    handle_httpstatus_list = range(100,599)
    generic_categories = [410001, 4486]

    def __init__(self, *a, **kw):
        super(AmazonAPISpider, self).__init__(*a, **kw)
        self.project_conf = get_project_conf()
        self.amazon_apis = {}
        self.categories_to_scrape = {}
        self.brands_by_category_id = {}
        self._review_scrape = {}
        self.publishers = {}

    def parse(self, response):
        print('Parsing ' + response.url)
        if 'https://www.amazon.' in response.url:
            source_key = remove_prefix(response.url, 'https://www.amazon.').split('/')[0]

            if source_key not in self.categories_to_scrape:
                ala_source_id = self.spider_conf['source_id']
                self.categories_to_scrape[source_key] = get_categories_to_load_from_source(self.mysql_manager, ala_source_id, source_key)
                if not self.categories_to_scrape[source_key]:
                    self.logger.info(
                        'No category found for source prefix=^(' + source_key + ')[[:digit:]]+$ and source_id={source_id}'.format(
                            source_id=ala_source_id))

            if source_key not in self.amazon_apis:
                self.amazon_apis[source_key] = AmazonAPI(self)
            amazon_api = self.amazon_apis[source_key]

            for category in self.categories_to_scrape[source_key]:
                cat_id = category['category_id']
                node_id = remove_prefix(category['OriginalCategoryName'],
                                        source_key)
                if cat_id in self.generic_categories:
                    products_url = amazon_api.item_search_full_url(node_id,
                                        doAuth=False)

                    req = Request(url=products_url, callback=self.parsePage,
                                  errback=self.errback)
                    req.meta['ItemPage'] = 1
                    req.meta['source_key'] = source_key
                    req.meta['node_id'] = node_id
                    req.meta['source_id'] = category['source_id']
                    yield req
                else:
                    if category['category_id'] not in self.brands_by_category_id:
                        self.brands_by_category_id[category['category_id']] = \
                            load_icecat_brands_by_category_id(self.mysql_manager,
                                                              cat_id)
                    for brand in self.brands_by_category_id[cat_id]:
                        products_url = amazon_api.item_search_full_url(node_id,
                                brand=brand['BrandMasterName'],
                                doAuth=False)

                        req = Request(url=products_url, callback=self.parsePage,
                                      errback=self.errback)
                        req.meta['ItemPage'] = 1
                        req.meta['source_key'] = source_key
                        req.meta['node_id'] = node_id
                        req.meta['brand'] = brand['BrandMasterName']
                        req.meta['source_id'] = category['source_id']
                        yield req

    def errback(self, failure):
        error_msg = "Error parsing: %s\nTraceback: %s"

        self.logger.error(error_msg % (str(failure.getErrorMessage()),
                                       str(failure.getTraceback())) )

    def publish_reviews(self, source_id):
        reviews_to_send = []
        for asin in list(self._review_scrape):
            review_dict = self._review_scrape.pop(asin)
            reviews_to_send.append(review_dict)

        reviews_to_send.sort(key=lambda x: x['sales_rank'])

        if reviews_to_send:
            exchange = self.project_conf.get("SCHEDULER", "exchange")
            routing_key = str(source_id)

            if not self.publishers.get(source_id):
                mq_publisher = MQPublisher(self.project_conf, "SCHEDULER")
                queue_name = "amazon_reviews_%s" % source_id
                mq_publisher._channel.queue_declare(queue=queue_name, durable=True,
                                                    exclusive=False, auto_delete=False)
                mq_publisher._channel.queue_bind(queue=queue_name,
                                                 exchange=exchange,
                                                 routing_key=routing_key)
                self.publishers[source_id] = mq_publisher

            mq_publisher = self.publishers.get(source_id)
            for message in reviews_to_send:
                mq_publisher.publish_message(message, exchange, routing_key)

    def parsePage(self, response):

        if response.status is not 200:
            self.logger.error(str(response.status) + ' : ' + response.url)

        if hasattr(response, 'text'):
            # print('parsing page ' + response.url)
            xml = response.text
            xml = xml.replace(' xmlns=', ' xmlnamespace=')
            f = StringIO.StringIO(xml)
            tree = etree.parse(f)

            try:
                # totalResults = int(tree.xpath("//ItemSearchResponse/Items/TotalResults/text()")[0])
                totalResults = len(tree.xpath("//ItemSearchResponse/Items/Item"))
                if totalResults:
                    print('Found results for ' + response.url)

                    source_key = response.meta['source_key']

                    salesRank = None
                    for item in tree.xpath('//ItemSearchResponse/Items/Item'):
                        has_reviews = 'true' == (first_or_empty(item.xpath('./CustomerReviews/HasReviews/text()')))
                        salesRank = int(first_or_empty(item.xpath('./SalesRank/text()')) or 0)
                        asin = first_or_empty(item.xpath('./ASIN/text()'))

                        if not has_reviews:
                            self.log(asin + ' doesn\'t have reviews, skipping')
                            print(asin + ' doesn\'t have reviews, skipping')
                            continue

                        if not salesRank:
                            self.log(asin + ' doesn\'t have salesRank, skipping')
                            print(asin + ' doesn\'t have salesRank, skipping')
                            continue

                        if not (salesRank <= SALESRANK_LIMIT):
                            self.log(asin + ' has too low salesRank, skipping')
                            print(asin + ' has too low salesRank, skipping')
                            continue

                        parent_ASIN = first_or_empty(item.xpath('./ParentASIN/text()'))
                        product_url = first_or_empty(item.xpath('./DetailPageURL/text()'))

                        # <Description>All Customer Reviews</Description>
                        item_link_description_all_customer_reviews = item.xpath('./ItemLinks/ItemLink/Description[contains(text(), "All Customer Reviews")]')[0]
                        #product_reviews_url = first_or_empty(item_link_description_all_customer_reviews.xpath('./parent::ItemLink/URL/text()'))
                        image_url = first_or_empty(item.xpath('./LargeImage/URL/text()'))
                        #brand= first_or_empty(item.xpath('./ItemAttributes/Brand/text()'))
                        ean = first_or_empty(item.xpath('./ItemAttributes/EAN/text()'))
                        manufacturer = first_or_empty(item.xpath('./ItemAttributes/Manufacturer/text()'))
                        title = first_or_empty(item.xpath('./ItemAttributes/Title/text()'))
                        #upc = first_or_empty(item.xpath('./ItemAttributes/UPC/text()'))
                        mpn = first_or_empty(item.xpath('./ItemAttributes/MPN/text()'))

                        category = CategoryItem()
                        category['category_path'] = source_key + response.meta['node_id']

                        product = ProductItem.from_response(
                            response,
                            product_name=title,
                            source_internal_id=asin,
                            url=product_url,
                            manufacturer=manufacturer,
                            pic_url=image_url,
                            category=category
                        )
                        product['source_id'] = response.meta['source_id']
                        yield product
                        print('Found the product ' + product['source_internal_id'])

                        asin_item = self.product_id(product, 'amazon_' + source_key + '_id', asin)
                        yield asin_item

                        if ean:
                            ean_item = self.product_id(product, 'EAN', ean)
                            yield ean_item

                        if mpn:
                            mpn_item = self.product_id(product, 'MPN', mpn)
                            yield mpn_item

                        if salesRank:
                            salesrank_item = self.product_id(product, 'amazon_salesrank', int(salesRank))
                            yield salesrank_item

                        if parent_ASIN:
                            amazon_group = self.product_id(product, 'amazon_group_id', parent_ASIN)
                            yield amazon_group

                        _scrape_key = parent_ASIN or asin
                        self._review_scrape[_scrape_key] = {'sales_rank': salesRank,
                                                              'asin': _scrape_key}

                    if totalResults == 10 and salesRank and salesRank <= SALESRANK_LIMIT:
                        itemPage = response.meta['ItemPage']
                        node_id = response.meta['node_id']
                        brand = response.meta.get('brand', None)
                        req = Request(
                            url=self.amazon_apis[
                                source_key].item_search_full_url(node_id,
                                                                 brand=brand,
                                                                 page= 1+itemPage,
                                                                 doAuth=False),
                            callback=self.parsePage, errback=self.errback, meta=response.meta
                        )
                        req.meta['ItemPage'] = 1 + itemPage
                        yield req

                    self.publish_reviews(response.meta['source_id'])
            except IndexError:
                raise Exception('Invalid Response: %s' % xml)