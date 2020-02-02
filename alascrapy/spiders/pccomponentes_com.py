__author__ = 'jim'

import re

from scrapy.http import Request

from alascrapy.items import ProductItem, CategoryItem, ReviewItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import date_format


class PccomponentesComSpider(AlaSpider):
    name = 'pccomponentes_com'
    allowed_domains = ['pccomponentes.com']
    start_urls = ['http://pccomponentes.com/']

    def parse(self, response):
        category_urls = self.extract_list(response.xpath('//div[@class="_submenu_cargado"]/@id'))

        for category_url in category_urls:
            category_url = 'http://www.pccomponentes.com/nuevo_menu/inc_menu_dinamico.php?opcion=%s' % \
                           category_url.strip('submenu_')
            yield Request(url=category_url, callback=self.parse_sub_category)

    def parse_sub_category(self, response):
        category_urls = self.extract_list(response.xpath(
                '//div[@class="secciones"]//li[not(child::ul)]'
                '/a[not(@onclick)][not(contains(@onmouseover,"mostrarSubmenuSubfamilia"))]/@href'))

        for category_url in category_urls:
            yield Request(url=category_url, callback=self.parse_category)

    def parse_category(self, response):
        category = None

        if "category" in response.meta:
            category = response.meta['category']

        if not category:
            path = self.extract_all(response.xpath('//div[@class="hilo-navegacion"]//span/text()'), " > ")
            applied_filter = response.xpath('//font[contains(text(),"Filtros Aplicados")]')

            if path and not applied_filter:
                category = CategoryItem()
                category['category_path'] = path
                category['category_leaf'] = self.extract(response.xpath('//h1/text()'))
                category['category_url'] = response.url
                yield category

        if category:
            if not self.should_skip_category(category):
                product_urls = self.extract_list(response.xpath(
                        '//meta[@itemprop="reviewCount"][@content>0]/ancestor::a/@href'))

                for product_url in product_urls:
                    request = Request(url=product_url, callback=self.parse_product)
                    request.meta['ocn'] = category['category_path']
                    yield request

                next_page_url = self.extract(response.xpath('//a[contains(text(),"Siguiente")]/@href'))
                if next_page_url:
                    request = Request(url=next_page_url, callback=self.parse_category)
                    request.meta['category'] = category
                    yield request

    def parse_product(self, response):
        product = ProductItem()

        product['TestUrl'] = response.url
        product['OriginalCategoryName'] = response.meta['ocn']
        product['ProductName'] = self.extract_all(response.xpath(
                '//div[@class="hilo-navegacion"]/descendant::span[last()]/text()'))
        product['PicURL'] = self.extract(response.xpath('//a[@id="imagen-principal-1"]/@href'))
        product['ProductManufacturer'] = self.extract(response.xpath('//span[@itemprop="brand"]/text()'))
        product['source_internal_id'] = self.extract(response.xpath('//li[@id="id_articulo"]/@data-id'))
        yield product

        mpn = self.extract(response.xpath('//span[@itemprop="productID"]/@content'))
        if mpn:
            product_id = self.product_id(product)
            product_id['ID_kind'] = "MPN"
            product_id['ID_value'] = mpn.strip('mpn:')
            product_id['source_internal_id'] = product['source_internal_id']
            yield product_id

        review_url = 'http://www.pccomponentes.com/comentarios/inc_pagina_comentarios.php?id_articulo=%s' \
                     '&orden=recientes' % product['source_internal_id']
        request = Request(url=review_url, callback=self.parse_reviews)
        request.meta['product'] = product
        yield request

    def parse_reviews(self, response):
        reviews = response.xpath('//div[@class="caja-comentarios"]')
       
        for review in reviews:
            user_review = ReviewItem()
            user_review['DBaseCategoryName'] = "USER"
            user_review['ProductName'] = response.meta['product']['ProductName']
            user_review['TestUrl'] = response.meta['product']['TestUrl']
            user_review['source_internal_id'] = response.meta['product']['source_internal_id']
            date = self.extract(review.xpath('./p/text()[2]'))
            user_review['TestDateText'] = date_format(date, '%d-%m-%Y')
            rates = self.extract_list(review.xpath('.//li[@class="current-rating"]'))
            scale = 0
            rating = 0
            for rate in rates:
                rate_match = re.findall(r'([\d.]+)/5', rate)
                rating += float(rate_match[0])
                scale += 5
            user_review['SourceTestRating'] = str(rating)
            user_review['SourceTestScale'] = str(scale)
            user_review['Author'] = self.extract(review.xpath('.//span[contains(@class,"nick")]/text()'))
            user_review['TestSummary'] = self.extract(review.xpath('.//div[@class="caja"]/text()[1]'))
            user_review['TestPros'] = self.extract(review.xpath(
                    './/strong[contains(text(),"Ventajas")]/following-sibling::text()[1]'))
            user_review['TestCons'] = self.extract(review.xpath(
                    './/strong[contains(text(),"Desventajas")]/following-sibling::text()[1]'))
            yield user_review
