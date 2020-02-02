# -*- coding: utf8 -*-
__author__ = 'leonardo'

import re

from scrapy.http import Request

from alascrapy.items import CategoryItem, ProductItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, normalize_price, parse_float


class MediaMarktEsSpider(AlaSpider):
    name = 'mediamarkt_es'
    allowed_domains = ['mediamarkt.es']
    start_urls = ['http://tiendas.mediamarkt.es/productos']

    source_internal_id_re = '-(\d+)$'

    def parse(self, response):
        product_container_xpath = "//*[@id='categoryContainerProducts']"
        category_path_xpath = "//a[contains(@class,'categoryPath')]/text()"
        category_leaf_xpath = "(//a[contains(@class,'categoryPath')])[last()]/text()"
        product_url_xpath = "(//a[contains(@class,'productName')])/@href"
        next_page_xpath = "//div[@class='pagerContainer']/a[contains(@class, 'arrow') and not(contains(@class, 'arrowPrev'))]/@href"
        subcategory_xpath = "//a[contains(@class, 'categoryTree')]/@href"

        category = response.meta.get('category', None)

        if response.xpath(product_container_xpath):
            if not category:
                category = CategoryItem()
                category['category_url'] = response.url
                category['category_leaf'] = self.extract(
                    response.xpath(category_leaf_xpath))
                category['category_path'] = self.extract_all(
                    response.xpath(category_path_xpath), separator='>')
                yield category

            if self.should_skip_category(category):
                return

            product_urls = self.extract_list(response.xpath(product_url_xpath))
            for product_url in product_urls:
                product_url = get_full_url(response, product_url)
                request = Request(product_url, callback=self.parse_product)
                request.meta['category'] = category
                yield request


            next_page_url = self.extract(response.xpath(next_page_xpath))
            next_page_url = get_full_url(response, next_page_url)
            if next_page_url:
                request = Request(next_page_url, callback=self.parse)
                request.meta['category'] = category
                yield request

        else:
            subcategory_urls = self.extract_list(response.xpath(subcategory_xpath))

            for subcategory_url in subcategory_urls:
                subcategory_url = get_full_url(response, subcategory_url)
                request = Request(subcategory_url, callback=self.parse)
                yield request

    def parse_product(self, response):
        category = response.meta['category']
        product_name_xpath = "//h1[@itemprop='name']/text()"
        pic_url_xpath = "//div[@id='productDetailImage']//img/@src"
        manufacturer_xpath = "//div[@class='productDetailBrand']/img/@alt"
        price_xpath = "//div[contains(@class, 'mm-price')]/@price"
        source_internal_id_xpath = u"//div[contains(@class, " \
                                   u"'productCustomTagName') and contains(text(), 'Número de artículo')]/following-sibling::div[contains(@class, 'productCustomTagValue')]/text()"
        source_internal_id = None

        product = ProductItem.from_response(response, category)
        product['ProductName'] = self.extract(response.xpath(product_name_xpath))
        product["PicURL"] = self.extract(response.xpath(pic_url_xpath))
        product['ProductManufacturer'] = self.extract(response.xpath(manufacturer_xpath))

        match = re.search(self.source_internal_id_re, response.url)
        if match:
            source_internal_id = match.group(1)

        if not source_internal_id:
            source_internal_id = self.extract(response.xpath(source_internal_id_xpath))

        if source_internal_id:
            product['source_internal_id'] = source_internal_id

        mediamarkt_es_id = self.product_id(product)
        mediamarkt_es_id['ID_kind'] = 'mediamarkt_es_id'
        mediamarkt_es_id['ID_value'] = source_internal_id

        price_value = parse_float(self.extract(response.xpath(price_xpath)))
        if price_value:
            price = self.product_id(product)
            price['ID_kind'] = 'price'
            price['ID_value'] = normalize_price(price_value)
            yield price

        yield product
        yield mediamarkt_es_id