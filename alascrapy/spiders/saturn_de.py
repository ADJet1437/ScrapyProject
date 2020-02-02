import alascrapy.lib.dao.incremental_scraping as incremental_utils

from scrapy.http import Request
from alascrapy.spiders.base_spiders.bazaarvoice_spiderAPI5_5 import BazaarVoiceSpiderAPI5_5
from alascrapy.items import CategoryItem,ProductItem
from alascrapy.lib.generic import get_full_url

import alascrapy.lib.extruct_helper as extruct_helper

class SaturnDeSpiderOptim(BazaarVoiceSpiderAPI5_5):
    name = 'saturn_de'
    start_urls = ['http://www.saturn.de/']
    download_delay=2.2
    bv_base_params = {'passkey': 'caVjMvXb3K6LO7C2wVCIJKTjJrDJWgT8khuQFINExZvO0',
                      'display_code': '13072-de_DE',
                      'content_locale': 'de_DE'}

    def parse(self, response):
        categories_xpath = "//li[contains(@class, 'site-navigation2__child-item') and (@data-nav-level = 'level 2')]" \
                             "/a[contains(@href,'category')]/@href"
        category_urls = self.extract_list(response.xpath(categories_xpath))
        for category_url in category_urls:
            category_url = get_full_url(response, category_url)
            request = Request(category_url, callback=self.parse_product_list)
            yield request

    def parse_product_list(self, response):
        category = response.meta.get('category', None)
        if not category:
            category_path_xpath = "//ul[@class='breadcrumbs']/li[position() != 1 and position() < last()]/a/text()"
            category_leaf_xpath = "//ul[@class='breadcrumbs']/li[last()]/text()"
            category = CategoryItem()
            category['category_url'] = response.url
            category['category_leaf'] = self.extract(
                    response.xpath(category_leaf_xpath))
            category['category_path'] = self.extract_all(response.xpath(category_path_xpath), separator=' | ')
            category['category_path'] = '%s | %s' % (category['category_path'],
                                                 category['category_leaf'])
            yield category

        if self.should_skip_category(category):
            return

        next_page_url_xpath = "//a[@rel='next']/@href"
        products_xpath = "//ul[@class='products-list']/li"
        product_url_xpath = "..//div[@class='product-wrapper']//h2/a/@href"
        products = response.xpath(products_xpath)
        for product in products:
            product_url = self.extract_xpath(product, product_url_xpath)
            product_url = get_full_url(response, product_url)
            request = Request(product_url, callback=self.parse_product)
            request.meta['category'] = category
            yield request

        next_page_url = self.extract_xpath(response, next_page_url_xpath)
        if next_page_url:
            next_page_url = get_full_url(response, next_page_url)
            request = Request(next_page_url, callback=self.parse_product_list)
            request.meta['category'] = category
            yield request

    def parse_product(self, response):
        items = extruct_helper.get_microdata_extruct_items(response.body_as_unicode())
        category = response.meta['category']
        product = list(extruct_helper.get_products_microdata_extruct(items, response, category))
        if len(product) != 1:
            raise Exception("Could not extract product in %s" % response.url)
        product_dict = product[0]
        product = product_dict['product']
        product['ProductManufacturer'] = self.extract(response.xpath("//meta[contains(@property, 'product:brand')]/@content"))
        yield product

        for product_id in product_dict['product_ids']:
            yield product_id

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