# -*- coding: utf8 -*-
import re
from datetime import datetime

from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format
import alascrapy.lib.dao.incremental_scraping as incremental_utils


class DdayITSpider(AlaSpider):
    name = 'dday_it'
    allowed_domains = ['dday.it']
    start_urls = ['http://www.dday.it/prove']
    source_internal_id_re = re.compile("/redazione/(\d+)/")

    def __init__(self, *args, **kwargs):
        super(DdayITSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(self.mysql_manager, self.spider_conf["source_id"])

    def parse(self, response):
        next_page_xpath = "//a[@rel='next']/@href"
        review_selectors = response.xpath("//section[@class='content']//article[@class='preview']")
        review_url_xpath = "./a/@href"

        for review_selector in review_selectors:
            review_url = self.extract_all(review_selector.xpath(review_url_xpath))
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

        review_date_xpath = "//span[@class='date']/text()"
        review_dates = self.extract_list(response.xpath(review_date_xpath))
        last_review_date = review_dates[-1]

        last_review_date = datetime.strptime(last_review_date, "%d/%m/%Y %H:%M")
        if self.stored_last_date > last_review_date:
            return False
        else:
            return True

    def parse_review(self, response):
        if not response.xpath("//section[contains(@class, 'review-page')]"):
            return

        product_xpaths = { "PicURL": "//img[@class='product-image']/@src",
                           "ProductName": "//section[@class='product-summary']//h3/text()",
                           "ProductManufacturer": "//span[@class='brand']/text()"
                         }

        review_xpaths = { "TestTitle": "//section[contains(@class, 'review-page')]//h1/text()",
                          "TestSummary": "//section[contains(@class, 'article-summary')]/h2/text()",
                          "Author": "//span[@class='author']/following-sibling::strong[1]//text()",
                          "TestDateText": "//span[@class='date']/text()",
                          #"TestVerdict": "(//section[@class='product-summary']/div[@class='col'])[2]/h4/text()",
                          "SourceTestRating": "//li[@class='total']/div[@class='score']/text()",
                          #"TestPros": "//section[@class='rating']//h2[text()='Cosa ci piace']/following-sibling::p/text()",
                          #"TestCons": "//section[@class='rating']//h2[text()='Cosa non ci piace']/following-sibling::p/text()"
                        }
        pic_url_alt_xpath = "//img[@class='cover-image']/@src"

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        if not review["TestSummary"]:
            return

        if not product["ProductName"]:
            product["ProductName"] = review["TestTitle"]
            review["ProductName"] = review["TestTitle"]

        if not product["PicURL"]:
            product["PicURL"] = self.extract(response.xpath(pic_url_alt_xpath))


        sii_match = re.search(self.source_internal_id_re, response.url)
        if sii_match:
            source_internal_id = sii_match.group(1)
            product["source_internal_id"] = source_internal_id
            review["source_internal_id"] = source_internal_id

        review["DBaseCategoryName"] = "PRO"
        if review["SourceTestRating"]:
            review["SourceTestScale"] = "10"
        review["ProductName"] = product["ProductName"]
        review["TestDateText"] = date_format(review["TestDateText"], "%d/%m/%Y %H:%M")

        yield product
        yield review
