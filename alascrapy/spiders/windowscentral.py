# -*- coding: utf8 -*-

from datetime import datetime

from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url
import alascrapy.lib.dao.incremental_scraping as incremental_utils


class WindowsCentralSpider(AlaSpider):
    name = 'windowscentral'
    allowed_domains = ['windowscentral.com']
    start_urls = ['http://www.windowscentral.com/reviews']

    def __init__(self, *args, **kwargs):
        super(WindowsCentralSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(self.mysql_manager, self.spider_conf["source_id"])

    def parse(self, response):
        next_page_xpath = "//*[@class='pager-next']/a/@href"
        review_selectors = response.xpath("//*[@class='node-title']/h2")
        review_url_xpath = "./a/@href"
        review_title_xpath = "./a/text()"

        for review_selector in review_selectors:
            title = self.extract_all(review_selector.xpath(review_title_xpath))
            if 'review' in title.lower(): 
                review_url = self.extract_all(review_selector.xpath(review_url_xpath))
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

        review_date_xpath = "//*[@class='node-title']//time[@class='published']/@datetime"
        review_dates = self.extract_list(response.xpath(review_date_xpath))
        last_review_date = review_dates[-1]

        last_review_date = datetime.strptime(last_review_date[0:-6], "%Y-%m-%dT%H:%M:%S")
        if self.stored_last_date > last_review_date:
            return False
        else:
            return True

    def parse_review(self, response):
        product_xpaths = { "PicURL": "(//*[@property='og:image'])[1]/@content",
                           "OriginalCategoryName": "(//*[@class='cats']/li)[1]/a[contains(@href, '/category/')]/text()"
                         }

        review_xpaths = { "TestTitle": "//*[@property='og:title']/@content",
                          "TestSummary": "//*[@property='og:description']/@content",
                          "Author": "//p[@class='meta-data']/a[contains(@class,'author')]/text()",
                          "TestDateText": "//*[@property='article:published_time']/@content",
                          "TestVerdict": "(//*[contains(@class,'entry-content')]"
                                         "//*[contains(text(),'Overall Impression')"
                                         "]/following-sibling::p[1])//text()"
                        }

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        product["ProductName"] = review["TestTitle"]
    
        review["DBaseCategoryName"] = "PRO"    
        review["ProductName"] = product["ProductName"]
        review["TestDateText"] = datetime.strptime(review["TestDateText"][0:-6], 
            "%Y-%m-%dT%H:%M:%S").strftime('%Y-%m-%d %H:%M:%S')

        yield product
        yield review
