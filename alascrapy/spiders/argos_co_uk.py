__author__ = 'jim, frank'

from scrapy.http import Request

from alascrapy.items import ProductItem, CategoryItem, ProductIdItem
from alascrapy.lib.generic import get_full_url
from alascrapy.spiders.base_spiders.bazaarvoice_spiderAPI5_5 import BazaarVoiceSpiderAPI5_5

import alascrapy.lib.dao.incremental_scraping as incremental_utils

import re


class ArgosCoUkSpider(BazaarVoiceSpiderAPI5_5):
    name = 'argos_co_uk'
    allowed_domains = ['argos.co.uk']
    start_urls = ['https://www.argos.co.uk/static/AtoZ.htm']

    bv_base_params = {}

    FULL_URL_PATTERN = 'http://www.argos.co.uk/product-api/bazaar-voice-reviews;partNumber={bv_id};' \
               'query={{"Limit":100,"Offset":{offset},"Sort":"SubmissionTime:Desc"}}?returnMeta=true'

    def parse(self, response):
        category_page_xpath = "//div[@id='atoz']/dl[ ./dt/a ]/dd/a"
        categories = response.xpath(category_page_xpath)
        for category in categories:
            category_name = self.extract_xpath(category, './text()')
            category_url = get_full_url(response, self.extract_xpath(category, './@href'))
            if category_name and category_url:
                category_item = CategoryItem()
                category_item["category_leaf"] = category_name
                category_item["category_path"] = category_name
                category_item["category_url"] = category_url
                yield category_item

                if self.should_skip_category(category_item):
                    continue

                request = Request(category_url, callback=self.parse_category)
                request.meta['OriginalCategoryName'] = category_name
                yield request

    def parse_category(self, response):
        product_url_xpath = "//a[@data-product-name]/@href"
        next_page_xpath = "(//*[@rel='next'])[1]/@href"

        product_urls = self.extract_list_xpath(response, product_url_xpath)
        category_name = response.meta.get('OriginalCategoryName', '')

        # Not a leaf category page or something wrong with getting category name
        if not product_urls or not category_name:
            return

        for product_url in product_urls:
            product_url = get_full_url(response, product_url)
            request = Request(product_url, callback=self.parse_product)
            request.meta['OriginalCategoryName'] = category_name
            yield request

        next_page_url = self.extract_xpath(response, next_page_xpath)
        if next_page_url:
            next_page_url = get_full_url(response, next_page_url)
            next_page_request = Request(next_page_url, callback=self.parse_category)
            next_page_request.meta['OriginalCategoryName'] = category_name
            yield next_page_request

    def parse_product(self, response):
        mobile_xpath = "//*[@id='mobile_content_bar']"
        mobile = response.xpath(mobile_xpath)
        canonical_url_xpath = "//link[@rel='canonical']/@href"
        if mobile:
            canonical_url = self.extract(response.xpath(canonical_url_xpath))
            request = Request(url=canonical_url, callback=self.parse_product)
            request.meta['category'] = response.meta['category']
            request.meta['review_url'] = response.meta['review_url']
            yield request
            return

        pic_url_xpath = '//img[contains(@class,"s7carousel-main-image-slide-vertical")][1]/@src'
        product_name_xpath = "//div[@class='product-name']//span[@itemprop='name']/text()"
        product_name_alt_xpath = "//div[@id='pdpProduct']/h1/text()"
        product_id_xpath = "//*[@itemprop='sku']/text()"
        #product_id_alt_xpath = "//span[contains(@class,'partnumber')]/text()"
        manufacturer_xpath = "//*[@itemprop='brand']/text()"

        product = ProductItem()
        product['TestUrl'] = response.url
        product['OriginalCategoryName'] = response.meta['OriginalCategoryName']
        product['source_internal_id'] = self.extract(response.xpath(product_id_xpath))
        product['ProductName'] = self.extract(response.xpath(product_name_xpath))
        product['ProductManufacturer'] = self.extract(response.xpath(manufacturer_xpath))
        product['PicURL'] = self.extract(response.xpath(pic_url_xpath))

        if not product['ProductName']:
            product['ProductName'] = self.extract(response.xpath(product_name_alt_xpath))

        # the id from alt_xpath is different from the default xpath, do not use it
        # if not product['source_internal_id']:
        #    product['source_internal_id'] = self.extract(response.xpath(product_id_alt_xpath))

        bv_id = ''
        bv_id_re = r'product/([0-9]+)$'
        bv_id_match = re.search(bv_id_re, response.url, re.I)
        if bv_id_match:
            bv_id = bv_id_match.group(1)

        if product['ProductName'] and product['source_internal_id'] and bv_id:
            yield product

            product_id = self.product_id(product)
            product_id['ID_kind'] = "argos_uk_id"
            product_id['ID_value'] = product['source_internal_id']
            yield product_id

            review_url = self.get_review_url(bv_id=bv_id, offset=0)
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
