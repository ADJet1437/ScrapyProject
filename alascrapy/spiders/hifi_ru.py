# -*- coding: utf8 -*-
from datetime import datetime
import dateparser
import re
from scrapy import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import date_format, get_full_url
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem

class Hifi_ruSpider(AlaSpider):
    name = 'hifi_ru'
    allowed_domains = ['hi-fi.ru']
    start_urls = ['https://www.hi-fi.ru/video/']

    def __init__(self, *args, **kwargs):
        super(Hifi_ruSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):

        review_urls_xpath = "//div[@class='content']/div[@class='reviews']/a[2]/@href"
        review_urls = (response.xpath(review_urls_xpath)).getall()
        for review_url in review_urls:
            review = get_full_url(response, review_url)
            yield Request(url=review, callback=self.parse_items)

        last_page=10
        for i in range(2, last_page+1):
            next_page_url = 'https://www.hi-fi.ru/video/scroll_razdel.php?PAGEN_1='+str(i)
            if next_page_url:
                yield Request(next_page_url, callback=self.parse)

    def parse_items(self, response):

        review_date = self.extract(response.xpath("//meta[@itemprop='datePublished']/@content"))
        reviewdate = datetime.strptime(review_date, "%Y-%m-%d")
        if self.stored_last_date > reviewdate:
            return

        product_xpaths = { "PicURL": "//meta[@property='og:image']/@content"
                         }

        review_xpaths = { "TestSummary": "//meta[@name='description']/@content",
                          "TestVerdict": "//div[@class='text']/div[2]/strong/text()",  
                          "TestTitle": "//meta[@property='og:title']/@content",
                          "Author": "//meta[@itemprop='author']/@content",
                          "TestPros": "//td[@class='minus'][1]/text()",
                          "TestCons": "//td[@class='minus'][2]/text()",
                          "SourceTestRating": "//div[@class='rating'][5]/p/text()"
                        }

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        productname = (response.url).split("/")[5].replace("-", " ")
        review['ProductName'] = productname
        product['ProductName'] = productname

        source_internal_id = (response.url).split("/")[5]
        review['source_internal_id'] = source_internal_id
        product['source_internal_id'] = source_internal_id

        if review['SourceTestRating']:
            review['SourceTestScale'] = "100"

        review["DBaseCategoryName"] = "PRO"

        review['TestDateText'] = review_date

        yield review
        yield product