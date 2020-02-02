#!/usr/bin/env python

"""gsmarena Spider: """

__author__ = 'leonardo'

import re

from scrapy.http import Request

from alascrapy.items import ProductItem, ProductIdItem
from alascrapy.lib.generic import get_full_url
from alascrapy.spiders.base_spiders.ala_crawl import AlaSpider


class GsmArenaProductsSpider(AlaSpider):
    name = 'gsmarena_products'
    allowed_domains = ['gsmarena.com']
    start_urls = [
        'http://www.gsmarena.com/results.php3?sQuickSearch=yes&sName=watch']

    manufacturer_re = re.compile('(.*) phones')
    source_internal_id_re = re.compile("-([^-]+).php")

    def parse(self, response):
        product_url_xpath = "//*[@class='makers']/ul/li//a/@href"
        product_urls = self.extract_list(response.xpath(product_url_xpath))
        watches_sii = {}
        for product_url in product_urls:
            match = re.search(self.source_internal_id_re, product_url)
            if match:
                sii = match.group(1)
                watches_sii[sii] = product_url

        brand_list_url = 'http://www.gsmarena.com/makers.php3'
        request = Request(brand_list_url, callback=self.parse_brands)
        request.meta['watches_sii'] = watches_sii
        yield request

    def parse_brands(self, response):
        brand_link_xpath = "//div[@class='st-text']//tr/td/a[text()]/@href"
        brand_links = self.extract_list(response.xpath(brand_link_xpath))
        for brand_link in brand_links:
            brand_link = get_full_url(response, brand_link)
            request = Request(brand_link, callback=self.parse_category)
            request.meta['watches_sii'] = response.meta['watches_sii']
            yield request

    def parse_category(self, response):
        manufacturer_text_xpath = "//h1[@class='article-info-name']/text()"
        manufacturer_text = self.extract(
            response.xpath(manufacturer_text_xpath))
        match = re.match(self.manufacturer_re, manufacturer_text)
        if match:
            manufacturer = match.group(1)
        else:
            raise Exception("Could not extract Manufacturer")

        product_url_xpath = "//*[@class='makers']/ul/li//a/@href"
        product_urls = self.extract_list(response.xpath(product_url_xpath))
        for product_url in product_urls:
            product_url = get_full_url(response, product_url)
            request = Request(product_url, callback=self.parse_product)
            request.meta['manufacturer'] = manufacturer
            request.meta['watches_sii'] = response.meta['watches_sii']
            yield request

    def parse_product(self, response):
        manufacturer = response.meta['manufacturer']
        watches_sii = response.meta['watches_sii']
        product = ProductItem()

        product_name_xpath = "//h1[@class='specs-phone-name-title']/text()"
        pic_url_xpath = "//div[@class='specs-photo-main']//img/@src"
        description_xpath = "//*[@name='Description']/@content"
        # Just in case they realize they got the standard wrong...
        description_xpath_alt = "//*[@name='description']/@content"

        description = self.extract(response.xpath(description_xpath))
        if not description:
            description = self.extract(response.xpath(description_xpath_alt))

        product['TestUrl'] = response.url
        product['ProductName'] = self.extract(
            response.xpath(product_name_xpath))
        product['PicURL'] = self.extract(response.xpath(pic_url_xpath))
        product['ProductManufacturer'] = manufacturer
        match = re.search(self.source_internal_id_re, response.url)
        if match:
            product['source_internal_id'] = match.group(1)

        ocn = None

        if " phone." in description:
            ocn = "Phones"
        if " smartphone." in description:
            ocn = "Smartphones"
        if " tablet." in description:
            ocn = "Tablets"

        if product['source_internal_id'] in watches_sii:
            ocn = "Smartwatches"

        product['OriginalCategoryName'] = ocn

        gsmarena_kind = ProductIdItem()
        gsmarena_kind['source_internal_id'] = product["source_internal_id"]
        gsmarena_kind['ProductName'] = product["ProductName"]
        gsmarena_kind['ID_kind'] = "gsmarena_id"
        gsmarena_kind['ID_value'] = product["source_internal_id"]
        yield gsmarena_kind

        # add needed spec.s
        # --------------------------------------------------------------------------------
        kinds_xpath = {
            'screen_size': '//td[@data-spec="displaysize"]/text()',
            'screen_resolution': '//td[@data-spec="displayresolution"]/text()',
            'main_camera_resolution': '(//td[@data-spec="cam1modules"]/text())[1]',
            'first_publish_date': '//span[@data-spec="released-hl"]/text()',
            'operating_system': '//span[@data-spec="os-hl"]//text()',
            'weight': '//td[@data-spec="weight"]//text()',
        }

        kinds = {}
        for kind, xpath in kinds_xpath.iteritems():
            val = self.extract_xpath(response, xpath)
            if val:
                kinds[kind] = val

        # publish date: Released 2018, Sept
        date = kinds.get('first_publish_date', '')
        if date and 'Released' in date:
            date_formatted = date.split('Released')[1].strip()
            kinds['first_publish_date'] = date_formatted

        for ID_kind, val in kinds.iteritems():
            yield ProductIdItem.from_product(
                product,
                kind=ID_kind,
                value=val
            )

        alt_names = []
        alt_names_xpath = "(//*[@id='specs-list']/p)[1]/text()"
        alt_names_raw = self.extract_list(response.xpath(alt_names_xpath))

        alt_names_re1 = "Available as:"
        alt_names_re2 = "Also known as:"
        alt_names_re3 = "Also known as (.*)"

        if alt_names_raw:
            first_line = alt_names_raw[0]
            if re.search(alt_names_re1, first_line) or \
                    re.search(alt_names_re2, first_line):
                alt_names = alt_names_raw[1:]
            else:
                for line in alt_names_raw:
                    match = re.search(alt_names_re3, line)
                    if match:
                        alt_names = match.group(1).split(",")
                        break

            for name in alt_names:
                product['ProductName'] = product['ProductName'] + \
                    " / " + name.strip()
        yield product
