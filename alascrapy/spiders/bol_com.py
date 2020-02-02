#coding:utf-8
__author__ = 'leo'

import json
from copy import deepcopy

import dateparser
from scrapy.http import Request

from alascrapy.items import CategoryItem, ProductItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import set_query_parameter, \
    get_query_parameter, date_format
from alascrapy.lib.dao.incremental_scraping import get_latest_user_review_date
from alascrapy.lib.extruct_helper import get_review_items_from_microdata


class BolComSpider(AlaSpider):
    name = 'bol_com'
    allowed_domains = ['bol.com']
    open_api_key = "224E5E87BB054B39B208D73D944C66C9"
    category_url = 'https://api.bol.com/catalog/v4/lists/?dataoutput=categories&format=json'
    product_url = 'https://api.bol.com/catalog/v4/lists/?dataoutput=products&format=json'
    review_url = 'https://www.bol.com/nl/rnwy/productPage/reviews.html?productId=%s'
    limit = 10 #number of products/reviews
    default_offset = 3
    download_delay = 2.2

    def start_requests(self):
        category_url = set_query_parameter(self.category_url, 'apikey',
                                           self.open_api_key)

        request = Request(category_url, self.parse_category)
        return [request]

    def parse_category(self, response):
        body = json.loads(response.body_as_unicode())
        category_path = response.meta.get('category_path', [])
        children_categories = body.get('categories', [])

        if children_categories:
            for _category in children_categories:
                _path = deepcopy(category_path)
                try:
                    if 'name' in _category:
                        _path.append(_category['name'])
                    elif 'Name' in _category:
                        _path.append(_category['Name'])
                except Exception, e:
                    print _category
                    raise e
                category_url = set_query_parameter(self.category_url, 'apikey',
                                                   self.open_api_key)
                category_url = set_query_parameter(category_url, 'ids',
                                                   _category['id'])
                request = Request(category_url, self.parse_category)
                request.meta['category_path'] = _path
                yield request
        else:
            category = CategoryItem()
            category['category_leaf'] = body['originalRequest']['category']['name']
            category['category_string'] = body['originalRequest']['category']['id']
            category['category_path'] = ' | '.join(category_path)
            yield category

            product_url = set_query_parameter(self.product_url, 'apikey',
                                              self.open_api_key)
            product_url = set_query_parameter(product_url, 'ids',
                                              category['category_string'])
            product_url = set_query_parameter(product_url, 'limit',
                                              self.limit)
            product_url = set_query_parameter(product_url, 'offset', 0)

            if not self.should_skip_category(category):
                request = Request(product_url, callback=self.parse_products)
                request.meta['category'] = category
                yield request

    def parse_products(self, response):
        category = response.meta['category']
        body = json.loads(response.body_as_unicode())
        if body["totalResultSize"] == 0:
            return
        products = body.get('products', [])

        for raw_product in products:
            url = ''
            pic_url = ''
            for _url in raw_product['urls']:
                url = _url['value']
                if _url['key'] == "DESKTOP":
                    break

            for _image in raw_product['images']:
                pic_url = _image['url']
                if _image['key'] == "L":
                    break
            product_name = raw_product['title']
            source_internal_id =raw_product['id']
            manufacturer = raw_product.get('specsTag', None) # specTags == manufacturer? YES! For reasons...
            ean_value = raw_product['ean']

            product = ProductItem.from_response(response, category=category, product_name=product_name,
                                                source_internal_id=source_internal_id, url=url,
                                                manufacturer=manufacturer, pic_url=pic_url)

            bol_id = self.product_id(product, kind='bolcom_id', value=source_internal_id)
            if ean_value:
                ean = self.product_id(product, kind='EAN', value=ean_value)

            #go to review page
            review_url = self.review_url % source_internal_id
            request = Request(review_url, callback=self.parse_reviews)
            request.meta['use_proxy'] = True
            request.meta['product'] = product
            request.meta['bol_id'] = bol_id
            if ean:
                request.meta['ean'] = ean
            yield request

        #go to "next" page
        offset = get_query_parameter(response.url, 'offset')
        offset = int(offset) + self.limit
        if offset > body["totalResultSize"]:
            return

        next_page_url = set_query_parameter(response.url, 'offset', offset)
        request = Request(next_page_url, callback=self.parse_products)
        request.meta['category'] = category
        yield request

    def parse_reviews(self, response):
        reviews_xpath = "//li[@itemprop='review']"
        pros_xpath = ".//li[contains(@class, 'review-pros-and-cons__attribute--pro')]//text()"
        cons_xpath = ".//li[contains(@class, 'review-pros-and-cons__attribute--con')]//text()"

        product = response.meta['product']

        if not 'last_date_db' in response.meta:
            bol_id = response.meta['bol_id']
            ean = response.meta.get('ean', None)
            yield product
            yield bol_id
            yield ean

            last_review_in_db = get_latest_user_review_date(self.mysql_manager,
                                                            self.spider_conf['source_id'],
                                                            bol_id["ID_kind"],
                                                            bol_id["ID_value"])
        else:
            last_review_in_db = response.meta['last_date_db']

        review_items = get_review_items_from_microdata(self, 'USER', response, product, reviews_xpath,
                                                       pros_xpath, cons_xpath)

        if not review_items:
            return

        for review in review_items:
            yield review

        #incremental scraping
        date = review['TestDateText']
        last_date_in_page = dateparser.parse(date, ["%Y-%m-%d"])

        if last_review_in_db > last_date_in_page:
            return

        offset = get_query_parameter(response.url, 'offset')
        if not offset:
            offset = self.default_offset
        offset = int(offset) + self.limit

        next_page_url = set_query_parameter(response.url, 'offset', offset)
        next_page_url = set_query_parameter(next_page_url, 'limit', self.limit)
        request = Request(next_page_url, callback=self.parse_reviews)
        request.meta['use_proxy'] = True
        request.meta['last_date_db'] = last_review_in_db
        request.meta['product'] = product
        yield request
