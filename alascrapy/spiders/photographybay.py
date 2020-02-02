# -*- coding: utf8 -*-

from datetime import datetime
import re

from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url
import alascrapy.lib.dao.incremental_scraping as incremental_utils


class PhotographyBaySpider(AlaSpider):
    name = 'photographybay'
    allowed_domains = ['photographybay.com']
    start_urls = ['http://www.photographybay.com/tag/review']

    def __init__(self, *args, **kwargs):
        super(PhotographyBaySpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(self.mysql_manager, self.spider_conf["source_id"])

    def parse(self, response):
        next_page_xpath = "//*[@class='pagination-next']/a/@href"
        review_urls = self.extract_list(
            response.xpath("//*[@class='entry-title']/a/@href"))

        for review_url in review_urls:
            review_url = get_full_url(response, review_url)
            request = Request(review_url, callback=self.parse_review)
            yield request

        if self.continue_to_next_page(response):
            next_page = self.extract(response.xpath(next_page_xpath))
            next_page = get_full_url(response, next_page)
            request = Request(next_page, callback=self.parse)
            yield request

    def continue_to_next_page(self, response):
        if not self.stored_last_date:
            return True

        review_date_xpath = "//*[@itemprop='datePublished']/@datetime"
        review_dates = self.extract_list(response.xpath(review_date_xpath))
        last_review_date = review_dates[-1]

        last_review_date = datetime.strptime(last_review_date[0:-6], "%Y-%m-%dT%H:%M:%S")
        if self.stored_last_date > last_review_date:
            return False
        else:
            return True

    def parse_review(self, response):
        product_xpaths = { "PicURL": "(//*[@property='og:image'])[1]/@content"
                         }

        review_xpaths = { "TestTitle": "//*[@property='og:title']/@content",
                          "TestSummary": "//*[@property='og:description']/@content",
                          "Author": "//*[@class='entry-author-name']/text()",
                          "TestDateText": "//*[@itemprop='datePublished']/@datetime"
                        }

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        review["DBaseCategoryName"] = "PRO"

        product_name_re = "([\w\s\(\)]+)\sReview"

        name_match = re.search(product_name_re, review["TestTitle"])
        if name_match:
            product["ProductName"] = name_match.group(1)
        else:
            product["ProductName"] = review["TestTitle"]
        
        review["ProductName"] = product["ProductName"]

        review["TestDateText"] = datetime.strptime(review["TestDateText"][0:-6], 
            "%Y-%m-%dT%H:%M:%S").strftime('%Y-%m-%d %H:%M:%S')

        yield product
        yield review

