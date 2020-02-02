# -*- coding: utf8 -*-

import re
from datetime import datetime

from scrapy.http import Request

import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url


class TechSpotSpider(AlaSpider):
    name = 'techspot'
    allowed_domains = ['techspot.com']
    start_urls = ['http://techspot.com/reviews']

    def __init__(self, *args, **kwargs):
        super(TechSpotSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(self.mysql_manager, self.spider_conf["source_id"])

    def parse(self, response):
        review_urls_xpaths = "//*[@id='review']//li//h3/a/@href"
        next_page_xpath = "//*[contains(@class, 'footerPagelist')]//a[@rel='next']/@href"

        review_urls = self.extract_list(
            response.xpath(review_urls_xpaths))

        for review_url in review_urls:
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

        review_date_xpath = "//*[@id='review']//li//time//text()"
        review_dates = self.extract_list(response.xpath(review_date_xpath))
        last_date_string = review_dates[-1]

        last_review_date = datetime.strptime(last_date_string, "%B %d, %Y")
        if self.stored_last_date > last_review_date:
            return False
        else:
            return True

    def parse_review(self, response):
        review_last_page_xpath = "(//*[@class='index-mobile']//li)[last()]/a/@href"

        category_xpaths = { "category_leaf": "(//*[@class='category-chicklets']/li)[last()]//text()",
                            "category_path": "(//*[@class='category-chicklets']/li)[last()]//text()"
                          }

        product_xpaths = { "PicURL": "(//*[@property='og:image'])[1]/@content",
                           "OriginalCategoryName": "(//*[@class='category-chicklets']/li)[last()]//text()"
                         }

        review_xpaths = { "TestTitle": "//*[@itemprop='name']/text()",
                          "TestSummary": "//*[@property='og:description']/@content",
                          "Author": "//*[@itemprop='author']//text()",
                          "TestDateText": "//time/@datetime",
                          "SourceTestRating": "//*[@itemprop='ratingValue']/text()"
                        }

        category = self.init_item_by_xpaths(response, "category", category_xpaths)
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        product_name_re = "([\w\s\(\)]+)\sReview"
        name_match = re.search(product_name_re, review["TestTitle"])
        if name_match:
            product["ProductName"] = name_match.group(1)
        else:
            product["ProductName"] = review["TestTitle"]
        
        review["ProductName"] = product["ProductName"]
        yield category
        yield product

        review["DBaseCategoryName"] = "PRO"
        review["TestDateText"] = review["TestDateText"][0:-5]
        review_last_page = self.extract(response.xpath(review_last_page_xpath))
        if review_last_page:
            request = Request(review_last_page, callback=self.parse_last_page)
            request.meta['review'] = review
            yield request
        else:
            yield review

    def parse_last_page(self, response):
        review = response.meta["review"]
        verdict_xpath = "(//*[@itemprop='articleBody']/p)[1]//text()"
        pros_xpath = "//*[@class='content_box']//span[contains(text(),'Pros:')]/parent::p/text()"
        cons_xpath = "//*[@class='content_box']//span[contains(text(),'Cons:')]/parent::p/text()"

        review["TestVerdict"] = self.extract(response.xpath(verdict_xpath))
        review["TestPros"] = self.extract(response.xpath(pros_xpath))
        review["TestCons"] = self.extract(response.xpath(cons_xpath))
        yield review

