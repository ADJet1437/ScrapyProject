# -*- coding: utf-8 -*-
import dateparser
from datetime import datetime

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from scrapy.http import Request
from alascrapy.lib.generic import get_full_url, date_format
from alascrapy.items import ReviewItem, ProductItem


class A9to5macSpider(AlaSpider):
    name = '9to5mac'
    allowed_domains = ['9to5mac.com']
    start_urls = ['http://9to5mac.com/']

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
            product_name = self.get_product_name(title)
            # product items
            product['ProductName'] = product_name
            product['PicURL'] = pic
            product['source_internal_id'] = sid
            product['TestUrl'] = test_url
            # review
            review['ProductName'] = product_name
            review['TestTitle'] = title
            review['TestSummary'] = sumamry
            review['TestUrl'] = test_url
            review['DBaseCategoryName'] = 'pro'
            review['source_internal_id'] = sid
            review['TestDateText'] = date
            review['Author'] = author

            yield review
            yield product
    
    def get_product_name(self, title):
        product_name = title
        if 'review' in title:
            product_name = product_name.split('review')[0].strip()
        if product_name.startswith('Review:'):
            product_name = product_name.replace('Review:', "").strip()
        product_name = product_name.replace('[Video]', '')

        return product_name
        