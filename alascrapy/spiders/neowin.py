# -*- coding: utf8 -*-
import re
from datetime import datetime

from scrapy import Selector
from scrapy.http import Request

from alascrapy.lib.selenium_browser import SeleniumBrowser
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url
import alascrapy.lib.dao.incremental_scraping as incremental_utils


class NeowinSpider(AlaSpider):
    name = 'neowin'
    allowed_domains = ['neowin.net']
    start_urls = ['http://www.neowin.net/news/tags/review']

    def __init__(self, *args, **kwargs):
        super(NeowinSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(self.mysql_manager, self.spider_conf["source_id"])
        self.reviews_in_page = 0


    def stop_scraping(self, response):
        review_date_xpath = "//div[@id='news-content']//time[@class='date published']/@datetime"
        review_dates = self.extract_list(response.xpath(review_date_xpath))
        
        last_review_date = review_dates[-1]
        last_review_date = datetime.strptime(last_review_date[0:-6], "%Y-%m-%dT%H:%M:%S")

        if self.reviews_in_page == len(review_dates):
            stop_scraping = True
        else:
            stop_scraping = False

        if self.stored_last_date:
            if self.stored_last_date > last_review_date:
                stop_scraping = True

        self.reviews_in_page = len(review_dates)
        return stop_scraping

    def parse(self, response):
        selector = Selector(response)
        next_page_xpath = "//*[@class='more-button']"

        with SeleniumBrowser(self, response) as browser:
            browser.get(response.url)
            while not self.stop_scraping(selector):
                selector = browser.click(next_page_xpath)

        review_urls = self.extract_list(
            selector.xpath('//h3[@class="news-item-title"]/a/@href'))

        for review_url in review_urls:
            review_url = get_full_url(response, review_url)
            request = Request(review_url, callback=self.parse_review)
            yield request

    def parse_review(self, response):
        product_xpaths = { "ProductName": "//*[@itemprop='itemReviewed']//*[@itemprop='name']/@content",
                           "PicURL": "//*[@property='og:image']/@content"
                         }

        review_xpaths = { "TestTitle": "//*[@property='og:title']/@content",
                          "TestSummary": "//*[@property='og:description']/@content",
                          "Author": "//*[@rel='author']/text()",
                          "TestDateText": "//*[@class='article-meta']//time[@class='date published']/text()",
                          "SourceTestRating": "//*[@itemprop='ratingValue']/@content",
                          "TestVerdict": "(//*[@itemprop='articleBody']//*[contains(text(),'Conclusion')]/following-sibling::p[1])//text()"
                        }        


        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        review["DBaseCategoryName"] = "PRO"

        if not product["ProductName"]:
            product_name_re = "([\w\s\(\)]+)\sReview"
            name_match = re.search(product_name_re, review["TestTitle"])
            if name_match:
                product["ProductName"] = name_match.group(1)
            else:
                product["ProductName"] = review["TestTitle"]
        
        review["ProductName"] = product["ProductName"]

        if not review["TestVerdict"]:
            alt_verdict_xpat="(//*[@itemprop='articleBody']//h3/*[contains(text(),'Conclusion')])/../following-sibling::p[1]//text()"
            review["TestVerdict"] = self.extract_all(response.xpath(alt_verdict_xpat))

        if not review["TestVerdict"]:
            alt_verdict_xpat="(//*[@itemprop='articleBody']//*[contains(text(),'Final thoughts')]/following-sibling::p[1])//text()"
            review["TestVerdict"] = self.extract_all(response.xpath(alt_verdict_xpat))

        if not review["TestVerdict"]:
            alt_verdict_xpat="(//*[@itemprop='articleBody']//*[contains(text(),'Final Words')]/following-sibling::p[1])//text()"
            review["TestVerdict"] = self.extract_all(response.xpath(alt_verdict_xpat))

        if review["TestDateText"]:
            review["TestDateText"] = datetime.strptime(review["TestDateText"], 
                "%b %d, %Y").strftime('%Y-%m-%d')

        yield product
        yield review