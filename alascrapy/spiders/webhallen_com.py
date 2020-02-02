#!/usr/bin/env python

import re

from scrapy.http import Request
from scrapy.selector import Selector

from alascrapy.items import ProductItem, ProductIdItem, ReviewItem, CategoryItem
from alascrapy.lib.generic import get_full_url, abbreviate_month, date_format, unescape_js_string
from alascrapy.spiders.base_spiders.ala_crawl import AlaSpider

import alascrapy.lib.dao.incremental_scraping as incremental_utils

class WebhallenSpider(AlaSpider):
    name = 'webhallen_com'
    custom_settings = {'COOKIES_ENABLED': True}

    start_urls = ['https://www.webhallen.com/se-sv/mobilt/telefoner/alla_mobiltelefoner/',
                  'https://www.webhallen.com/se-sv/ljud_och_bild/horlurar/alla_horlurar/',
                  'https://www.webhallen.com/se-sv/datorer_och_tillbehor/surfplattor/alla_surfplattor/',
                  'https://www.webhallen.com/se-sv/datorer_och_tillbehor/barbara_datorer/alla_barbara_datorer/',
                  'https://www.webhallen.com/se-sv/datorer_och_tillbehor/stationara_datorer/alla_stationara_datorer/',
                  'https://www.webhallen.com/se-sv/mobilt/smartklockor/alla_smartklockor/',
                  'https://www.webhallen.com/se-sv/datorer_och_tillbehor/bildskarmar/alla_bildskarmar/',
                  'https://www.webhallen.com/se-sv/lek_och_gadgets/dronare-quadcopters/dronare/',
                  'https://www.webhallen.com/se-sv/mobilt/smartbands-aktivitetstrackers/alla_smartbands/',
                  'https://www.webhallen.com/se-sv/ljud_och_bild/blu-ray-dvd-spelare/',
                  'https://www.webhallen.com/se-sv/datorkomponenter/virtual_reality_vr/'
                  'https://www.webhallen.com/se-sv/ljud_och_bild/tv/alla_tv-apparater/',
                  'https://www.webhallen.com/se-sv/hem_och_halsa/dammsugare/',
                  'https://www.webhallen.com/se-sv/hem_och_halsa/kaffemaskiner/',
                  'https://www.webhallen.com/se-sv/natverk_och_smarta_hem/smarta_hem/'
                  ]

    headers = {'Referer': '*/*',
               'Accept-Encoding': 'gzip, deflate, sdch, br',
               'Accept-Language': 'en-US,en;q=0.8',
               'Cache-Control': 'no-cache',
               'Connection': 'keep-alive',
               'Pragma': 'no-cache',
               'Host': 'www.webhallen.com'}

    def parse(self, response):
        product_url_xpath = "//tr[@class='prod_list_row']//td[not(@*)]/a/@href"
        category_url_xpath = "//div[contains(@class, 'list_block_item')]/span/a/@href"
        product_urls = self.extract_list(response.xpath(product_url_xpath))
        category_urls = self.extract_list(response.xpath(category_url_xpath))

        if product_urls:
            # A page containing products, e.g. all cell phones
            for product_url in product_urls:
                product_url = get_full_url(response, product_url)
                request = Request(product_url, callback=self.parse_product)
                yield request

            next_page_xpath = "//span[@class='next']/a/@href"
            next_page = self.extract(response.xpath(next_page_xpath))
            if next_page:
                next_page = get_full_url(response, next_page)
                request = Request(next_page, callback=self.parse)
                yield request
        elif category_urls:
            # A page containing all sub-categories of a type of product
            for category_url in category_urls:
                category_url = get_full_url(response, category_url)
                request = Request(category_url, callback=self.parse)
                yield request
        else:
            # Failed
            request = self._retry(response.request)
            yield request
            return

    def parse_product(self, response):
        product = ProductItem()

        sii_xpath = "//div[@class='nosto_product']/span[@class='product_id']/text()"
        product_name_xpath = "//div[@class='nosto_product']/span[@class='name']/text()"
        ocn_xpath = "//div[@class='nosto_product']/span[@class='category']/text()"
        category_url_xpath = "//li[@class='current_level']/a/@href"
        pic_url_xpath = "//div[@class='nosto_product']/span[@class='image_url']/text()"
        manufacturer_xpath = "//td[@class='prod_spec_key' and contains(text(),'Utvecklare')]/following-sibling::td//text()"

        product['TestUrl'] = response.url
        product['ProductName'] = self.extract(response.xpath(product_name_xpath))

        if not product['ProductName']: #blocked
            request = self._retry(response.request)
            yield request
            return

        category = CategoryItem()
        category_name = self.extract(response.xpath(ocn_xpath))
        category_partial_url = self.extract(response.xpath(category_url_xpath))

        if category_partial_url:
            category['category_url'] = get_full_url('https://www.webhallen.com', category_partial_url)
            category['category_leaf'] = category_name
            category['category_path'] = category_name
            yield category

        product['PicURL'] = self.extract(response.xpath(pic_url_xpath))
        product['ProductManufacturer'] = self.extract(response.xpath(manufacturer_xpath))
        product['OriginalCategoryName'] = category_name
        product['source_internal_id'] = self.extract(response.xpath(sii_xpath))
        yield product

        webhallen_internal = ProductIdItem()

        webhallen_internal['source_internal_id'] = product['source_internal_id']
        webhallen_internal['ProductName'] = product['ProductName']
        webhallen_internal['ID_kind'] = "webhallen_se_id"
        webhallen_internal['ID_value'] = product['source_internal_id']
        yield webhallen_internal

        webhallen_mpn = ProductIdItem()

        mpn_xpath = "//td[@class='prod_spec_key' and contains(text(),'Tillv. artikelnr')]/following-sibling::td//text()"
        webhallen_mpn['source_internal_id'] = product['source_internal_id']
        webhallen_mpn['ProductName'] = product['ProductName']
        webhallen_mpn['ID_kind'] = "MPN"
        webhallen_mpn['ID_value'] = self.extract(response.xpath(mpn_xpath))
        if webhallen_mpn['ID_value'] != '':
            yield webhallen_mpn

        review_link = "https://www.webhallen.com/prod.php?tab=reviews&id=%s" % product["source_internal_id"]
        self.headers['Referer'] = response.url
        request = Request(review_link, callback=self.parse_review, headers=self.headers)
        request.meta['product'] = product
        yield request

    def parse_review(self, response):
        product = response.meta['product']

        testSummary_xpath = ".//div[@class='review-text']/p/text()"
        author_xpath = ".//span[@class='review-created-by']/text()"
        testDateText_xpath = ".//span[@class='review-created-at']/text()"
        sourceTestRating_xpath = ".//span[@class='review-rating']/img/@src"

        # Remove all unnecessary backslashes in response body, which are used to escape characters in JavaScript
        response_body_escaped = unescape_js_string(response.body)
        review_html_regex = '(<div class="reviews">.*)<div class="add-review">'

        review_html_match = re.search(review_html_regex, response_body_escaped)
        if not review_html_match:
            #self.logger.error('Webhallen review html match failed')
            return

        review_html = review_html_match.group(1)
        selector = Selector(text=review_html)

        divs = selector.xpath("//div[@class='reviews']")

        for div in divs.xpath("./div"):
            review = ReviewItem()
            self.set_product(review, product)

            extracted_date = self.extract(div.xpath(testDateText_xpath))
            date_with_abbrev_month = abbreviate_month(extracted_date)
            review["TestDateText"] = date_format(date_with_abbrev_month, "%d %B %Y")

            review["DBaseCategoryName"] = "USER"
            review["SourceTestScale"] = "5"
            review["TestTitle"] = product['ProductName']
            review["TestSummary"] = self.extract(div.xpath(testSummary_xpath))
            review["Author"] = self.extract(div.xpath(author_xpath))

            review["SourceTestRating"] = self.extract(div.xpath(sourceTestRating_xpath))
            if review["SourceTestRating"]:
                review["SourceTestRating"] = self.clear_score(review["SourceTestRating"])

            if review["Author"]:
                yield review

    def clear_score(self, score):
        score = score[-5]
        return score
