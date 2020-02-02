#!/usr/bin/env python

"""fonearena Spider: """

__author__ = 'graeme'

import re

from scrapy.spiders import Rule
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor

from alascrapy.items import ProductItem, ReviewItem
from alascrapy.spiders.base_spiders.ala_crawl import AlaCrawlSpider
from alascrapy.lib.generic import date_format


class FoneArenaSpider(AlaCrawlSpider):
    name = 'fonearena'
    allowed_domains = ['fonearena.com']
    start_urls = ['http://www.fonearena.com/reviews.php']

    rules = [Rule(LxmlLinkExtractor(restrict_xpaths='//figure[@class="effect3"]/a',
                                    unique=True),
                  callback="parse_review"),
             Rule(LxmlLinkExtractor(restrict_xpaths='//a[@title="next page"]',
                                    unique=True))
             ]

    def parse_review(self, response):

        if not response.url.endswith(".php"):
            product = ProductItem()
            review = ReviewItem()

            review['TestTitle'] = self.extract(response.xpath('//h2/text()'))

            if review['TestTitle']:
                matches = re.search("^(.*?) review", review['TestTitle'], re.IGNORECASE)
                if matches:
                    review['ProductName'] = matches.group(1)
                    product['ProductName'] = matches.group(1)
                else:
                    review['ProductName'] = review['TestTitle']
                    product['ProductName'] = review['TestTitle']

            review['Author'] = self.extract(response.xpath('//a[@rel="author"]/text()'))

            date_span = self.extract(response.xpath('//span[@class="updated"]/text()'))
            if date_span:
                matches = re.search(r'(\S+ \d+, \d+) ', date_span)
                if matches:
                    date_span = matches.group(1)
                    review['TestDateText'] = date_format(date_span, '%B %d, %Y')

            product['PicURL'] = self.extract(response.xpath('//div[contains(@class,"entry")]/p//img/@src'))

            review['TestSummary'] = self.extract_all(response.xpath('//div[contains(@class,"entry")]/p[1]//text()'), separator=" ")
            if not review['TestSummary']:
                review['TestSummary'] = self.extract_all(response.xpath('//div[contains(@class,"entry")]/p[2]//text()'), separator=" ")

            review['TestVerdict'] = self.extract_all(response.xpath('//div[contains(@class,"entry")]/p[strong[contains(text(),"Conclusion")]]/following-sibling::p/text()'), separator=" ")
            if not review['TestVerdict']:
                review['TestVerdict'] = self.extract_all(response.xpath('//div[contains(@class,"entry")]/h2[contains(text(),"Conclusion")]/following-sibling::p/text()'), separator=" ")

            review['TestPros'] = self.extract_all(response.xpath('//div[contains(@class,"entry")]/p[strong[contains(text(),"Pros")]]/following-sibling::*[1]/li/text()'), separator="; ")
            if not review['TestPros']:
                review['TestPros'] = self.extract_all(response.xpath('//div[contains(@class,"entry")]/h3[contains(text(),"Pros")]/following-sibling::*[1]/li/text()'), separator="; ")

            review['TestCons'] = self.extract_all(response.xpath('//div[contains(@class,"entry")]/p[strong[contains(text(),"Cons")]]/following-sibling::*[1]/li/text()'), separator="; ")
            if not review['TestCons']:
                review['TestCons'] = self.extract_all(response.xpath('//div[contains(@class,"entry")]/h3[contains(text(),"Cons")]/following-sibling::*[1]/li/text()'), separator="; ")

            product['OriginalCategoryName'] = "Miscellaneous"
            review['DBaseCategoryName'] = "PRO"

            product['TestUrl'] = response.url
            review['TestUrl'] = response.url

            yield product
            yield review
