__author__ = 'jim'

import re

from scrapy.http import Request

from alascrapy.items import ProductItem, ReviewItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import date_format


class AllaboutphonesNlSpider(AlaSpider):
    name = 'allaboutphones_nl'
    allowed_domains = ['allaboutphones.nl']
    start_urls = ['https://www.allaboutphones.nl/reviews/smartphones/',
                  'https://www.allaboutphones.nl/reviews/tablets/',
                  'https://www.allaboutphones.nl/reviews/wearables/']
            
    def parse(self, response):
        product_urls = self.extract_list(response.xpath('//a[@class="btn-readmore"]/@href'))
        for product_url in product_urls:
            yield Request(url=product_url, callback=self.parse_product)
        
    def parse_product(self, response):
        product = ProductItem()
        product['TestUrl'] = response.url
        product['OriginalCategoryName'] = self.extract(response.xpath(
                '//span[@class="breadcrumb_last"]/text()'))
        product['ProductName'] = self.extract(response.xpath('//h1/text()'))
        product['PicURL'] = self.extract(response.xpath(
                '//meta[@property="og:image"]/@content'))
        yield product

        review = ReviewItem()
        review['DBaseCategoryName'] = "PRO"
        review['ProductName'] = product['ProductName']
        review['TestUrl'] = response.url
        date = self.extract(response.xpath('//@datetime'))
        review['TestDateText'] = date_format(date, '')
        script = self.extract(response.xpath('//script[@type="application/ld+json"]/text()'))
        rate_match = re.findall(r'"ratingValue": ([\d.]+)', script)
        if rate_match:
            review['SourceTestRating'] = rate_match[0]
        review['Author'] = self.extract(response.xpath('//a[@itemprop="author"]/text()'))
        review['TestTitle'] = product['ProductName']
        review['TestSummary'] = self.extract_all(response.xpath('//div[@class="post-content"]/p[1]//text()'))
        review['TestVerdict'] = self.extract_all(response.xpath('//h2[last()]/following::p[1]//text()'))
        review['TestPros'] = self.extract_all(response.xpath('//div[@class="positive"]//li/text()'), '; ')
        review['TestCons'] = self.extract_all(response.xpath('//div[@class="negative"]//li/text()'), '; ')
        yield review
