# -*- coding: utf8 -*-
from datetime import datetime

from alascrapy.spiders.base_spiders import ala_spider as spiders
from alascrapy.items import ProductIdItem


class DPReviewProductsSpider(spiders.AlaSpider):
    name = 'dpreview_products'
    allowed_domains = ['dpreview.com']
    start_urls = ['http://www.dpreview.com/products/cameras/all',
                  'http://www.dpreview.com/products/lenses/all',
                  'http://www.dpreview.com/products/printers/all']

    prod_id_config = {
        'cameras': {
            'name': 'Digital Cameras',
            'prod_ids': [
                {
                    'ID_kind': 'camera_type',
                    'xpath': '//table//tr[./td[contains(text(), '
                    '"Body type")]]/td[2]/text()'
                },
            ]
        },
        'lenses': {
            'name': 'Lenses',
            'prod_ids': [
                {
                    'ID_kind': 'lens _type',
                    'xpath': '//table//tr[./td[contains(text(), '
                    '"Lens type")]]/td[2]/text()'
                },
            ]
        },
        'printers': {
            'name': 'Printers',
            'prod_ids': []
        },
    }

    def parse(self, response):
        next_page_xpath = '//td[@class="next enabled"]/a/@href'
        next_page_link = response.xpath(next_page_xpath).extract()
        if len(next_page_link) > 0:
            yield response.follow(url=next_page_link[0], callback=self.parse)

        product_links_xpath = '//td[@class="product"]' \
            '//div[@class="name"]/a/@href'
        product_links = response.xpath(product_links_xpath).extract()
        for link in product_links:
            # Gets "cameras", "lenses" or "printers" from the start_urls
            category = response.url.split('/')[-2]
            yield response.follow(
                url=link,
                callback=self.parse_product_page,
                meta={'category': category}
            )

    def parse_product_page(self, response):
        product = self.parse_product(response)
        product_ids = self.parse_product_ids(response, product)
        yield product
        for product_id in product_ids:
            yield product_id
        # yield product

    def parse_product(self, response):
        product_xpaths = {
            'PicURL': '//meta[@property="og:image"]/@content',
            'ProductManufacturer': '//div[@class="breadcrumbs"]/a[2]/text()',
            'ProductName': '//h1/text()',
        }
        product = self.init_item_by_xpaths(response, 'product', product_xpaths)

        product['TestUrl'] = response.url
        product['source_id'] = self.spider_conf['source_id']

        category = response.meta['category']
        config = self.prod_id_config[category]
        ocn = config['name']
        # tries to get more precise category names for cameras
        if category == 'cameras':
            if '/slrs/' in response.url:
                ocn = 'Interchangeable Lens Cameras'
            elif '/compacts/' in response.url:
                ocn = 'Compact Cameras'

        product['OriginalCategoryName'] = ocn

        return product

    def parse_product_ids(self, response, product):
        config = self.prod_id_config[response.meta['category']]
        prod_ids = config['prod_ids']

        items = []

        for prod_id_config in prod_ids:
            kind = prod_id_config['ID_kind']
            xpath = prod_id_config['xpath']

            value = self.extract(response.xpath(xpath))

            product_id = ProductIdItem.from_product(
                product, kind=kind, value=value)
            items.append(product_id)

        return items
