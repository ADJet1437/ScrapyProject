__author__ = 'leonardo'
import re
import json

from scrapy.http import Request

from alascrapy.spiders.reevoo_com import ReevooComSpider
from alascrapy.items import ReviewItem
from alascrapy.lib.generic import get_full_url, date_format, dateparser

import alascrapy.lib.extruct_helper as extruct_helper


class CurrysUKSpider(ReevooComSpider):
    name = 'currys_co_uk'
    allowed_domains = ['currys.co.uk', 'reevoo.com']
    start_urls = ['http://www.currys.co.uk/gb/uk/navbardesktop/sMenuIds/621-622-623-641-624-642-643-625-626/ajax.html']
    review_url_format = 'https://mark.reevoo.com/reevoomark/en-GB/product.html?sku={}&tab=reviews&sort_by=recent&trkref=CYS&per_page=30'

    reevoo_review_id_re = re.compile("-(\d+)-pdt.html$")

    def parse_cat_json(self, response_url, json_cat_list):
        for category in json_cat_list:
            category_name = category.get('label', '').lower()
            if not category_name or 'shop by ' in category_name or 'learn more ' in category_name or \
                'clearance' in category_name or 'services' in category_name:
                return
            next_levels = category.get('nav', [])
            if next_levels:
                if isinstance(next_levels[0], list):
                    for next_level in next_levels:
                        for item in self.parse_cat_json(response_url, next_level):
                            yield item
                else:
                    for item in self.parse_cat_json(response_url, next_levels):
                        yield item
            else:
                category_url = category.get('link', '')
                if category_url:
                    category_url = get_full_url(response_url, category_url)
                    request = Request(url=category_url, callback=self.parse_category)
                    yield request

    def parse(self, response):
        json_cat_list = json.loads(response.text)
        for item in self.parse_cat_json(response.url, json_cat_list):
            yield item

    def parse_category(self, response):
        products_xpath = "//div[@data-component='product-list-view']/article/div[@class='desc']"
        next_page_xpath = "//a[@class='next']/@href"

        product_url_xpath = "./a/@href"
        has_review_xpath = ".//*[contains(@class, 'reevoo-score')]"

        products = response.xpath(products_xpath)
        if not products:
            return

        # This category may be too general, but it helps if we know it can be skipped
        category_json_ld = extruct_helper.extract_json_ld(response.body, 'BreadcrumbList')
        if category_json_ld:
            category = extruct_helper.category_item_from_breadcrumbs_json_ld(category_json_ld)
            yield category
            if self.should_skip_category(category):
                return

        for product in products:
            has_review = product.xpath(has_review_xpath)
            if not has_review:
                continue
            product_url = self.extract(product.xpath(product_url_xpath))
            request = Request(url=get_full_url(response, product_url), callback=self.parse_product)
            yield request

        next_page_url = self.extract(response.xpath(next_page_xpath))
        if next_page_url:
            next_page_url = get_full_url(response, next_page_url)
            request = Request(next_page_url, callback=self.parse_category)
            yield request

    def parse_product(self, response):
        # The category names extracted in category pages are not very detailed,
        # extract it in product page instead
        category = ''
        category_json_ld = extruct_helper.extract_json_ld(response.body, 'BreadcrumbList')
        if category_json_ld:
            category = extruct_helper.category_item_from_breadcrumbs_json_ld(category_json_ld)
            yield category
            if self.should_skip_category(category):
                return
        # TODO: retry if we fail to get JSON-LD?

        sku = ''
        product_json_ld = extruct_helper.extract_json_ld(response.body, 'Product')
        if product_json_ld:
            product = extruct_helper.product_item_from_product_json_ld(product_json_ld)
            sku = product_json_ld.get('sku', None)
        else:
            # Not sure why we fail to extract JSON-LD from some pages, it will be good if we can figure out later
            product_xpaths = {"PicURL": "(//*[@property='og:image'])[1]/@content",
                              "ProductName": "//h1[contains(@class, 'page-title')]/span//text()",
                              "ProductManufacturer": "//h1[contains(@class,'page-title')]/span[1]/text()"
                              }
            product = self.init_item_by_xpaths(response, "product", product_xpaths)

        if not sku:
            sku_xpath = "//p[@class='prd-code']/text()"
            sku = self.extract(response.xpath(sku_xpath))
            if sku:
                splitted = sku.split(': ')
                if splitted:
                    sku = splitted[-1]

        product['TestUrl'] = response.url
        if category:
            product['OriginalCategoryName'] = category['category_path']

        if sku:
            product['source_internal_id'] = sku
            product_id = self.product_id(product=product, kind='currys_internal_id', value=sku)
            yield product_id

        yield product

        reevoo_review_id = ''
        match = re.search(self.reevoo_review_id_re, response.url)
        if match:
            reevoo_review_id = match.group(1)
        if reevoo_review_id:
            # TODO: test if the url is valid or not?
            review_url = self.review_url_format.format(reevoo_review_id)
            request = Request(url=review_url, callback=self.parse_review)
            request.meta['product'] = product
            request.meta['rating_xpath'] = ".//div[@class='overall_score_stars']/@title"
            yield request
