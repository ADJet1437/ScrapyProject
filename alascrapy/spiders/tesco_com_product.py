# -*- coding: utf8 -*-

import re

from scrapy.http import Request

from alascrapy.spiders.base_spiders.bazaarvoice_spiderAPI5_5 import BazaarVoiceSpiderAPI5_5
from alascrapy.lib.generic import date_format
from alascrapy.items import ProductIdItem, CategoryItem
from alascrapy.lib.generic import get_full_url

import alascrapy.lib.dao.incremental_scraping as incremental_utils


class Tesco_com_Product_Spider(BazaarVoiceSpiderAPI5_5):
    name = 'tesco_com_product'
    #start_urls = ['https://www.tesco.com/direct/help/sitemap.page']
    start_urls = ['https://www.tesco.com/direct/acer-aspire-a114-31-1-14-intel-pentium-4gb-ram-64gb-storage-laptop-black/445-8269.prd?skuId=445-8269']

    bv_base_params = {'passkey': 'asiwwvlu4jk00qyffn49sr7tb',
                      'display_code': '1235-en_gb',
                      'content_locale': 'en_GB'}

    def parse(self, response):
        #Product
        product_xpaths = {
            "ProductName": "//h1[contains(@class,'title')]/span[@itemprop='name']/text()",
        }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['source_internal_id'] = self.extract(response.xpath("//*[@itemprop='sku']/text()"))

        #Category
        category_leaf_xpath = "(//a[contains(@itemprop,'url')]/span[contains(@itemprop,'title')])[last()]/text()"
        category_path_xpath = "(//a[contains(@itemprop,'url')]/span[contains(@itemprop,'title')])/text()"
        category = CategoryItem()
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        #product's OriginalCategoryName should always match category_path of the corresponding category item
        product['OriginalCategoryName'] = category['category_path']

        yield product
        yield category

        #Review
        bv_params = self.bv_base_params.copy()
        bv_params['bv_id'] = product['source_internal_id']
        bv_params['offset'] = 0
        review_url = self.get_review_url(**bv_params)
        request = Request(url=review_url, callback=self.parse_reviews)

        last_user_review = incremental_utils.get_latest_user_review_date_by_sii(
            self.mysql_manager, self.spider_conf['source_id'],
            product["source_internal_id"]
        )
        request.meta['last_user_review'] = last_user_review
        request.meta['bv_id'] = product['source_internal_id']
        request.meta['product'] = product
        request.meta['filter_other_sources'] = False
        yield request


