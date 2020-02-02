# -*- coding: utf8 -*-

import re

from scrapy.http import Request

from alascrapy.spiders.base_spiders.bazaarvoice_spiderAPI5_5 import BazaarVoiceSpiderAPI5_5
from alascrapy.lib.generic import date_format
from alascrapy.items import ProductIdItem, CategoryItem
from alascrapy.lib.generic import get_full_url

import alascrapy.lib.dao.incremental_scraping as incremental_utils


class VeryCoUkSpider(BazaarVoiceSpiderAPI5_5):
    name = 'very_co_uk'
    start_urls = ['http://www.very.co.uk/']
    custom_settings = {'COOKIES_ENABLED': True}

    bv_base_params = {'passkey': '35w0b6mavcfmefkhv3fccjwcc',
                      'display_code': '17045-en_gb',
                      'content_locale': 'en_GB'}

    source_internal_id_re = re.compile("/(\d+)\.prd")
    category_url_suffix = '?numProducts=99'

    def parse(self, response):
        categories_xpath = "//div[@id='menuElectricals' or @id='menuBeauty']/" \
                           "div[@class='topNavCol' and not(contains(./h3/text(), 'Shop By')) " \
                           "and not(contains(./h3/text(), 'Not To Be Missed'))]/a/@href"

        category_urls = self.extract_list(response.xpath(categories_xpath))

        for category_url in category_urls:
            category_url = get_full_url(response, category_url) + self.category_url_suffix
            request = Request(category_url, callback=self.parse_category)
            yield request

    def parse_category(self, response):
        is_category_xpath = "//*[@class='productList']"
        has_sub_cat_xpath = "//*[@class='Department']"
        category_path_xpath = "//ul[@class='breadcrumbList']/li[position() < last()]/a//text()"
        category_leaf_xpath = "//ul[@class='breadcrumbList']/li[last()]/a//text()"
        if not response.xpath(is_category_xpath):
            return

        if not response.xpath(has_sub_cat_xpath):
            next_page_xpath = "(//*[@rel='next'])[1]/@href"

            category = response.meta.get('category', None)
            if not category:
                category = CategoryItem()
                category['category_url'] = response.url
                category['category_leaf'] = self.extract(
                    response.xpath(category_leaf_xpath))
                category['category_path'] = self.extract_all(
                    response.xpath(category_path_xpath), separator=' | ')
                category['category_path'] = '%s | %s' % (category['category_path'],
                                                         category['category_leaf'])
                yield category

            if self.should_skip_category(category):
                return

            products_xpath = "//*[@class='productList']/li/div[@class='productInfo']"
            product_url_xpath = "./a[@class='productTitle'][1]/@href"
            product_rating_xpath = "./div[@class='bvRollup']"

            products = response.xpath(products_xpath)
            for product in products:
                has_reviews = self.extract(
                    product.xpath(product_rating_xpath))

                if has_reviews:
                    product_url = self.extract(product.xpath(product_url_xpath))
                    product_url = get_full_url(response, product_url)
                    request = Request(product_url, callback=self.parse_product)
                    request.meta['category'] = category
                    yield request

            next_page_url = self.extract(response.xpath(next_page_xpath))
            if next_page_url:
                next_page_url = get_full_url(response, next_page_url)
                request = Request(next_page_url, callback=self.parse_category)
                request.meta['category'] = category
                yield request
        else:
                subcat_url_xpath = "(//*[@class='Department']/following::ul[1])/li[not(contains(@class, 'hidden'))]/a/@href"
                subcat_urls = self.extract_list(response.xpath(subcat_url_xpath))
                for subcat_url in subcat_urls:
                    subcat_url = get_full_url(response, subcat_url)
                    request = Request(subcat_url, callback=self.parse_category)
                    yield request

    def parse_product(self, response):
        product_xpaths = { "PicURL": "//meta[@property='og:image']/@content",
                           "ProductName": "//h1[@class='productHeading']//text()",
                           "ProductManufacturer": "//h1[@class='productHeading']/text()"
                         }

        product = self.init_item_by_xpaths(response, "product", product_xpaths)

        match = re.search(self.source_internal_id_re, response.url)
        if match:
            product['source_internal_id'] = match.group(1)

        product['TestUrl'] = response.url
        product["OriginalCategoryName"] = response.meta["category"]["category_path"]
        yield product

        mpn_value = self.extract(response.xpath("//span[@id='productMPN']/text()"))
        if mpn_value:
            mpn = ProductIdItem()
            mpn['source_internal_id'] = product["source_internal_id"]
            mpn['ProductName'] = product["ProductName"]
            mpn['ID_kind'] = "MPN"
            mpn['ID_value'] = mpn_value
            yield mpn

        ean_value = self.extract(response.xpath("//span[@id='productEAN']/text()"))
        if ean_value:
            ean = ProductIdItem()
            ean['source_internal_id'] = product["source_internal_id"]
            ean['ProductName'] = product["ProductName"]
            ean['ID_kind'] = "EAN"
            ean['ID_value'] = ean_value
            yield ean

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

