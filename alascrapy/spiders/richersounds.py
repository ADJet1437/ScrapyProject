__author__ = 'frank'

import re

from scrapy.http import Request

from alascrapy.spiders.base_spiders.bazaarvoice_spiderAPI5_5 import BazaarVoiceSpiderAPI5_5
from alascrapy.items import ProductIdItem, CategoryItem

from alascrapy.lib.generic import get_full_url

import alascrapy.lib.dao.incremental_scraping as incremental_utils


class RicheroundsSpider(BazaarVoiceSpiderAPI5_5):
    name = 'richersounds'
    start_urls = ['https://www.richersounds.com']

    bv_base_params = {'passkey': 'cawj3xzogWwKtMUd5xFgJbRIlwkwbd7He70TVLGqlFRA0',
                      'display_code': '5110-en_gb',
                      'content_locale': 'en_GB'}

    source_internal_id_re = re.compile('productId\s*=\s*"([^"]+)";')

    def parse(self, response):
        category_url_xpath = "//li[contains(@class, 'level2')]/a/@href"
        category_urls = self.extract_list(response.xpath(category_url_xpath))

        for url in category_urls:
            url = get_full_url(response, url)
            request = Request(url, callback=self.parse_category)
            yield request

    def parse_category(self, response):
        product_xpath = "//ol[contains(@class, 'products')]//div[@class='product-item-info']"
        product_url_xpath = ".//a[@class='product-item-link']/@href"
        next_page_xpath = "(//a[@title='Next'])[1]/@href"

        products = response.xpath(product_xpath)
        if not products:
            return

        for product_entity in products:
            product_url = self.extract(product_entity.xpath(product_url_xpath))
            if product_url:
                product_url = get_full_url(response, product_url)
                request = Request(product_url, callback=self.parse_product)
                yield request

        next_page_url = self.extract(response.xpath(next_page_xpath))
        if next_page_url:
            next_page_url = get_full_url(response, next_page_url)
            request = Request(next_page_url, callback=self.parse_category)
            yield request

    def parse_product(self, response):
        product_xpaths = {"PicURL": "(//*[@property='og:image'])[1]/@content",
                          "ProductName": "//h1//text()",
                          "OriginalCategoryName": "//li[contains(@class, 'item category')][last()]/a/text()",
                          "ProductManufacturer":  "//th[@class='col label' and text()='Brand']/"
                                                  "following-sibling::*/text()"
                          }

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        bv_config_data = self.extract(response.xpath("//script[@type='text/javascript']"
                                                     "[contains(text(),'productId')]/text()"))

        if product.get('OriginalCategoryName', ''):
            category = CategoryItem()
            category_url = self.extract(response.xpath("//li[contains(@class, 'item category')][last()]/a/@href"))
            category['category_url'] = get_full_url(response, category_url)
            category['category_leaf'] = product['OriginalCategoryName']
            category['category_path'] = category['category_leaf']
            yield category

        match = re.search(self.source_internal_id_re, bv_config_data)
        if match:
            product["source_internal_id"] = match.group(1).upper()

            product_id = ProductIdItem()
            product_id['source_internal_id'] = product["source_internal_id"]
            product_id['ProductName'] = product["ProductName"]
            product_id['ID_kind'] = "richersounds_id"
            product_id['ID_value'] = product["source_internal_id"]
            yield product_id
            yield product

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
