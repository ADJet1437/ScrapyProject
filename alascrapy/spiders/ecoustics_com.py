# -*- coding: utf-8 -*-
import re
from datetime import datetime

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import date_format
import alascrapy.lib.dao.incremental_scraping as incremental_utils


class EcousticsComSpider(AlaSpider):
    name = 'ecoustics_com'
    allowed_domains = ['ecoustics.com']
    start_urls = ['http://www.ecoustics.com/reviews/']

    def __init__(self, *args, **kwargs):
        super(EcousticsComSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

    def parse(self, response):
        review_url_xpath_1 = "//div[@class='read-more-box-wrapper']//a/@href"
        review_url_xpath_2 = \
            "//div[@class='widget-full-list-text left relative']//a/@href"
        review_urls = self.extract_list(response.xpath(review_url_xpath_1))
        additional_urls = self.extract_list(response.xpath(review_url_xpath_2))
        # review_urls.append(additional_urls)
        for url in review_urls:
            yield response.follow(url=url, callback=self.parse_review)
        for url in additional_urls:
            yield response.follow(url=url, callback=self.parse_review)

        pages = self.extract_list(response.xpath(
            "//div[@class='pagination']//a/@href"))
        for page in pages:
            yield response.follow(url=page, callback=self.parse)

    def parse_review(self, response):
        product_xpaths = {
            'PicURL': '//meta[@property="og:image"]/@content',
            'OriginalCategoryName': '(//span[@itemprop="name"])[4]//text()'
        }

        review_xpaths = {
            'TestSummary': '//meta[@property="og:description"]/@content',
            'TestDateText': '//meta[@property="og:updated_time"]/@content',
            'TestTitle': '//meta[@property="og:title"]/@content',
            'Author': '(//span[@itemprop="name"])[1]//text()'
            }

        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        # incremental
        ori_date = review['TestDateText']
        date_str = date_format(ori_date, '%Y-%m-%d')
        date_time = datetime.strptime(date_str, '%Y-%m-%d')
        if date_time < self.stored_last_date:
            return
        review['TestDateText'] = date_str
        # product name
        product['ProductName'] = review['TestTitle'].split('Review')[0]
        review['ProductName'] = product['ProductName']
        # sid
        _string = self.extract(response.xpath(
            '//body[@itemtype="https://schema.org/WebPage"]/@class'))
        source_internal_id = re.findall(r'postid-(\d+)', _string)[0]
        product['source_internal_id'] = source_internal_id
        review['source_internal_id'] = source_internal_id

        review['DBaseCategoryName'] = 'pro'

        yield product
        yield review
