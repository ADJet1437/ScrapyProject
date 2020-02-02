# -*- coding: utf8 -*-
from datetime import datetime
import dateparser
from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import date_format
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ReviewItem, ProductItem

class AudiovisionDeSpider(AlaSpider):
    name = 'audiovision_de'
    allowed_domains = ['audiovision.de']
    start_urls = ['http://audiovision.de/category/tests/fernseher/',
                    'http://audiovision.de/category/tests/boxensets/',
                    'http://audiovision.de/category/tests/blurayplayer/',
                    'http://audiovision.de/category/tests/bluetooth-speaker/']

    def __init__(self, *args, **kwargs):
        super(AudiovisionDeSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):

        review_divs_xpath = "//div[@class='col-8 main-content']"
        review_divs = response.xpath(review_divs_xpath)
        for review_div in review_divs:
            date_xpath = ".//time[@class='meta-item']/@datetime"
            dates = (review_div.xpath(date_xpath)).getall()
            for date in dates:
                date = str(date).split("T")[0]
                review_date = datetime.strptime(date, '%Y-%m-%d')
                if review_date > self.stored_last_date:
                    review_urls_xpath = ".//div[@class='content']/a/@href"
                    review_urls = (review_div.xpath(review_urls_xpath)).getall()
                    for review_url in review_urls:
                        yield Request(url=review_url, callback=self.parse_items)

        next_page_xpath = "//a[@class='next page-numbers']/@href"
        next_page = self.extract(response.xpath(next_page_xpath))

        review_date_xpath = "(//div[@class='col-8 main-content']//time[@class='meta-item']/@datetime)[last()]"
        review_date = self.extract(response.xpath(review_date_xpath))
        date = str(review_date).split("T")[0]
        oldest_review_date = datetime.strptime(date, '%Y-%m-%d')

        if next_page:
            if oldest_review_date > self.stored_last_date:
                yield response.follow(next_page_url, callback=self.parse)


    def parse_items(self, response):

        product_xpaths = { "PicURL": "//meta[@property='og:image']/@content"
                         }

        review_xpaths = { "TestSummary": "//meta[@property='og:description']/@content",
                          "TestTitle": "//meta[@property='og:title']/@content",
                          "Author": "//span[@class='reviewer']/a/text()",
                          "TestDateText": "substring-before(//meta[@property='article:published_time']/@content,'T')",
                          "TestVerdict": "//div[@class='text summary']/p/text()"
                        }

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        productname = review['TestTitle'].split("(")[0]

        link = self.extract(response.xpath('//link[@rel="shortlink"]/@href'))
        source_int_id = str(link).split("=")[1]

        product['ProductName'] = productname
        product['source_internal_id'] = source_int_id

        rating = self.extract(response.xpath("//span[@class='value']/text()"))
        if rating.isdigit():
            review['SourceTestRating'] = rating
            review['SourceTestScale'] = '100'

        db_cat = 'PRO'
        review['ProductName'] = productname
        review['DBaseCategoryName'] = db_cat
        review['source_internal_id'] = source_int_id

        yield product
        yield review
