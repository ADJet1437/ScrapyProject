# -*- coding: utf8 -*-

__author__ = 'zaahid'
from datetime import datetime

from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.items import ProductIdItem, ProductItem


class MindFactorySpider(AlaSpider):
    name = 'mindfactory_de'
    allowed_domains = ['mindfactory.de']
    start_urls = ['https://www.mindfactory.de/Notebook+~+PC/Netbooks.html',
                  'https://www.mindfactory.de/Notebook+~+PC/Notebooks.html']

    def parse(self, response):
        for product_url in response.xpath(
                '//*[@id="bProducts"]/div/div/div[3]/a/@href').extract():
            yield Request(url=product_url, callback=self.parse_items)

        next_page = response.xpath(
            (u"//*[@class='text-right']//li/a[@aria-label='Nächste Seite']/@href")).extract_first()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield response.follow(next_page, callback=self.parse)

    def parse_items(self, response):
        product_id = ProductIdItem()
        price = response.xpath(
                    '//*[@id="priceCol"]/div[2]/text()').extract()
        product_id['ProductName'] = self.extract(
                    response.xpath('//*[@id="cart_quantity"]/div/div[2]/h1/text()'))
        product_id['source_internal_id'] = self.extract(response.xpath('//span[@class="sku-model"]/text()'))
        if price:
            product_id['ID_kind'] = 'price'
            product_id['ID_value'] = str(price).split()[4].replace(
                "u'\\xa0", "").replace("*", "")
        EAN_id_xpath = '//span[@class="product-ean"]/text()'
        EAN_id = self.extract(response.xpath(EAN_id_xpath))
        if EAN_id:
            product_id['ID_kind'] = "EAN"
            product_id['ID_value'] = EAN_id
        yield product_id

        product = ProductItem()
        product['source_internal_id'] = self.extract(response.xpath('//span[@class="sku-model"]/text()'))
        product['ProductName'] = self.extract(response.xpath(
            '//*[@id="cart_quantity"]/div/div[2]/h1/text()'))
        picture = response.xpath(
            '//*[@id="bImageCarousel"]/div/div[1]/a/img').extract()
        if picture:
            product['PicURL'] = str(picture).split('=')[1].replace("alt", "").replace("\'", "").replace(" \"", "").replace("\"", "")
            product['OriginalCategoryName'] = self.extract(response.xpath(
                '//*[@id="bBreadcrumb"]/ol/li/a/span/text()'))
            product['TestUrl'] = response.url
            yield product
