# -*- coding: utf8 -*-

from datetime import datetime

from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url
import alascrapy.lib.dao.incremental_scraping as incremental_utils


class DigitalSpySpider(AlaSpider):
    name = 'digitalspy'
    allowed_domains = ['digitalspy.co.uk']
    start_urls = ['http://www.digitalspy.co.uk/tech/review/']

    def __init__(self, *args, **kwargs):
        super(DigitalSpySpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(self.mysql_manager, self.spider_conf["source_id"])

    def parse(self, response):
        next_page_xpath = "//*[contains(@class, 'pagination')]//a[@title='Next']/@href"
        review_urls = self.extract_list(
            response.xpath("//*[@class='content_area']//a[@class='component']/@href"))

        for review_url in review_urls:
            review_url = get_full_url(response, review_url)
            request = Request(review_url, callback=self.parse_review)
            yield request

        if self.continue_to_next_page(response):
            next_page = self.extract(response.xpath(next_page_xpath))
            if next_page:
                next_page = get_full_url(response, next_page)
                request = Request(next_page, callback=self.parse)
                yield request

    def continue_to_next_page(self, response):
        if not self.stored_last_date:
            return True

        review_date_xpath = "//*[@class='content_area']//time/@datetime"
        review_dates = self.extract_list(response.xpath(review_date_xpath))
        if review_dates:
            last_date_string = review_dates[-1]
            last_review_date = datetime.strptime(last_date_string[0:-4], "%Y-%m-%d:%H:%M")
            if self.stored_last_date > last_review_date:
                return False
        return True

    def parse_review(self, response):
        product_xpaths = { "ProductName": "(//*[@id='articleimage'])[1]//img/@alt",
                           "PicURL": "(//*[@property='og:image'])[1]/@content",
                           "OriginalCategoryName": "(//*[@class='category-chicklets']/li)[last()]//text()"
                         }

        review_xpaths = { "ProductName": "(//*[@id='articleimage'])[1]//img/@alt",
                          "TestTitle": "//*[@property='og:title']/@content",
                          "TestSummary": "//*[@property='og:description']/@content",
                          "Author": "//a[@rel='author']/text()",
                          "TestDateText": "//time/@datetime"
                        }

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        review["DBaseCategoryName"] = "PRO"
        review["TestDateText"] = datetime.strptime(review["TestDateText"][0:-4], 
            "%Y-%m-%d:%H:%M").strftime("%Y-%m-%d %H:%M:00")

        yield product
        yield review

