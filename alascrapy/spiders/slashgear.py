#!/usr/bin/env python

"""slashgear Spider: """

__author__ = 'graeme, frank'

import re

from scrapy import Selector
from scrapy.spiders import Rule
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.http import Request

from alascrapy.items import ProductItem, ReviewItem
from alascrapy.spiders.base_spiders.ala_crawl import AlaCrawlSpider
from alascrapy.lib.generic import date_format

import alascrapy.lib.extruct_helper as extruct_helper


class SlashgearSpider(AlaCrawlSpider):
    name = 'slashgear'
    allowed_domains = ['slashgear.com']
    start_urls = ['http://www.slashgear.com/section/reviews/']

    rules = [Rule(LxmlLinkExtractor(restrict_xpaths='//a[text()="Next"]',
                                    unique=True),
                callback="parse_list_page")
             ]

    def parse_start_url(self, response):
        start_page_items = list(self.parse_list_page(response))
        for item in start_page_items:
            yield item

    def parse_list_page(self, response):

        for review_text in response.xpath('//div[@class="post"]').extract():
            review_section = Selector(text=review_text)
            product = ProductItem()
            review = ReviewItem()

            review['TestTitle'] = self.extract(review_section.xpath('//h2/a/text()'))
            if review['TestTitle']:
                matches = re.search("^(.*?) review", review['TestTitle'], re.IGNORECASE)
                if matches:
                    review['ProductName'] = matches.group(1)
                    product['ProductName'] = matches.group(1)
                else:
                    review['ProductName'] = review['TestTitle']
                    product['ProductName'] = review['TestTitle']

                review['Author'] = self.extract(review_section.xpath('//div[@class="postmeta"]/span[@class="author"]//text()'))

                extracted_date = self.extract(review_section.xpath('//div[@class="postmeta"]/span[@class="date"]/text()'))
                review["TestDateText"] = date_format(extracted_date, "%b %d, %Y")

                review['TestSummary'] = self.extract_all(review_section.xpath('//div[@class="postcontent"]/p[1]/descendant-or-self::*/text()'), separator=" ")

                product['PicURL'] = self.extract(review_section.xpath('//figure/img/@src'))

                review_url = self.extract(review_section.xpath('//h2/a/@href'))

                req = Request(review_url, callback=self.parse_reviews)
                req.meta['product'] = product
                req.meta['review'] = review
                yield req

        next_url = self.extract(response.xpath('//a[text()="Next"]/@href'))
        if next_url:
            list_req = Request(next_url, callback=self.parse_list_page)
            yield list_req

    def parse_reviews(self, response):
        product = response.meta['product']
        review = response.meta['review']

        product['TestUrl'] = response.url

        review['TestVerdict'] = self.extract_all(response.xpath('//h4[contains(text(),"Wrap") or contains(text(),"Conclusion")]/following-sibling::p//text()'), separator=" ")
        if not review['TestVerdict']:
            review['TestVerdict'] = self.extract_all(response.xpath('//h3[contains(text(),"Wrap") or contains(text(),"Conclusion")]/following-sibling::p//text()'), separator=" ")

        review['DBaseCategoryName'] = "PRO"
        review['TestUrl'] = response.url

        review['TestPros'] = self.extract_all(response.xpath("//div[contains(@class, 'review-pros')]//li/text()"),
                                              separator=' ; ')
        review['TestCons'] = self.extract_all(response.xpath("//div[contains(@class, 'review-cons')]//li/text()"),
                                              separator=' ; ')

        review_json_ld = extruct_helper.extract_json_ld(response.text, 'Review')
        if review_json_ld:
            review = extruct_helper.review_item_from_review_json_ld(review_json_ld, review)

        yield product
        yield review
