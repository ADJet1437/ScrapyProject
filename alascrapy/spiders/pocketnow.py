# -*- coding: utf8 -*-

from datetime import datetime
import re

from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.selenium_browser import SeleniumBrowser
import alascrapy.lib.dao.incremental_scraping as incremental_utils


class PocketNowSpider(AlaSpider):
    name = 'pocketnow'
    allowed_domains = ['pocketnow.com']
    start_urls = ['http://pocketnow.com/reviews']

    def __init__(self, *args, **kwargs):
        super(PocketNowSpider, self).__init__(self, *args, **kwargs)
        self.get_date_re = re.compile("pocketnow.com/(\d{4}/\d{2}/\d{2})/")
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(self.mysql_manager, self.spider_conf["source_id"])


    def continue_to_next_page(self, last_review_url):
        if not self.stored_last_date:
            return True

        match = re.search(self.get_date_re, last_review_url)
        if match:
            last_date_string = match.group(1)
            last_review_date = datetime.strptime(last_date_string, "%Y/%m/%d")
            if self.stored_last_date > last_review_date:
                return False
            else:
                return True
        else:
            raise Exception("Cannot get date from URL: %s.\n Likely the website url format has changed" % last_review_url)

    def _parse(self, response, browser):
        next_page_xpath = "//*[@class='btn_next']"
        review_urls = self.extract_list(
            response.xpath('//*[@class="btn_read"]/@href'))

        for review_url in review_urls:
            request = Request(review_url, callback=self.parse_review)
            yield request

        if self.continue_to_next_page(review_urls[-1]):
            next_page = browser.click(next_page_xpath)
            for request in self.parse(next_page):
                request.meta['browser'] = browser
                yield request

    def parse(self, response):
        if 'browser' in response.meta:
            browser = response.meta['browser']
            for request in self._parse(response, browser):
                yield request
        else:
            with SeleniumBrowser(self, response) as browser:
                for request in self._parse(response, browser):
                    yield request


    def parse_review(self, response):
        product_xpaths = { "ProductName": "//*[@class='per_title']/text()",
                           "PicURL": "//*[@property='og:image']/@content",
                           "OriginalCategoryName": "//*[@property='article:section']/@content"
                         }

        review_xpaths = { "ProductName": "//*[@class='per_title']/text()",
                          "TestTitle": "//*[@class='per_title']/text()",
                          "TestSummary": "//*[@property='og:description']/@content",
                          "Author": "//*[@itemprop='author']//text()",
                          "TestDateText": "//meta[@name='pubdate']/@content",
                          "SourceTestRating": "//*[@itemprop='ratingValue']/@content",
                          "TestVerdict": "(//h2[contains(text(),'Conclusion')]/following-sibling::p[text()!='Index'])//text()"
                        }        

        pros_xpath = "(//h2[contains(text(),'Pros')]/following-sibling::*)[1]//text()"
        cons_xpath = "(//h2[contains(text(),'Cons')]/following-sibling::*)[1]//text()"

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        review["TestPros"] = self.extract_all(response.xpath(pros_xpath), separator=" ; ", strip_chars="+")
        review["TestPros"] = re.sub("\+\s+", "", review["TestPros"])
        review["TestCons"] = self.extract_all(response.xpath(cons_xpath), separator=" ; ", strip_chars="-")
        review["TestCons"] = re.sub("-\s+", "", review["TestCons"])

        if "(video)" in review["TestTitle"].lower():
            review["DBaseCategoryName"] = "VPRO"
        else:
            review["DBaseCategoryName"] = "PRO"

        review["TestDateText"] = datetime.strptime(review["TestDateText"], 
            "%Y%m%d").strftime('%Y-%m-%d')

        yield product
        yield review