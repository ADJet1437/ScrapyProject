# -*- coding: utf8 -*-
import requests
import traceback
import StringIO
import datetime
import os
import gzip
import csv
import sys
import re
from requests.auth import HTTPDigestAuth
from lxml import etree
import dateparser
from scrapy.http import Request


from alascrapy.lib.log import log_exception
from alascrapy.lib.amazon_graph import CategoryTree
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.items import ProductItem, CategoryItem, ReviewItem, AmazonProduct, ProductIdItem
from alascrapy.lib.amazon import AmazonAPI
from alascrapy.lib.generic import remove_querystring, normalize_price, \
    parse_float, download_file, md5, get_full_url, date_format
from alascrapy.lib.dao.amazon import get_feed_categories, update_feed_category
from alascrapy.lib.mq.mq_publisher import MQPublisher
from alascrapy.lib.dao.incremental_scraping import \
    get_latest_user_review_date, get_incremental, update_incremental


class AmazonSpider(AlaSpider):
    user = "alaTest"
    password = "M94Y6vKb6Ss8EeKT"

    def __init__(self, *a, **kw):
        super(AmazonSpider, self).__init__(*a, **kw)
        self.amazon_api = AmazonAPI(self)
        self.category_tree = CategoryTree(self.country_code)
        self._amazon_check_reviews = {}
        self._review_scrape = {}

    def download_feed(self, feed):
        dir = self.get_temp_dir()
        download_feed_url = "https://assoc-datafeeds-eu.amazon.com/datafeed/getFeed"
        auth = HTTPDigestAuth(self.user, self.password)
        params = {'filename': feed['filename']}

        abs_filepath = os.path.join(dir, feed['filename'])
        r = requests.get(download_feed_url, auth=auth, params=params,
                         allow_redirects=False)

        for i in range(3):
            if r.status_code==302:
                download_file(r.headers['location'], abs_filepath)
            else:
                raise Exception("Did not get download redirect url")

            if md5(abs_filepath) == feed['md5']:
                return abs_filepath
            os.unlink(abs_filepath)
        raise Exception("File %s does not match md5 after three tries" % abs_filepath)

    def get_feed_list(self):
        list_feed_url = "https://assoc-datafeeds-eu.amazon.com/datafeed/listFeeds"

        for i in range(3):
            available_feeds = requests.get(list_feed_url,
                                           params = {'format':'text/xml'},
                                           auth=HTTPDigestAuth(self.user, self.password))
            if available_feeds.status_code == 200:
                return available_feeds.text
        raise Exception("Could not download feed list after three tries")

    def extract_feeds(self, tree, xpath):
        feeds_xml = tree.xpath(xpath)
        feeds=[]
        for feed_xml in feeds_xml:
            feed = {
                'filename': feed_xml.xpath("./Filename")[0].text,
                'size': feed_xml.xpath("./Size")[0].text,
                'date': feed_xml.xpath("./LastModified")[0].text,
                'md5': feed_xml.xpath("./MD5")[0].text.strip("\" "),
            }
            feed['date'] = dateparser.parse(feed['date'],
                                            ['%c'], languages=['en'])
            feeds.append(feed)
        sorted(feeds, key=lambda k: k['date'])
        return feeds

    def get_latest_date(self, date_str):
        if date_str:
            return dateparser.parse(date_str, ['%Y-%m-%d %H:%M:%S'])
        else:
            return datetime.datetime.min

    def process_feed(self, category, feed):
        temp_dir = self.get_temp_dir()
        latest_load = category['last_feed_date'] if category['last_feed_date'] \
                        else datetime.datetime.min
        if feed['date'] > latest_load:
            try:
                feed['filepath'] = self.download_feed(feed)
            except Exception, e:
                log_exception(self.logger, e)
                return

            for item in self.parse_feed(feed):
                yield item

            last_date = feed['date'].strftime('%Y-%m-%d %H:%M:%S')
            update_feed_category(self.mysql_manager, category['feed_name'],
                                     self.spider_conf['source_id'], last_date)
            abs_filepath = os.path.join(temp_dir, feed['filename'])
            os.unlink(abs_filepath)


    def parse(self, response):
        feed_categories = get_feed_categories(self.mysql_manager, self.spider_conf[
            'source_id'] )
        available_feeds = self.get_feed_list()
        f = StringIO.StringIO(available_feeds)
        tree = etree.parse(f)
        for category in feed_categories:
            xpath = self.feeds_xpath(category['feed_name'])
            feeds = self.extract_feeds(tree, xpath)
            if not feeds:
                self.logger.warning("""AMAZON WARNING: No
                                       feed found in amazon %s for
                                       category %s""" % (self.country_code,
                                                         category['feed_name']))
                continue
            if len(feeds) > 1:
                self.logger.warning("""AMAZON WARNING: More than
                                       one feed in amazon %s for
                                       category %s: %s""" % (self.country_code,
                                                         category['feed_name'],
                                                         str(feeds)))
                continue

            feed = feeds[0]
            for item in self.process_feed(category, feed):
                yield item

    def publish_reviews(self):
        reviews_to_send = []
        for asin in list(self._review_scrape):
            review_dict = self._review_scrape.pop(asin)
            reviews_to_send.append(review_dict)

        reviews_to_send.sort(key=lambda x: x['sales_rank'])
        mq_publisher = MQPublisher(self.project_conf, "SCHEDULER")
        source_id = self.spider_conf['source_id']
        queue_name = "amazon_reviews_%s" % source_id
        routing_key = str(source_id)
        exchange = self.project_conf.get("SCHEDULER", "exchange")

        mq_publisher._channel.queue_declare(queue=queue_name, durable=True,
                                            exclusive=False, auto_delete=False)
        mq_publisher._channel.queue_bind(queue=queue_name,
                                         exchange=exchange,
                                         routing_key=routing_key)

        for message in reviews_to_send:
            mq_publisher.publish_message(message, exchange, routing_key)


class AmazonCSV(AmazonSpider):

    associate_tag = 'alatestcouk0e-21'
    subscription_id = '0EWA6R5AGNW9AA6JF8R2'
    secret_key = '1RFwtwfJeqi6fTzO/hxmf+J9E8Nfai2rHWSwy6xu'

    def __init__(self, *a, **kw):
        super(AmazonCSV, self).__init__(*a, **kw)
        csv.field_size_limit(sys.maxsize)

    def feeds_xpath(self, category):
        feed_path = "//Feed/Filename[%s]/.."
        conditions = """contains(text(),'%s_') and
                        contains(text(),'_%s.csv')
                     """ % (self.country_code, category)
        return feed_path % conditions

    def parse_manual(self, line):
        fields = []
        escaped = False
        in_quotes = False
        skip_next = False
        field = ""
        for i in range(0, len(line)):
            if skip_next:
                skip_next = False
                continue
            elif line[i] == '\\' and not escaped:
                escaped = True
            elif line[i]=='"' and in_quotes and not escaped and i!=len(line)-1:
                if line[i+1]=='"':
                    field+='\\"\\"'
                    skip_next=True
                elif line[i+1]!=',' and line[i+1]!='\n':
                    field+='\\"'
                else:
                    in_quotes = not in_quotes
            elif line[i]=='"' and not escaped:
                in_quotes = not in_quotes
            elif line[i]==',' and not in_quotes:
                fields.append(field)
                field=""
            else:
                escaped=False
                field+=line[i]
        fields.append(field)
        return fields

    def parse_feed(self, feed, type="base"):
        error_msg = "Could not parse line %s in feed %s.\n Uncaught Exception %s.\n%s"
        with gzip.open(feed['filepath']) as f:
            f.next() #skip header
            for line in f:
                row = csv.reader([line]).next()
                if type=="delta" and row[-1]!="ADD":
                    continue

                try:
                    for item in self.parse_row(row):
                        yield item
                except Exception:
                    row2 = self.parse_manual(line)
                    try:
                        for item in self.parse_row(row2):
                            yield item
                    except Exception, e:
                        self.logger.error(error_msg % (line,
                                                       feed['filename'], e,
                                                       traceback.format_exc()))

    def get_nodes(self, row):
        nodes = []
        node_paths = {}
        for node_schema in self.schema['nodes']:
            node_id = row[node_schema['node']]
            if node_id:
                graph_node_id = "%s%s" % (self.country_code, node_id)
                node_string_path =  row[node_schema['node_path']]
                node_paths[graph_node_id] = node_string_path

                node = self.category_tree.categories.get(graph_node_id, None)
                if not node:
                    browse_node = self.amazon_api.get_node(node_id)
                    if type(browse_node) is dict:
                        node = self.category_tree.add_new_category(browse_node,
                                                                   self.amazon_api,
                                                                   self.country_code)
                    elif browse_node == "AWS.InvalidParameterValue":
                        self.category_tree.delete_category(graph_node_id)
                        continue
                    else:
                        self.logger.warning("Unknown error from amazon API.")
                        continue
                if node:
                    nodes.append(node)
            return nodes, node_paths

    def parse_row(self, row):
        asin = row[self.schema['asin']]
        nodes, node_paths = self.get_nodes(row)

        do_not_load = True
        for node in nodes:
            do_not_load = do_not_load and bool(node["do_not_load"])

        for node in nodes:
            category = CategoryItem()
            category['category_path'] = str(node['id'])
            category['category_leaf'] = str(node['id'])
            category['category_string'] = node_paths[node['id']]
            category['do_not_load'] = do_not_load
            yield category

            ocn_nodes = [node for node in nodes if not bool(node["is_root"])
                         and not node["do_not_load"]]

            if not ocn_nodes:
                continue

            if len(ocn_nodes)==1:
                deepest_node = ocn_nodes[0]
            else:
                deepest = 0
                deepest_node = None
                for category in ocn_nodes:
                    current_length = category['shortest_length_root']
                    if current_length >= deepest:
                        deepest = current_length
                        deepest_node = category

            if deepest_node:
                ocn = deepest_node['id']

                product_dict = AmazonProduct()
                product = ProductItem()
                product["ProductName"] = row[self.schema['name']]
                if not product["ProductName"]:
                    return
                product["source_internal_id"] = asin
                product["OriginalCategoryName"] = str(ocn)
                for url_key in self.schema['url']:
                    if row[url_key]:
                        product["TestUrl"] = remove_querystring(row[url_key])
                        break

                for pic_key in self.schema['image']:
                    if row[pic_key]:
                        product["PicURL"] = row[pic_key]
                        break
                product["ProductManufacturer"] = row[self.schema['manufacturer']]
                product_dict['product'] = product

                asin_item = self.product_id(product)
                asin_item['ID_kind'] = self.asin_kind
                asin_item['ID_value'] = asin
                product_dict['asin'] = asin_item

                ean_value = row[self.schema['ean']]
                if ean_value:
                    ean = self.product_id(product)
                    ean['ID_kind'] = 'EAN'
                    ean['ID_value'] = ean_value
                    product_dict['ean'] = ean

                mpn_value = row[self.schema['mpn']]
                if mpn_value:
                    mpn = self.product_id(product)
                    mpn['ID_kind'] = 'MPN'
                    mpn['ID_value'] = mpn_value
                    product_dict['mpn'] = mpn

                salesrank_value = row[self.schema['salesrank']]
                if salesrank_value:
                    salesrank = self.product_id(product)
                    salesrank['ID_kind'] = 'amazon_salesrank'
                    salesrank['ID_value'] = int(salesrank_value)
                    product_dict['salesrank'] = salesrank

                if 'parent_asin' in self.schema:
                    parent_asin_value = row[self.schema['parent_asin']]
                    if parent_asin_value:
                        amazon_group = self.product_id(product)
                        amazon_group['ID_kind'] = 'amazon_group_id'
                        amazon_group['ID_value'] = parent_asin_value
                        product_dict['amazon_group'] = amazon_group

                for price_key in self.schema['price']:
                    if row[price_key]:
                        price = parse_float(row[price_key])
                        if price:
                            price_item = self.product_id(product)
                            price_item['ID_kind'] = 'price'
                            price_item['ID_value'] = normalize_price(price)
                            product_dict['price'] = price_item
                            break
                yield product_dict


class AmazonReviewsSpider(AlaSpider):

    rating_re = re.compile('a-star-(\d)')
    custom_settings = {'COOKIES_ENABLED': True,
                       'DOWNLOADER_MIDDLEWARES':
                           {'alascrapy.middleware.forbidden_requests_middleware.ForbiddenRequestsMiddleware': None},
                       'HTTPCACHE_ENABLED': True}
    download_delay=3

    def __init__(self, *args, **kwargs):
        super(AmazonReviewsSpider, self).__init__(self, *args, **kwargs)
        self.asin = kwargs['asin']
        # if send_mq argument is presented and not evaluated to False, then a message will be send to
        # 'load' to fetch the scraped reviews
        self.send_mq = kwargs.get('send_mq', 0)
        self.last_review_in_db = get_latest_user_review_date(self.mysql_manager,
                                                             self.spider_conf['source_id'],
                                                             self.amazon_kind,
                                                             self.asin)
        self.incremental = get_incremental(self.mysql_manager,
                                           self.spider_conf['source_id'],
                                           self.amazon_kind,
                                           self.asin)
        self.update_incremental_kind = self.project_conf.getboolean("OUTPUT",
                                                    "update_incremental_kind")

    def start_requests(self):
        asin = self.asin
        start_url = self.start_url_format % asin
        yield Request(url=start_url, callback=self.parse_reviews)

    def _format_date(self, raw_review, date_xpath):
        date = self.extract_xpath(raw_review, date_xpath)
        date = date_format(date, self.date_format, languages=[self.language])
        return date

    def parse_reviews(self, response):
        product_name_xpath = "//div[contains(@class, 'product-title')]//text()"
        product_url_xpath = "(//a[@data-hook='product-link'])[1]/@href"
        reviews_xpath = "//div[@id='cm_cr-review_list']/div[@id]"
        next_page_xpath = "//div[@id='cm_cr-pagination_bar']//li[@class='a-last']/a/@href"

        title_xpath=".//a[contains(@class,'review-title')]/text()"
        review_url_xpath=".//a[contains(@class,'review-title')]/@href"
        summary_xpath = ".//span[contains(@class,'review-text')]/text()"
        author_xpath = ".//a[contains(@class,'author')]/text()"
        rating_xpath = ".//i[contains(@class, 'review-rating')]/@class"
        date_xpath = ".//span[contains(@class, 'review-date')]/text()"

        product = response.meta.get('product')

        if not product:
            product_url = self.extract_xpath(response, product_url_xpath)
            if self.asin not in product_url:
                product_url = response.url
            else:
                product_url = get_full_url(response, product_url)

            product_name = self.extract_xpath(response, product_name_xpath)
            product = ProductItem.from_response(response, product_name=product_name,
                                                source_internal_id=self.asin,
                                                url=product_url)
            yield product

        reviews = response.xpath(reviews_xpath)
        date = ''

        for raw_review in reviews:
            rating = ''
            title = self.extract_xpath(raw_review, title_xpath)
            review_url = self.extract_xpath(raw_review, review_url_xpath)
            review_url = get_full_url(response.url, review_url)
            summary = self.extract_all_xpath(raw_review, summary_xpath)
            author = self.extract_xpath(raw_review, author_xpath)
            raw_rating = self.extract_xpath(raw_review, rating_xpath)
            match = re.search(self.rating_re, raw_rating)
            if match:
                rating = match.group(1)
            date = self._format_date(raw_review, date_xpath)

            review = ReviewItem.from_product(product=product, tp='USER', rating=rating,
                                             scale=5, date=date, author=author,
                                             summary=summary, url=review_url, title=title)
            yield review

        if not date:
            retries = response.meta.get('ama_retries', 0)
            if retries >= 8: #8 tor processes
                incremental_value = '0'
                if self.incremental is None:
                    incremental = ProductIdItem()
                    incremental['source_internal_id'] = self.asin
                    incremental['ID_kind'] = 'incremental_scraping'
                    incremental['ID_value'] = incremental_value
                    yield incremental
                elif self.update_incremental_kind:
                    update_incremental(self.mysql_manager,
                                       self.spider_conf['source_id'],
                                       self.amazon_kind,
                                       self.asin,
                                       incremental_value)
                self.logger.warning("Max retries, blocked: %s" % response.url)
                return

            retryreq = response.request.copy()
            retryreq.meta['ama_retries'] = retries + 1
            retryreq.meta['dont_merge_cookies'] = True
            retryreq.dont_filter = True
            retryreq.cookies = {}
            yield retryreq
            return

        last_date_in_page = dateparser.parse(date, ["%Y:%m:%d"])
        if self.last_review_in_db and self.incremental:
            if self.last_review_in_db > last_date_in_page:
                return

        next_page_url = self.extract_xpath(response, next_page_xpath)
        if next_page_url:
            next_page_url = get_full_url(response.url, next_page_url)
            request = Request(next_page_url, callback=self.parse_reviews)
            request.meta['product'] = product
            yield request
        else:
            incremental_value = '1'
            if self.incremental is None:
                incremental = ProductIdItem()
                incremental['source_internal_id'] = self.asin
                incremental['ID_kind'] = 'incremental_scraping'
                incremental['ID_value'] = incremental_value
                yield incremental
            elif self.update_incremental_kind:
                update_incremental(self.mysql_manager,
                                   self.spider_conf['source_id'],
                                   self.amazon_kind,
                                   self.asin,
                                   incremental_value)
