# -*- coding: utf8 -*-
import re
import json

from alascrapy.items import ProductIdItem, CategoryItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.extruct_helper as extruct_helper


class Bcc_nl_Spider(AlaSpider):
    """
    This spider only crawl for products' info.
    """
    name = 'bcc_nl'
    allowed_domains = ['bcc.nl']
    # skipped cats including network and all accessories.
    # only got console in gaming cat, 
    # only man/woman shaver nd oral tools in personal cat are kept.
    start_urls = [
        'https://www.bcc.nl/huishouden/wasmachine',
        'https://www.bcc.nl/huishouden/wasdroger',
        'https://www.bcc.nl/huishouden/stofzuiger',
        'https://www.bcc.nl/huishouden/stoomreiniger',
        'https://www.bcc.nl/huishouden/strijken',
        'https://www.bcc.nl/huishouden/verlichting',
        'https://www.bcc.nl/huishouden/klimaatbeheersing',
        'https://www.bcc.nl/huishouden/hogedrukreiniger',
        'https://www.bcc.nl/keuken/koelkast',
        'https://www.bcc.nl/keuken/koelvriescombinatie',
        'https://www.bcc.nl/keuken/amerikaanse-koelkast',
        'https://www.bcc.nl/keuken/vriezer',
        'https://www.bcc.nl/keuken/vaatwasser',
        'https://www.bcc.nl/keuken/fornuis-en-kookplaat',
        'https://www.bcc.nl/keuken/magnetron-en-oven',
        'https://www.bcc.nl/keuken/koffiezetapparaat',
        'https://www.bcc.nl/keuken/voedselbereiding',
        'https://www.bcc.nl/keuken/drankbereiding',
        'https://www.bcc.nl/inbouw-apparatuur/koelkast',
        'https://www.bcc.nl/inbouw-apparatuur/vriezer',
        'https://www.bcc.nl/inbouw-apparatuur/vaatwasser',
        'https://www.bcc.nl/inbouw-apparatuur/oven',
        'https://www.bcc.nl/inbouw-apparatuur/kookplaat',
        'https://www.bcc.nl/inbouw-apparatuur/magnetron',
        'https://www.bcc.nl/inbouw-apparatuur/afzuigkap',
        'https://www.bcc.nl/inbouw-apparatuur/koffie',
        'https://www.bcc.nl/inbouw-apparatuur/wasmachine',
        'https://www.bcc.nl/beeld-en-geluid/televisie',
        'https://www.bcc.nl/beeld-en-geluid/digitale-tv',
        'https://www.bcc.nl/beeld-en-geluid/blu-ray-dvd-en-mediaspeler',
        'https://www.bcc.nl/beeld-en-geluid/audiosystemen-en-componenten',
        'https://www.bcc.nl/beeld-en-geluid/home-cinema-systeem',
        'https://www.bcc.nl/beeld-en-geluid/ipod-en-mp3',
        'https://www.bcc.nl/beeld-en-geluid/radio',
        'https://www.bcc.nl/beeld-en-geluid/autoradio',
        'https://www.bcc.nl/beeld-en-geluid/hoofdtelefoons',
        'https://www.bcc.nl/beeld-en-geluid/dj-gear',
        'https://www.bcc.nl/beeld-en-geluid/mini-en-draadloze-speakers',
        'https://www.bcc.nl/foto-en-video/compact-camera',
        'https://www.bcc.nl/foto-en-video/spiegelreflex-camera',
        'https://www.bcc.nl/foto-en-video/camcorder',
        'https://www.bcc.nl/foto-en-video/systeem-camera',
        'https://www.bcc.nl/foto-en-video/instant-camera',
        'https://www.bcc.nl/foto-en-video/cameralens',
        'https://www.bcc.nl/computer/tablet',
        'https://www.bcc.nl/computer/laptop',
        'https://www.bcc.nl/computer/e-readers',
        'https://www.bcc.nl/computer/desktop',
        'https://www.bcc.nl/computer/monitor',
        'https://www.bcc.nl/computer/printer-en-scanner',
        'https://www.bcc.nl/computer/opslagmedia',
        'https://www.bcc.nl/computer/gaming/game-console',
        'https://www.bcc.nl/persoonlijke-verzorging/scheren-en-trimmen',
        'https://www.bcc.nl/persoonlijke-verzorging/scheren-en-ontharen',
        'https://www.bcc.nl/persoonlijke-verzorging/mondverzorging',
        'https://www.bcc.nl/navigatie-en-telefoon/navigatiesysteem',
        'https://www.bcc.nl/navigatie-en-telefoon/huistelefoon',
        'https://www.bcc.nl/navigatie-en-telefoon/mobiele-telefoon',
        'https://www.bcc.nl/navigatie-en-telefoon/smartwatch',
    ]

    def parse(self, response):
        product_url_xpath = "//div[contains(@class,'lister-product')]/a/@href"
        product_urls = self.extract_list(response.xpath(product_url_xpath))

        for product_url in product_urls:
            yield response.follow(url=product_url,
                                  callback=self.parse_product_json)

        next_page_xpath = "//link[@rel='next']/@href"
        next_page_url = self.extract(response.xpath(next_page_xpath))
        if next_page_url:
            yield response.follow(url=next_page_url, callback=self.parse)

    def parse_product_json(self, response):
        product_json_ld = extruct_helper.extract_json_ld(response.body, 'Product')
        if product_json_ld:
            ocns = product_json_ld.get('category', '')
            if ocns:
                seperator = '/'
                ocns = ocns.split(seperator)
                ocn = ' | '.join (ocn for ocn in ocns)
                category = CategoryItem()
                category['category_path'] = ocn
                yield category

                if not self.should_skip_category(category):
                    product = extruct_helper.product_item_from_product_json_ld(product_json_ld)
                    product['source_id'] = self.spider_conf['source_id']
                    product['TestUrl'] = response.url
                    product['source_internal_id'] = product_json_ld.get('productID', '')
                    product['OriginalCategoryName'] = ocn
                    yield product

                    # Product Price Item
                    # ----------------------------------------
                    price_str = product_json_ld.get('offers', {}).get('price', '')
                    currency_str = product_json_ld.get('offers', {}).get('priceCurrency', '')
                    price_str = price_str + ' ' + currency_str
                    yield ProductIdItem.from_product(product, kind='price', value=price_str)

                    # Product SKU Item
                    # ----------------------------------------
                    sku_str = product_json_ld.get('sku', '')
                    yield ProductIdItem.from_product(product, kind='SKU', value=sku_str)




