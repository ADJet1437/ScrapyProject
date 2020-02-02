# -*- coding: utf8 -*-
__author__ = 'leonardo'

import re

from alascrapy.lib.selenium_browser import SeleniumBrowser
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import date_format, get_full_url
from alascrapy.items import ProductItem, ReviewItem

class LinuxTvSpider(AlaSpider):
    name = 'linux-tv'
    allowed_domains = ['linux-tv.com']
    start_urls = ['http://linux-tv.com/receiver-reviews/']

    def parse(self, response):
        with SeleniumBrowser(self, response) as browser:
            for item in self.parse_links(browser, response.url):
                yield item

    def parse_links(self, browser, url):
        selector = browser.get(url)
        review_list_xpath = "//div[@class='post-panel']//h2/a/@href"
        next_page_xpath = "(//div[@class='pagination']/*[" \
                          "@class='current']/following-sibling::a)[1]/@href"
        review_links = self.extract_list(selector.xpath(review_list_xpath))

        for review_url in review_links:
            review_url = get_full_url(url, review_url)
            review_selector = browser.get(review_url)
            for item in self.parse_review(review_selector, review_url):
                yield item

        next_page_url = self.extract(selector.xpath(next_page_xpath))
        if next_page_url:
            next_page_url = get_full_url(url, next_page_url)
            for item in self.parse_links(browser, next_page_url):
                yield item

    def parse_review(self, selector, url):
        image_xpath = "//img[@itemprop='image']/@src"
        image_alt_xpath = "//meta[@property='og:image']/@content"
        manufacturer_xpath = "(//span[@class='taxName' and text()='Manufacturer']/following-sibling::span[@class='taxContent'])[1]//text()"

        title_xpath = "//span[@itemprop='itemReviewed']/text()"
        summary_xpath = "//*[@itemprop='description']//text()"
        summary_alt_xpath = "//meta[@property='og:description']/@content"
        author_xpath = "//span[@itemprop='author']//text()"
        date_xpath = "//meta[@itemprop='datePublished']/@content"
        pros_xpath = "//div[@class='positive-wrapper']/text()"
        cons_xpath = "//div[@class='negative-wrapper']/text()"
        rating_value_xpath = "//*[@itemprop='ratingValue']/text()"
        rating_scale_xpath = "//*[@itemprop='bestRating']/text()"

        review = ReviewItem()
        review["TestTitle"] = self.extract_all(selector.xpath(title_xpath))
        review["TestSummary"] = self.extract_all(selector.xpath(summary_xpath))
        review["Author"] = self.extract(selector.xpath(author_xpath))
        review["TestDateText"] = self.extract(selector.xpath(date_xpath))
        review["TestPros"] = self.extract_all(selector.xpath(pros_xpath), ' ; ')
        review["TestCons"] = self.extract_all(selector.xpath(cons_xpath), ' ; ')
        review["SourceTestRating"] = self.extract(selector.xpath(rating_value_xpath))
        review["SourceTestScale"] = self.extract(selector.xpath(rating_scale_xpath))
        review["DBaseCategoryName"] = "PRO"
        review["TestUrl"] = url
        review["TestDateText"] = date_format(review["TestDateText"], "%b %d,%Y")

        product = ProductItem()
        product_name_re = "(.+)\sReview"
        name_match = re.search(product_name_re, review["TestTitle"], re.IGNORECASE)
        if name_match:
            product["ProductName"] = name_match.group(1)
        else:
            product["ProductName"] = review["TestTitle"]

        review["ProductName"] = product["ProductName"]

        product["TestUrl"] = url
        product["PicURL"] = self.extract(selector.xpath(image_xpath))
        product["ProductManufacturer"] = self.extract(selector.xpath(manufacturer_xpath))
        if not product["PicURL"]:
            product["PicURL"] = self.extract(selector.xpath(image_alt_xpath))

        if not review["TestSummary"]:
            review["TestSummary"] = self.extract(selector.xpath(summary_alt_xpath))

        yield product
        yield review