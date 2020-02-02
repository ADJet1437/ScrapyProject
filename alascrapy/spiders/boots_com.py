__author__ = 'frank'

from scrapy.http import Request

from alascrapy.items import ProductItem, CategoryItem, ProductIdItem
from alascrapy.lib.generic import get_full_url
from alascrapy.spiders.base_spiders.bazaarvoice_spiderAPI5_5 import BazaarVoiceSpiderAPI5_5

import alascrapy.lib.dao.incremental_scraping as incremental_utils

import re


class BootsComSpider(BazaarVoiceSpiderAPI5_5):
    name = 'boots_com'
    start_urls = ['http://www.boots.com/site-map']

    bv_base_params = {'passkey': '324y3dv5t1xqv8kal1wzrvxig',
                      'display_code': '2111-en_gb',
                      'content_locale': 'en_EU,en_GB,en_IE,en_US'}

    def parse(self, response):
        root_category_xpath = "(//li[@class='h2 siteMapSection'])[1]//li[@class='h2 subcategoryBlock']"
        root_category_name_xpath = "./a/text()"

        middle_cat_xpath = ".//li[@class='h3 subcategoryChildHeading']"
        middle_cat_name_xpath = "./a/text()"
        middle_cat_url_xpath = "./a/@href"

        leaf_category_xpath = ".//li[@class='h3']"
        leaf_name_xpath = "./a/text()"
        leaf_url_xpath = "./a/@href"

        category_list = []

        root_categories = response.xpath(root_category_xpath)
        for root_category in root_categories:
            root_category_name = self.extract_xpath(root_category,
                                                    root_category_name_xpath)
            middle_cats = root_category.xpath(middle_cat_xpath)
            for middle_cat in middle_cats:
                middle_cat_name = self.extract_xpath(middle_cat,
                                                     middle_cat_name_xpath)

                leaf_categories = middle_cat.xpath(leaf_category_xpath)

                if not leaf_categories:
                    category_path = "%s | %s" % (root_category_name, middle_cat_name)

                    category = CategoryItem()
                    category['category_path'] = category_path
                    category['category_url'] = self.extract_xpath(middle_cat, middle_cat_url_xpath)
                    yield category

                    category_list.append(category)

                for leaf in leaf_categories:
                    leaf_name = self.extract_xpath(leaf, leaf_name_xpath)
                    leaf_url = self.extract_xpath(leaf, leaf_url_xpath)

                    category_path = "%s | %s | %s" % (root_category_name,
                                                      middle_cat_name,
                                                      leaf_name)

                    category = CategoryItem()
                    category['category_path'] = category_path
                    category['category_url'] = leaf_url
                    yield category

                    category_list.append(category)

            for category in category_list:
                if not self.should_skip_category(category):
                    request = Request(category['category_url'], self.parse_category)
                    request.meta['category'] = category
                    yield request

    def parse_category(self, response):
        products_xpath = "//div[@class='product_info']"
        product_url_xpath = "./div[@class='product_name']/a/@href"
        has_review_xpath = ".//div[@class='product_rating']/span[@class!='noRating']"
        next_page_xpath = "(//*[@rel='next'])[1]/@href"

        products = response.xpath(products_xpath)
        category = response.meta['category']
        category_name = category['category_path']

        # Not a leaf category page
        if not products:
            return

        for product in products:
            has_review = product.xpath(has_review_xpath)
            if not has_review:
                continue

            product_url = self.extract(product.xpath(product_url_xpath))
            product_url = get_full_url(response, product_url)
            request = Request(product_url, callback=self.parse_product)
            request.meta['OriginalCategoryName'] = category_name
            yield request

        next_page_url = self.extract_xpath(response, next_page_xpath)
        if next_page_url:
            next_page_url = get_full_url(response, next_page_url)
            next_page_request = Request(next_page_url, callback=self.parse_category)
            next_page_request.meta['category'] = category
            yield next_page_request

    def parse_product(self, response):
        product_name_xpath = "//h1[@itemprop='name']/text()"
        product_id_xpath = "//div[@class='productid']/text()"
        manufacturer_xpath = "//input[@id='productManufacturerName']/@value"
        bv_id_xpath = "//input[@id='product_ID']/@value"

        product = ProductItem()
        product['TestUrl'] = response.url
        product['OriginalCategoryName'] = response.meta['OriginalCategoryName']
        product['source_internal_id'] = self.extract(response.xpath(product_id_xpath))
        product['ProductName'] = self.extract(response.xpath(product_name_xpath))
        product['ProductManufacturer'] = self.extract(response.xpath(manufacturer_xpath))

        bv_id = self.extract(response.xpath(bv_id_xpath))

        if product['ProductName'] and product['source_internal_id'] and bv_id:
            yield product

            product_id = self.product_id(product)
            product_id['ID_kind'] = "boots_com_id"
            product_id['ID_value'] = product['source_internal_id']
            yield product_id

            bv_params = self.bv_base_params.copy()
            bv_params['bv_id'] = bv_id
            bv_params['offset'] = 0
            review_url = self.get_review_url(**bv_params)
            request = Request(url=review_url, callback=self.parse_reviews)

            last_user_review = incremental_utils.get_latest_user_review_date_by_sii(
                self.mysql_manager, self.spider_conf['source_id'],
                product["source_internal_id"]
            )
            request.meta['last_user_review'] = last_user_review
            request.meta['filter_other_sources'] = False

            request.meta['bv_id'] = bv_id
            request.meta['product'] = product
            yield request
        else:
            self.logger.info("Could not scrape product at %s" % response.url)
