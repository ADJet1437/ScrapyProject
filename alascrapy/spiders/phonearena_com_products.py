# -*- coding: utf8 -*-

import re

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url
from alascrapy.items import ProductItem, ProductIdItem


class PhoneArenaComProductsSpider(AlaSpider):
    name = 'phonearena_com_products'
    allowed_domains = ['phonearena.com']
    start_urls = ['https://www.phonearena.com/phones/manufacturers']

    def parse(self, response):
        contents = response.xpath(
            '//div[@class="manufacturer-item stream-item"]')
        for content in contents:
            link = self.extract(content.xpath(
                './/a[@class="thumbnail"]/@href'))
            full_path = get_full_url(response.url, link)
            brand = self.extract(content.xpath('.//span//text()'))
            yield response.follow(url=full_path,
                                  callback=self.parse_product,
                                  meta={'brand': brand})

    def parse_product(self, response):
        ori_cat = self.extract(response.xpath(
            "//li[@class='active']/span/text()"))
        brand = response.meta.get('brand', '')
        contents = response.xpath('//div[@class="stream-item"]')
        for content in contents:
            product = ProductItem()
            product_id = ProductIdItem()
            img_url = self.extract(content.xpath('.//img/@data-src'))
            page_url = self.extract(content.xpath(
                './/a[@class="thumbnail"]/@href'))
            test_url = get_full_url(response.url, page_url)
            product_name = self.extract(content.xpath(
                './/p[@class="title"]/text()'))
            source_internal_id_re = r'id([0-9]+)'
            match = re.search(source_internal_id_re, test_url)
            if match:
                source_internal_id = match.group(1)
                product['source_internal_id'] = source_internal_id
            # assigning values
            product['ProductName'] = product_name
            product['PicURL'] = img_url
            product['ProductManufacturer'] = brand
            product['TestUrl'] = test_url
            product['OriginalCategoryName'] = ori_cat

            yield ProductIdItem.from_product(product,
                                       kind='phonearena_internal_id', 
                                       value=source_internal_id)
            yield product
