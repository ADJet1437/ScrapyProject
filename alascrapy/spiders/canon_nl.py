
# -*- coding: utf8 -*-

__author__ = 'liu'

from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_sitemap_spider import AlaSitemapSpider
from alascrapy.spiders.base_spiders.bazaarvoice_spiderAPI5_5 import BazaarVoiceSpiderAPI5_5
from alascrapy.lib.generic import get_full_url
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import CategoryItem, ProductIdItem


class CanonNlSpider(AlaSitemapSpider, BazaarVoiceSpiderAPI5_5):
    name = 'canon_nl'
    # core setup for using sitemap scrapying
    sitemap_urls = ['https://www.canon.nl/sitemap.xml']
    sitemap_rules = [('/product_finder/', 'parse_product'),
                     ('//www.canon.nl/printers/', 'parse_product'),
                     ('//www.canon.nl/cameras/', 'parse_product'),
                     ('//www.canon.nl/scanners/', 'parse_product'),
                     ]

    # core setup for using bazzarvoice data
    bv_base_params = {'passkey': 'tsvlsbctitvzy6hhyik3zno77',
                      'display_code': '18238-nl_nl',
                      'content_locale': 'nl_BE,nl_NL'}

    def parse_product(self, response):
        # sku
        # --------------------------------------------------------------------
        sku_xpath = "//meta[@name='Product-Article-Number']/@content"
        sku = self.extract_xpath(response, sku_xpath)
        if not sku:
            # not a product page
            return

        # set up product item
        # --------------------------------------------------------------------
        product_xpaths = {
                "ProductName": "//meta[@name='productName']/@content",
                "OriginalCategoryName": "//meta[@name='Product-Sub-Category']/@content",
                }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['source_internal_id'] = sku
        # all products are from canon.nl
        product['ProductManufacturer'] = 'Canon'

        # product picture
        # --------------------------------------------------------------------
        pic_url_xpath = "//meta[@name='Product-Image-Large']/@content"
        pic_url_xpath_alt = "//meta[@name='Product-Image-Small']/@content"
        # only got a relative url from Xptah
        pic_url = self.extract(response.xpath(pic_url_xpath))
        if not pic_url:
            pic_url = self.extract(response.xpath(pic_url_xpath_alt))
            print('got pic_url')
        product['PicURL'] = get_full_url(response, pic_url)

        # double check product name
        # --------------------------------------------------------------------
        product_name = product.get('ProductName')
        if not product_name:
            product_name_xpath = "//meta[@name='og:title']/@content"
            product_name = self.extract(response.xpath(product_name_xpath))
            if product_name:
                product['ProductName'] = product_name

        # double check OriginalCategoryName
        # --------------------------------------------------------------------
        original_category = product.get('OriginalCategoryName')
        if not original_category:
            '''
            a typical canon.nl product page has category names in their url
            for example:
                https://www.canon.nl/for_home/product_finder/printers/laser/i-sensys_lbp7750cdn/
                where the last item seperated by '/' is the actual product
                and the two items before the last two
                are helpful for our category matching
            '''
            sep = '|'
            start_category_ind = -4
            end_category_ind = -2
            all_category_names = sep.join(
                response.url.split('/')[start_category_ind:end_category_ind]
                 )
            product['OriginalCategoryName'] = all_category_names

        # set up category item
        # --------------------------------------------------------------------
        if product.get('OriginalCategoryName', ''):
            category = CategoryItem()
            category['category_path'] = product['OriginalCategoryName']
            yield category

        # set up product_id item
        # --------------------------------------------------------------------
        product_id = ProductIdItem()
        product_id['source_internal_id'] = product['source_internal_id']
        product_id['ProductName'] = product['ProductName']
        product_id['ID_kind'] = 'canon_id'
        product_id['ID_value'] = product['source_internal_id']
        yield product_id
        yield product

        # set up for bv review
        # --------------------------------------------------------------------
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
