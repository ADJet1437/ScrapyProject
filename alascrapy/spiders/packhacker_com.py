# -*- coding: utf8 -*-

import re
from datetime import datetime
from scrapy import Request

from alascrapy.items import ProductItem, ReviewItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import date_format
import alascrapy.lib.dao.incremental_scraping as incremental_utils


class PackhackerSpider(AlaSpider):
    name = 'packhacker_com'
    allowed_domains = ['packhacker.com']
    start_urls = ['https://packhacker.com/travel-gear/category/bags-and-luggage/']

    def __init__(self, *args, **kwargs):
        super(PackhackerSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        #if not self.stored_last_date:
        self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):

        for product_url in response.xpath(
                "//article/a/@href").extract():
            yield Request(url=product_url, callback=self.parse_review)

        next_page_xpath = "//nav/ul[@class='pagination']/li/a[@class='next page-link']/@href"
        next_page = self.extract(response.xpath(next_page_xpath))

        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_review(self, response):

        date_str = self.extract(response.xpath("//meta[@property='article:published_time']/@content"))
        review_date = datetime.strptime(date_str, "%Y-%m-%d")
        if self.stored_last_date > review_date:
            return

        review_xpaths = {
            "Author": "//div[@class='author-name']//span/text()",
            "TestSummary": "//meta[@name='description']/@content"
        }
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        product = ProductItem()
        
        title = self.extract(response.xpath("//h1[@class='entry-title']/text()"))
        if not title:
            title = str((self.extract(response.xpath("//meta[@property='og:title']/@content")))).encode('utf-8').replace(" | Pack Hacker", "")
        review['TestTitle'] = title
        
        if not review['TestSummary']:
            review['TestSummary'] = self.extract(response.xpath("//div[@class='card-body card-body-wysiwyg']/ul/li/text()"))

        test_url = response.url
        internal_source_id = str(test_url).split('/')[5].rstrip('/')
        review['source_internal_id'] = internal_source_id
        product['source_internal_id'] = internal_source_id
        # product name
        product_name = title.replace(" Review", "").replace(" review", "")

        review['ProductName'] = product_name
        product['ProductName'] = product_name

        source_test_rating = self.extract(response.xpath(
            "//div[@class='rating-value']/text()"))
        if source_test_rating:
            review['SourceTestRating'] = source_test_rating
            review['SourceTestScale'] = '10'
        review['TestUrl'] = test_url
    
        review['TestDateText'] = date_str
        review['DBaseCategoryName'] = 'PRO'

        product['TestUrl'] = test_url
        product['OriginalCategoryName'] = self.extract(response.xpath("//div[@class='breadcrumbs']//span[3]//text()"))
        product['PicURL'] = self.extract(response.xpath('//meta[@property="og:image"]/@content'))
        yield review
        yield product