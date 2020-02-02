import alascrapy.lib.dao.incremental_scraping as incremental_utils

from scrapy.http import Request
from alascrapy.spiders.base_spiders.bazaarvoice_spiderAPI5_5 import BazaarVoiceSpiderAPI5_5
from alascrapy.items import CategoryItem,ProductItem
from alascrapy.lib.generic import get_full_url

import alascrapy.lib.extruct_helper as extruct_helper

class EpriceItSpider(BazaarVoiceSpiderAPI5_5):
    name = 'eprice_it'
    start_urls = ['https://www.eprice.it']
    bv_base_params = {'passkey': 'cafhLFPMIhT7hiLansGQtu5wfMVOhS6RaVy0vYpin1Jm4',
                      'display_code': '17950-it_it',
                      'content_locale': 'it_IT'}

    def parse(self, response):
        categories_xpath = "//div[@id='menu']//h4//a/@href"
        category_urls = self.extract_list(response.xpath(categories_xpath))
        for category_url in category_urls:
            category_url = get_full_url(response, category_url)
            request = Request(category_url, callback=self.parse_category)
            yield request

    def parse_category(self, response):
        next_page_url_xpath = "//*[@rel='next']/@href"
        products_xpath = "//div[contains(@class, 'item') and .//*[@class='stelline']]"
        product_id_xpath = ".//*[@name='sku']/@value"
        bv_id_xpath = ".//*[@class='stelline']/@id"

        products = response.xpath(products_xpath)

        if not products:
            sub_cat_xpath = "//div[@class='box_menu']//li/a/@href"
            sub_cat_urls = self.extract_list(response.xpath(sub_cat_xpath))
            for url in sub_cat_urls:
                yield response.follow(url, callback=self.parse_category)

            return

        category = response.meta.get('category', {})
        if not category:
            category_path_xpath = "//span[@class='path']/*[@itemprop='name']//text()"
            category = CategoryItem()
            category['category_url'] = response.url
            category['category_path'] = self.extract_all(response.xpath(category_path_xpath), separator=' | ')
            yield category

        if self.should_skip_category(category):
            return

        for product in products:
            source_internal_id = self.extract(product.xpath(product_id_xpath))
            bv_id = product.xpath(bv_id_xpath).re_first(r'-([0-9]+)')
            if not (source_internal_id and bv_id):
                continue

            bv_params = self.bv_base_params.copy()
            bv_params['bv_id'] = bv_id
            bv_params['offset'] = 0
            review_url = self.get_review_url(**bv_params)

            request = Request(url=review_url, callback=self.parse_reviews)
            last_user_review = incremental_utils.get_latest_user_review_date_by_sii(
                self.mysql_manager, self.spider_conf['source_id'],
                source_internal_id
            )
            request.meta['last_user_review'] = last_user_review
            request.meta['bv_id'] = bv_id
            request.meta['product_id'] = source_internal_id
            request.meta['OriginalCategoryName'] = category.get('category_path')

            request.meta['filter_other_sources'] = False

            yield request

        next_page_url = self.extract_xpath(response, next_page_url_xpath)
        if next_page_url:
            next_page_url = get_full_url(response, next_page_url)
            request = Request(next_page_url, callback=self.parse_category)
            request.meta['category'] = category
            yield request
