#!/usr/bin/env python

"""mobileburn Spider: """

__author__ = 'graeme'

import re

from scrapy import Selector
from scrapy.http import Request

from alascrapy.items import ProductItem, ReviewItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider


class MobileBurnSpider(AlaSpider):
    name = 'mobileburn'
    allowed_domains = ['mobileburn.com']
    start_urls = ['http://www.mobileburn.com/cell_phone_archive.jsp?Types=1&Classes=2&Label=Smartphone_Reviews']

    def parse(self, response):

        for review_text in response.xpath('//div[@class="storysub"]').extract():
            review_section = Selector(text=review_text)
            product = ProductItem()
            review = ReviewItem()

            product['OriginalCategoryName'] = "Cell Phones"
            review['DBaseCategoryName'] = "PRO"

            review['TestTitle'] = self.extract(review_section.xpath('//a[2]/text()'))

            review['TestUrl'] = "http://www.mobileburn.com" + self.extract(review_section.xpath('//a[2]/@href'))
            product['TestUrl'] = review['TestUrl']

            if review['TestTitle']:
                matches = re.search("^(.*?) review", review['TestTitle'], re.IGNORECASE)
                if matches:
                    review['ProductName'] = matches.group(1)
                    product['ProductName'] = matches.group(1)
                else:
                    review['ProductName'] = review['TestTitle']
                    product['ProductName'] = review['TestTitle']

            author_and_date = self.extract(review_section.xpath('//span'))
            if author_and_date:
                matches = re.search("^By (.*?) on \w+ (.+)", author_and_date, re.IGNORECASE)
                if matches:
                    review['Author'] = matches.group(1)
                    review["TestDateText"] = matches.group(2)

            review['TestSummary'] = self.extract_all(review_section.xpath('//p/text()'), separator=" ")

            product['PicURL'] = "http://www.mobileburn.com/" + self.extract(review_section.xpath('//a/img/@src'))

            yield product
            yield review

        next_url = self.extract(response.xpath('//a[@id="next"]/@href'))
        if next_url:
            next_url = "http://www.mobileburn.com/" + next_url
            list_req = Request(next_url, callback=self.parse)
            yield list_req