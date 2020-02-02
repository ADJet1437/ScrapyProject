__author__ = 'frank'

from scrapy.http import Request

from alascrapy.items import ProductIdItem
from alascrapy.lib.generic import get_full_url
from alascrapy.spiders.base_spiders.bazaarvoice_spiderAPI5_5 import BazaarVoiceSpiderAPI5_5

import alascrapy.lib.extruct_helper as extruct_helper
import alascrapy.lib.dao.incremental_scraping as incremental_utils

class FeelUniqueSpider(BazaarVoiceSpiderAPI5_5):
    name = 'feelunique_com'
    locale = 'en'
    start_urls = ['http://www.feelunique.com/electricals/electricals-hair?q=&filter=fh_location=//c1/en_GB/categories%3C{c1_c1c18}/categories%3C{c1_c1c18_c1c18c1}/!exclude_countries%3E{se}/!site_exclude%3E{1}/!brand={a70}/hisandhers%3E{0;2;1}/%26fh_view_size=180%26fh_sort_by=-$rc_featured',
                  'http://www.feelunique.com/hair/hair-care-electrical?q=&filter=fh_location=//c1/en_GB/categories%3C%7bc1_c1c9%7d/categories%3C%7bc1_c1c9_c1c9c11%7d/!exclude_countries%3E%7bse%7d/!site_exclude%3E%7b1%7d/!brand%3d%7ba70%7d/hisandhers%3E%7b0%3b2%3b1%7d/%26fh_sort_by=-$rc_featured%26fh_view_size=36',
                  'http://www.feelunique.com/mens/electricals/electricals-electric-toothbrushes?q=&filter=fh_location=//c1/en_GB/categories%3C%7bc1_c1c18%7d/categories%3C%7bc1_c1c18_c1c18c6%7d/!exclude_countries%3E%7bse%7d/!site_exclude%3E%7b1%7d/!brand%3d%7ba70%7d/hisandhers%3E%7b0%3b2%3b1%7d/%26fh_sort_by=-$rc_featured%26fh_view_size=36',
                  'http://www.feelunique.com/electricals/electricals-face?q=&filter=fh_location=//c1/en_GB/categories%3C%7bc1_c1c18%7d/categories%3C%7bc1_c1c18_c1c18c2%7d/!exclude_countries%3E%7bse%7d/!site_exclude%3E%7b1%7d/!brand%3d%7ba70%7d/hisandhers%3E%7b0%3b2%3b1%7d/%26fh_sort_by=-$rc_featured%26fh_view_size=36',
                  'http://www.feelunique.com/body/hair-removal?q=&filter=fh_location=//c1/en_GB/categories%3C%7bc1_c1c5%7d/categories%3C%7bc1_c1c5_c1c5c13%7d/!exclude_countries%3E%7bse%7d/!site_exclude%3E%7b1%7d/!brand%3d%7ba70%7d/hisandhers%3E%7b0%3b2%3b1%7d/%26fh_sort_by=-$rc_featured%26fh_view_size=36',
                  'http://www.feelunique.com/body/bath-body-dental-cares%3C%7bc1_c1c5_c1c5c22%7d/!exclude_countries%3E%7bse%7d/!site_exclude%3E%7b1%7d/!brand%3d%7ba70%7d/hisandhers%3E%7b0%3b2%3b1%7d/%26fh_sort_by=-$rc_featured%26fh_view_size=36',
                  'http://www.feelunique.com/skin/skin-cleansers-cleansing-systems?q=&filter=fh_location=//c1/en_GB/categories%3C%7bc1_c1c1%7d/categories%3C%7bc1_c1c1_c1c1c2%7d/categories%3C%7bc1_c1c1_c1c1c2_c1c1c2c10%7d/!exclude_countries%3E%7bse%7d/!site_exclude%3E%7b33%7d/!brand%3d%7ba70%7d/hisandhers%3E%7b0%3b2%3b1%7d/%26fh_sort_by=-$rc_featured%26fh_view_size=36'
                  ]

    # scrape this site slower than usual, or we may get noticed by feelunique.com
    custom_settings = {
        'COOKIES_ENABLED': True,
        'DOWNLOAD_DELAY': 6,
    }

    bv_base_params = {'passkey': '3nyme34wieekt8tkoexsipmli',
                      'display_code': '17462-en_gb',
                      'content_locale': 'en_GB'}

    # We need to hard code the categories to scrape, or else feelunique.com may block us if we start from home page
    def start_requests(self):
        for url in self.start_urls:
            request = Request(url=url, callback=self.parse_category)
            yield request

    def parse(self, response):
        category_xpath = "(//ul[contains(@class, 'subnav')][position() <= 2])//li[@class='featured-categories']/div/span/a/@href"

        category_urls = self.extract_list(response.xpath(category_xpath))
        for url in category_urls:
            url = get_full_url(response, url)
            request = Request(url=url, callback=self.parse_category)
            yield request

    def parse_category(self, response):
        products_xpath = "//div[@class='Productlist']/div"
        product_sku_xpath = "./@data-sku"
        has_review_xpath = ".//span[@class='Rating-average']"
        next_page_xpath = "(//*[@rel='next'])[1]/@href"

        category = response.meta.get('category', '')
        if not category:
            # the category we get here is actually parent category
            category_json_ld = extruct_helper.extract_json_ld(response.text, 'BreadcrumbList')
            if not category_json_ld:
                request = self._retry(response.request)
                yield request
                return

            category = extruct_helper.category_item_from_breadcrumbs_json_ld(category_json_ld)
            current_category_name = self.extract(response.xpath("//div[@id='breadcrumb']/ul/li[@class='pad-left']/text()"))
            if current_category_name.lower() != category['category_leaf'].lower():
                category['category_leaf'] = current_category_name
                category['category_path'] = u'{} | {}'.format(category['category_path'], current_category_name)
                category['category_url'] = response.url

            yield category

            if self.should_skip_category(category):
                return

        products = response.xpath(products_xpath)

        # Not a leaf category page
        if not products:
            return

        # We skip the product page, as feelunique.com tries to block us if we access too many of their pages,
        # but it is impossible for them to block the access to Bazaarvoice API
        for product in products:
            has_review = product.xpath(has_review_xpath)
            if not has_review:
                continue

            product_sku = self.extract(product.xpath(product_sku_xpath))
            if product_sku:
                product_id = ProductIdItem()
                product_id['source_internal_id'] = product_sku
                product_id['ID_kind'] = 'feelunique_internal_id'
                product_id['ID_value'] = product_sku
                yield product_id

                bv_params = self.bv_base_params.copy()
                bv_params['bv_id'] = product_sku
                bv_params['offset'] = 0
                review_url = self.get_review_url(**bv_params)

                last_user_review = incremental_utils.get_latest_user_review_date_by_sii(
                    self.mysql_manager, self.spider_conf['source_id'],
                    product_sku
                )

                request = Request(review_url, callback=self.parse_reviews)
                request.meta['last_user_review'] = last_user_review
                request.meta['filter_other_sources'] = False
                request.meta['OriginalCategoryName'] = category['category_path']
                request.meta['bv_id'] = product_sku
                yield request
            else:
                product_url_xpath = "./a/@href"
                product_url = self.extract(response.xpath(product_url_xpath))
                product_url = get_full_url(response, product_url)
                self.logger.info("Failed to get SKU for product at %s" % product_url)

        next_page_url = self.extract_xpath(response, next_page_xpath)
        if next_page_url:
            next_page_url = get_full_url(response, next_page_url)
            next_page_request = Request(next_page_url, callback=self.parse_category)
            next_page_request.meta['category'] = category
            yield next_page_request
