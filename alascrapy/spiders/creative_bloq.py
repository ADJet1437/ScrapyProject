# -*- coding: utf8 -*-
import re
from datetime import datetime
from scrapy import Request

from alascrapy.items import ProductItem, ReviewItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import date_format, get_full_url
import alascrapy.lib.dao.incremental_scraping as incremental_utils

class CreativeBloqSpider(AlaSpider):
    name = 'creative_bloq'
    allowed_domains = ['creativebloq.com']
    start_urls = ['https://www.creativebloq.com/reviews']

    def __init__(self, *args, **kwargs):
        super(CreativeBloqSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

    def parse(self, response):

        contents = response.xpath("//div[@class='listingResults all']")
        for content in contents:
            urls_xpath = "./div/a/@href"
            urls = (content.xpath(urls_xpath)).extract()
            for url in urls:
                yield Request(url=url, callback=self.parse_items)
        
    def parse_items(self, response):

        review_xpaths = {
            "TestTitle": "//h1/text()",
            "TestVerdict": "//p[@class='game-verdict']/text()",
            "TestPros": "//div[@class='sub-box'][1]/ul/li/text()",
            "TestCons": "//div[@class='sub-box'][2]/ul/li/text()",
            "TestSummary": "//meta[@name='description']/@content"
        }
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        product = ProductItem()
        
        internal_source_id = str(response.url).split("/")[4]
        review['source_internal_id'] = internal_source_id
        product['source_internal_id'] = internal_source_id

        product_name = self.extract(response.xpath('//h1[@itemprop="name headline"]//text()')).encode('utf-8')
        review['ProductName'] = str(product_name).strip('review')
        product['ProductName'] = str(product_name).strip('review')

        source_test_rating = self.extract(response.xpath(
            "//span[@class='score no-graphic score-short']/text()"))
        if source_test_rating:
            review['SourceTestRating'] = source_test_rating
            review['SourceTestScale'] = '10'

        product['TestUrl'] = response.url

        date_str = self.extract(response.xpath("//time/@datetime"))
        if date_str:
            date_str = str(date_str).split("T")[0]
            date_time = date_format(date_str, "%Y-%m-%d")
            date_time_to_compare = datetime.strptime(date_time, '%Y-%m-%d')
            if self.stored_last_date > date_time_to_compare:
                return
        
        review['TestDateText'] = date_time
        review['DBaseCategoryName'] = 'PRO'
        
        picture_src = self.extract(response.xpath(
            "//img[@class='TODO image-class block-image-ads']/@src"))
        picture_url = get_full_url(response.url, picture_src)
        product['PicURL'] = picture_url

        cat = self.extract(response.xpath("//a[@class='chunk category']/text()"))
        if cat == 'Review':
            yield review
            yield product
        elif cat == 'Hardware':
            yield review
            yield product