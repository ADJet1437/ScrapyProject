# -*- coding: utf-8 -*-
import dateparser
from datetime import datetime

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from scrapy.http import Request
from alascrapy.lib.generic import get_full_url, date_format
from alascrapy.items import ReviewItem, ProductItem


class A9to5googleSpider(AlaSpider):
    name = '9to5google'
    allowed_domains = ['9to5google.com']
    start_urls = ['http://9to5google.com/']

    def parse(self, response):
        sub_links = self.extract_list(response.xpath(
            "//ul[@id='menu-guides']//li//a/@href"))
        for url in sub_links:
            url = get_full_url(response.url, url)
            yield Request(url=url, callback=self.parse_reviews)

    def parse_reviews(self, response):
        review = ReviewItem()
        product = ProductItem()
        contents = response.xpath('//article[@class="post-content"]')
        for content in contents:
            title = self.extract(content.xpath(
                './/div//h1[@class="post-title"]//text()'))
            test_url = self.extract(content.xpath(
                './/div//h1[@class="post-title"]//a/@href'))
            author = self.extract(content.xpath(
                './/span[@itemprop="name"]/text()'))
            date_str = self.extract_all(content.xpath(
                './/meta[@itemprop="datePublished"]/@content'))
            date = date_format(date_str, '%Y-%m-%d')
            pic = self.extract(content.xpath('.//img/@src'))
            sumamry = self.extract_all(content.xpath(
                './/div[@itemprop="articleBody"]//text()'))
            sid = test_url.split('/')[-2]
            # product items
            product['ProductName'] = title
            product['PicURL'] = pic
            product['source_internal_id'] = sid
            product['TestUrl'] = test_url
            # review
            review['ProductName'] = title
            review['TestTitle'] = title
            review['TestSummary'] = sumamry
            review['TestUrl'] = test_url
            review['DBaseCategoryName'] = 'pro'
            review['source_internal_id'] = sid
            review['TestDateText'] = date
            review['Author'] = author

            yield review
            yield product
