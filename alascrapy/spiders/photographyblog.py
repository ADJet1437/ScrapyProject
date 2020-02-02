# -*- coding: utf8 -*-

from datetime import datetime
import dateparser
from scrapy.http import Request
import json
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.items import ProductItem, ReviewItem
import alascrapy.lib.dao.incremental_scraping as incremental_utils

TEST_SCALE = 5

class PhotographyBlogSpider(AlaSpider):
    name = 'photographyblog'
    allowed_domains = ['photographyblog.com']
    start_urls = ['http://www.photographyblog.com/reviews/',
                  'http://www.photographyblog.com/reviews/#lenses',
                  'http://www.photographyblog.com/reviews/#printers',
                  'http://www.photographyblog.com/reviews/#accessories',
                  'http://www.photographyblog.com/reviews/#other']

    def __init__(self, *args, **kwargs):
        super(PhotographyBlogSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):

        review_divs_xpath = "//div[@id='review-item-wrap']"
        review_divs = response.xpath(review_divs_xpath)

        for review_div in review_divs:
            date_xpath = "./div//div[@class='review-item-date']/text()"
            dates = (review_div.xpath(date_xpath)).getall()
            for date in dates:
                review_date = dateparser.parse(date)
                if review_date > self.stored_last_date:
                    review_urls_xpath = "./div/a/@href"
                    review_urls = (review_div.xpath(review_urls_xpath)).getall()
                    for review_url in review_urls:
                        yield response.follow(url=review_url,
                                  callback=self.parse_review)

    def parse_review(self, response):

        product_xpaths = {
            'ProductName': "substring-before(//meta[@property='og:title']"
            "/@content,'Review')",
            'PicURL': '//meta[@property="og:image"]/@content'
        }

        product = self.init_item_by_xpaths(response, 'product', product_xpaths)
        product['source_internal_id'] = str(response.url).split('/')[4]

        review_xpaths = {
            'ProductName': "substring-before(//meta[@property='og:title']"
            "/@content,'Review')",
            'TestTitle': "substring-before(//meta[@property='og:title']"
            "/@content,'|')",
            'Author': '//span[@class="reviewer"]/text()',
            "SourceTestRating": '//span[@class="value-title"]/@title',
            "TestSummary": '//meta[@property="og:description"]/@content'
        }

        review = self.init_item_by_xpaths(response, 'review', review_xpaths)

        if review["SourceTestRating"]:
            review["SourceTestScale"] = TEST_SCALE

        date_xpath = "//span[@class='dtreviewed']/text()"
        date = self.extract(response.xpath(date_xpath))
        if date:
            test_date = datetime.strptime(date, '%B %d, %Y')
            test_date = test_date.strftime('%Y-%m-%d')
            review["TestDateText"] = test_date

        review['DBaseCategoryName'] = 'PRO'
        if not review['TestSummary']: 
            review['TestSummary'] = self.extract(response.xpath("//div[@class='content-inner KonaBody']/p[2]/text()"))

        review['source_internal_id'] = str(response.url).split('/')[4]

        date_time = datetime.strptime(test_date, '%Y-%m-%d')
        if date_time > self.stored_last_date: 
            yield review
            yield product