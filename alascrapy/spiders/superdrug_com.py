__author__ = 'frank'

from scrapy.http import Request

from alascrapy.items import CategoryItem
from alascrapy.lib.generic import get_full_url
from alascrapy.spiders.base_spiders.bazaarvoice_spiderAPI5_5 import BazaarVoiceSpiderAPI5_5

import alascrapy.lib.extruct_helper as extruct_helper
import alascrapy.lib.dao.incremental_scraping as incremental_utils

import re


class SuperdrugComSpider(BazaarVoiceSpiderAPI5_5):
    name = 'superdrug_com'
    locale = 'en'
    #start_urls = ['https://www.superdrug.com/']

    # Hard-code category pages, as the source loads category menu dynamically and the sitemap does not work well
    start_urls = ['https://www.superdrug.com/Electricals/Hair-Stylers/c/elec-hairstylers',
                  'https://www.superdrug.com/Skin/Face/c/skin-face',
                  'https://www.superdrug.com/Toiletries/Female-Hair-Removal/c/toil-hairemoval',
                  'https://www.superdrug.com/Health/Health-Monitors/Scales/c/pt_health_scales',
                  'https://www.superdrug.com/Electricals/Male-Grooming-Electricals/c/elec-grooming',
                  'https://www.superdrug.com/Mens/Shaving/c/mens-shaving',
                  'https://www.superdrug.com/Toiletries/Dental/c/toil-dental',
                  'https://www.superdrug.com/Electricals/Beauty-Electricals/c/beauty-electricals']

    bv_base_params = {'passkey': 'i5l22ijc8h1i27z39g9iltwo3',
                      'display_code': '10798-en_gb',
                      'content_locale': 'en_GB,en_US'}

    def start_requests(self):
        for url in self.start_urls:
            request = Request(url=url, callback=self.parse_category)
            yield request

    # Parsing categories from here no longer works as the source loads categories dynamically
    def parse(self, response):
        root_category_xpath = "//li[contains(@class, 'mega-dropdown')]"
        root_category_name_xpath = "./a/@title"

        middle_cat_xpath = ".//ul[not(@class)]"
        middle_cat_name_xpath = ".//li[contains(@class, 'sublevelonestyle')]/a/@title"
        middle_cat_url_xpath = ".//li[contains(@class, 'sublevelonestyle')]/a/@href"

        leaf_category_xpath = ".//li[not(contains(@class, 'sublevelonestyle'))]"
        leaf_name_xpath = "./a/@title"
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

                if not middle_cat_name:
                    continue

                leaf_categories = middle_cat.xpath(leaf_category_xpath)

                if not leaf_categories:
                    category_path = "%s | %s" % (root_category_name, middle_cat_name)

                    category = CategoryItem()
                    category['category_path'] = category_path
                    category_url = self.extract_xpath(middle_cat, middle_cat_url_xpath)
                    category_url = get_full_url(response, category_url)
                    category['category_url'] = category_url

                    yield category

                    category_list.append(category)

                for leaf in leaf_categories:
                    leaf_name = self.extract_xpath(leaf, leaf_name_xpath)
                    leaf_url = self.extract_xpath(leaf, leaf_url_xpath)
                    leaf_url = get_full_url(response, leaf_url)

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
        products_xpath = "//li[contains(@class, 'grid-group-item')]"
        product_url_xpath = ".//div[@class='img-holder']/a/@href"
        next_page_xpath = "(//li[contains(@class, 'next')])[1]/a/@href"

        products = response.xpath(products_xpath)
        category = response.meta.get('category', '')

        if not category:
            category_xpath = "//div[@id='breadcrumb']//a/text()"
            category_url_xpath = "//div[@id='breadcrumb']//a[last()]/@href"

            category_path = self.extract_all(response.xpath(category_xpath), separator=' | ')
            category_url = self.extract(response.xpath(category_url_xpath))
            if category_path and category_url:
                category = CategoryItem()
                category['category_path'] = category_path
                category['category_url'] = get_full_url(response, category_url)
                yield category

        if self.should_skip_category(category):
            return

        # Not a leaf category page
        if not products:
            return

        for product in products:
            product_url = self.extract(product.xpath(product_url_xpath))
            product_url = get_full_url(response, product_url)
            request = Request(product_url, callback=self.parse_product)
            request.meta['category'] = category
            yield request

        next_page_url = self.extract_xpath(response, next_page_xpath)
        if next_page_url:
            next_page_url = get_full_url(response, next_page_url)
            next_page_request = Request(next_page_url, callback=self.parse_category)
            next_page_request.meta['category'] = category
            yield next_page_request

    def parse_product(self, response):
        source_internal_id_re = r'(\d+)'

        _product = extruct_helper.product_items_from_microdata(response, response.meta['category'])
        if not _product:
            request = self._retry(response.request)
            yield request
            return

        product = _product.get('product')
        product_ids = _product.get('product_ids', [])

        if not (product and product_ids):
            self.logger.info("Could not scrape product at %s" % response.url)
            return

        # unfortunately, we need to clean up the source_internal_id for this source
        match = re.search(source_internal_id_re, product['source_internal_id'])
        if match:
            product['source_internal_id'] = match.group(1)

        for product_id in product_ids:
            product_id['source_internal_id'] = product['source_internal_id']
            if product_id['ID_kind'] == 'sku':
                match = re.search(source_internal_id_re, product_id['ID_value'])
                if match:
                    product_id['ID_value'] = match.group(1)
            yield product_id

        bv_id = product['source_internal_id']

        if product['ProductName'] and product['source_internal_id'] and bv_id:
            yield product

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
