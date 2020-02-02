#!/usr/bin/env python

"""technobuffalo Spider: """

__author__ = 'graeme'

import re

from scrapy import Selector

from alascrapy.items import ProductItem, ReviewItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.selenium_browser import SeleniumBrowser


class TechnoBuffaloSpider(AlaSpider):
    name = 'technobuffalo'
    allowed_domains = ['technobuffalo.com']
    start_urls = ['http://www.technobuffalo.com/reviews/']

    def parse(self, response):
        with SeleniumBrowser(self, response) as browser:
            browser.get(response.url)
            keep_going = True

            while keep_going:
                selector = browser.scroll_until_the_end(5000)

                for review_text in selector.xpath('//article[@itemtype="http://schema.org/BlogPosting"]').extract():
                    review_section = Selector(text=review_text)
                    product = ProductItem()
                    review = ReviewItem()

                    product['OriginalCategoryName'] = "Miscellaneous"
                    review['DBaseCategoryName'] = "PRO"

                    review['TestTitle'] = self.extract(review_section.xpath('//h2[@itemprop="headline"]/a/text()'))

                    review['TestUrl'] = self.extract(review_section.xpath('//h2[@itemprop="headline"]/a/@href'))
                    product['TestUrl'] = review['TestUrl']

                    review['Author'] = self.extract(review_section.xpath('//span[@itemprop="author"]/a/text()'))

                    if review['TestTitle']:
                        matches = re.search("^(.*?) review", review['TestTitle'], re.IGNORECASE)
                        if matches:
                            review['ProductName'] = matches.group(1)
                            product['ProductName'] = matches.group(1)
                        else:
                            review['ProductName'] = review['TestTitle']
                            product['ProductName'] = review['TestTitle']

                    review["TestDateText"] = self.extract(review_section.xpath('//time/@datetime'))

                    review['TestSummary'] = self.extract_all(review_section.xpath('//div[@class="block-excerpt"]/div[@itemprop="articleBody"]/*/text()'), separator=" ")

                    product['PicURL'] = self.extract(review_section.xpath('//div[@class="block-image"]/a/img/@src'))

                    yield product
                    yield review

                if self.extract(selector.xpath('//div[@id="load-more-posts"]')):

                    #if self.extract(selector.xpath('//div[@id="load-more-posts"]/div')):
                    #    print "Current URL: ", self.browser.browser.current_url
                    #    self.browser.browser.refresh()
                    #else:
                    pre_click_headline = self.extract(selector.xpath('//article[@itemtype="http://schema.org/BlogPosting" and position()=2]//h2[@itemprop="headline"]/a/text()'))
                    browser.click('//div[@id="load-more-posts"]')
                    post_click_headline = self.extract(selector.xpath('//article[@itemtype="http://schema.org/BlogPosting" and position()=2]//h2[@itemprop="headline"]/a/text()'))
                    if pre_click_headline == post_click_headline:
                        keep_going = False
                else:
                    keep_going = False
