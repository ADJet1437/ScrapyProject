# -*- coding: utf8 -*-

import re
from datetime import datetime

from urllib import unquote
from scrapy import Request

from alascrapy.items import ProductItem, ReviewItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import date_format
import alascrapy.lib.dao.incremental_scraping as incremental_utils


class CarryologySpider(AlaSpider):
    name = 'carryology_com'
    allowed_domains = ['carryology.com']
    start_urls = ['https://www.carryology.com/category/luggage/']

    def __init__(self, *args, **kwargs):
        super(CarryologySpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):

        review_divs_xpath = "//div[@id='main']/ul"
        review_divs = response.xpath(review_divs_xpath)

        for review_div in review_divs:
            date_xpath = './li//div[@class="meta"]/text()[2]'
            dates = (review_div.xpath(date_xpath)).getall()
            for date in dates:
                
                r_date = str(date).lstrip(", ")
                review_date = datetime.strptime(r_date, '%B %d, %Y')
                if review_date > self.stored_last_date:
                    review_urls_xpath = "./li/div/a/@href"
                    review_urls = (review_div.xpath(review_urls_xpath)).getall()
                    for review in review_urls:
                        yield Request(review, callback=self.parse_review)

        last_page=29
        for i in range(2, last_page+1):
            next_page_url = 'https://www.carryology.com/category/luggage/page/'+str(i)
            if next_page_url:
                last_date = self.extract(response.xpath('(//div[@id="main"]/ul/li//div[@class="meta"]/text()[2])[last()]'))
                r_date = str(last_date).lstrip(", ")
                review_date = datetime.strptime(r_date, '%B %d, %Y')
                if review_date > self.stored_last_date:
                    yield Request(next_page_url, callback=self.parse)

    def parse_review(self, response):

        review_xpaths = {
            "TestTitle": "//meta[@property='og:title']/@content",
            "Author": "//div[@class='meta']/a/text()",
            "TestSummary": "//meta[@name='description']/@content"
        }
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        product = ProductItem()
        if not review['TestSummary']:
            review['TestSummary'] = self.extract(response.xpath("//meta[@property='og:description']/@content"))

        test_url = response.url
        internal_source_id = str(test_url).split('/')[4].rstrip('/')
        review['source_internal_id'] = internal_source_id
        product['source_internal_id'] = internal_source_id
        # product name
        title = (review['TestTitle']).encode('utf-8')
        if 'review' in title:
            product_name = title.replace(" review", "")
        elif 'Review' in title:
            product_name = title.replace(" Review", "")
        elif 'Video' in title:
            product_name = title.replace(" Video", "").split(":")[0]
        elif ':' in title:
            product_name = str(title).split(":")[0]
        else:
            product_name = title

        product_name = product_name.replace(" - Carryology - Exploring better ways to carry", "").replace(" Video", "").replace("Drive By", "").replace(":", "").replace(" |", "").replace(" Carryology", "")

        review['ProductName'] = product_name
        product['ProductName'] = product_name

        source_test_rating = self.extract(response.xpath(
            "//div[@class='bar']/span[@class='score']/text()"))
        if source_test_rating:
            review['SourceTestRating'] = source_test_rating
            review['SourceTestScale'] = '10'
        review['TestUrl'] = test_url
    
        date_str = self.extract(response.xpath("//div[@class='meta']/text()[2]"))
        date = str(date_str).lstrip(", ")
        date_time = date_format(date, "%B %d, %Y")
        review['TestDateText'] = date_time
        review['DBaseCategoryName'] = 'PRO'

        product['TestUrl'] = test_url
        product['OriginalCategoryName'] = self.extract(response.xpath("//div[@class='breadcrumbs']//span/text()"))
        product['PicURL'] = self.extract(response.xpath('//meta[@property="og:image"]/@content'))
        yield review
        yield product