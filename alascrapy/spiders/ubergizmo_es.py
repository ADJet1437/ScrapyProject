# -*- coding: utf-8 -*-
import scrapy

from urllib import unquote

from datetime import datetime

# from translate import Translator

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider

import alascrapy.lib.dao.incremental_scraping as incremental_utils

from alascrapy.items import ProductIdItem, CategoryItem


class UbergizmoEsSpider(AlaSpider):
    name = 'ubergizmo_es'
    allowed_domains = ['es.ubergizmo.com']
    start_urls = [
        'https://es.ubergizmo.com/categoria/mobile',
        'https://es.ubergizmo.com/categoria/smarthome',
    ]

    def __init__(self, *args, **kwargs):
        super(UbergizmoEsSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

    def parse(self, response):
        link_xpaths = '//h2[@class="entry-title"]/a/@href'
        links = self.extract_list(response.xpath(link_xpaths))
        for link in links:
            yield response.follow(link, callback=self.parse_review)

        # next page
        if self.continue_to_next_page(response):
            next_page_xpath = '//a[@class="next page-numbers"]/@href'
            next_page = self.extract(response.xpath(next_page_xpath))

            if next_page:
                yield response.follow(next_page, callback=self.parse)

    def continue_to_next_page(self, response):
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

        review_date_xpath = 'substring-before(//div[@class="entry-date"]'\
            '/text(), ",")'
        review_dates = self.extract_list(response.xpath(review_date_xpath))

        if review_dates:
            last_review_date = datetime.strptime(review_dates[-1], "%d %b %Y")
            if self.stored_last_date > last_review_date:
                return False
        return True

    def parse_review(self, response):
        product_xpaths = {
            'PicURL': '//header[@class="entry-header"]/div/img/@src',
            'source_internal_id': 'substring-after(//article/@id, "-")',
            'TestUrl': '//link[@rel="canonical"]/@href',
        }

        review_xpaths = {
            'TestSummary': '//div[@class="entry-excerpt"]/p/text()',
            'Author': '//div[@class="entry-author"]/a/text()',

            'TestVerdict': '//div[@class="entry-content"]/p[last()]/text()',

            'TestDateText': 'substring-before(//div[@class="entry-date"]'
                            '/time/@datetime, "T")',

            'source_internal_id': 'substring-after(//article/@id, "-")',

            'TestUrl': '//link[@rel="canonical"]/@href'
        }

        review = self.init_item_by_xpaths(response, 'review', review_xpaths)
        product = self.init_item_by_xpaths(response, 'product', product_xpaths)

        test_title_xpath = '//h1[@class="entry-title"]/text()'
        test_title = self.extract(response.xpath(test_title_xpath))

        url_str = unquote(response.url)
        # sii = url_str.split('_')[-1].split('.')[0]
        product_name = test_title
        # title_es = test_title
        # translator = Translator(from_lang="es-ES", to_lang="English")
        # title_en = translator.translate(title_es)
        # items_en = title_en.split(' ')
        # # items_es = url_str.split('/')[-1].split('-')
        # title_en_list = [item for item in items_en]
        # # title_es_list = [item for item in items_es]

        # product_name = ''
        # for char_en in title_en_list:
        #     # for char_es in title_es_list:
        #         # if char_en.lower() == char_es.lower():
        #     if char_en not in product_name:
        #         product_name += '{} '.format(char_en)

        review['ProductName'] = product_name
        review['DBaseCategoryName'] = 'PRO'
        review['TestTitle'] = test_title

        product['ProductName'] = product_name

        yield review
        yield product
