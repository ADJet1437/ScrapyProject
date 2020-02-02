# -*- coding: utf8 -*-
from datetime import datetime

from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.items import ProductIdItem, ProductItem


class EpDeSpider(AlaSpider):
    name = 'ep_de'
    allowed_domains = ['ep.de']
    start_urls = ['https://www.ep.de/c/472/tv-audio',
                  'https://www.ep.de/c/474/computer-foto',
                  'https://www.ep.de/c/115/telefon-navi/handys-smartphones',
                  'https://www.ep.de/c/107/telefon-navi/wearables']

    def parse(self, response):

        for product_url in response.xpath(
                "//div[@class='cmsproductlist-desktop-layout-item']//h3/a/@href").extract():
            product_page = response.urljoin(product_url)
            yield Request(url=product_page, callback=self.parse_items)

        next_page = response.xpath(
            ("//a[@class='pagination-item-link']/@href")).extract_first()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield response.follow(next_page, callback=self.parse)

    def parse_items(self, response):

        product = ProductItem()

        product['TestUrl'] = response.url
        product_name = self.extract(response.xpath('//meta[@property="og:title"]/@content'))
        product['ProductName'] = product_name.replace(" | EP:", "")
        product['PicURL'] = self.extract(response.xpath('//meta[@property="og:image"]/@content'))
        product['ProductManufacturer'] = self.extract(response.xpath("//div[@class='product-details-left']/a//@title"))
        product['source_internal_id'] = str(response.url).split("/")[5]
        yield product

        price_xpath = "//div/div[@class='product-details-price']//div/text()"
        price = self.extract(response.xpath(price_xpath))
        if price:
            product_id = ProductIdItem()
            product_id['source_internal_id'] = product["source_internal_id"]
            product_id['ProductName'] = product["ProductName"]
            product_id['ID_kind'] = "price"
            product_id['ID_value'] = price.replace(".", "").rstrip(",-")
            yield product_id

        EAN_id_xpath = "//div[@class='product-flixdata']/@data-ean" 
        EAN_id = self.extract(response.xpath(EAN_id_xpath))
        if EAN_id:
            product_id = ProductIdItem()
            product_id['source_internal_id'] = product["source_internal_id"]
            product_id['ProductName'] = product["ProductName"]
            product_id['ID_kind'] = "EAN"
            product_id['ID_value'] = EAN_id
            yield product_id