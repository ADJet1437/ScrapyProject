# -*- coding: utf8 -*-

import re
from datetime import datetime

from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import date_format, get_full_url

from alascrapy.items import ProductIdItem


class maistecnologiaSpider(AlaSpider):
    name = 'maistecnologia_com'
    allowed_domains = ['maistecnologia.com']
    start_urls = ['https://www.maistecnologia.com/tecnologia/analises-tecnologia/']

    def parse(self, response):

        review_urls_xpath = "//div[contains(@class, 'td-ss-main-content')]//*[contains(@class, 'td-module-title')]/a/@href"
        next_page_xpath = "//div[contains(@class, 'page-nav')]/a[i/@class='td-icon-menu-right']/@href"

        review_urls = self.extract_list(response.xpath(review_urls_xpath))

        for review_url in review_urls:
            review_url = get_full_url(response, review_url)
            request = Request(review_url, callback=self.parse_review)
            yield request

        next_page_url = self.extract_xpath(response, next_page_xpath)
        if next_page_url:
            next_page_url = get_full_url(response, next_page_url)
            next_page_request = Request(next_page_url, callback=self.parse)
            yield next_page_request

    def parse_review(self, response):

        internal_id_xpath = '//article[1]/@id'
        internal_id_re = r'post-(.*)'

        product_xpaths = {"PicURL": "//meta[@property='og:image'][1]/@content",
                          "ProductName": "//h2[contains(., 'Veredito:') or "
                                         "contains(., 'VEREDITO:') or "
                                         "contains(., 'Veredicto:') or "
                                         "contains(., 'VEREDICTO:')][1]//text()",
                         }

        review_xpaths = { "TestTitle": "//meta[@property='og:title']/@content",
                          "TestSummary": "//meta[@property='og:description']/@content",
                          "Author": "//meta[@name='author'][1]/@content",
                          "TestDateText": "//meta[@property='article:published_time']/@content",
                          "TestVerdict": "//h2[contains(., 'Veredito') or "
                                         "contains(., 'VEREDITO') or "
                                         "contains(., 'Veredicto') or "
                                         "contains(., 'VEREDICTO')]/following::p[1]//text()"
                        }

        # some of the lists of pros and cons are formatted, e.g. italic, so we cannot use li//text() here
        pros_element_xpath = '''//p[contains(., 'Pontos a Favor') or 
                                    contains(., 'Pontos a favor') or 
                                    contains(., 'Pontos Positivos') or 
                                    contains(., 'Pontos positivos') or 
                                    contains(., 'Pontos fortes')]/following-sibling::ul[1]/li'''

        cons_element_xpath = '''//p[contains(., 'Pontos Contra') or 
                                    contains(., 'Pontos contra') or 
                                    contains(., 'Pontos Negativos') or 
                                    contains(., 'Pontos negativos') or 
                                    contains(., 'Pontos fracos')]/following-sibling::ul[1]/li'''

        product_name_re = r'Veredito:\s+(.*)'
        product_name_re_2 = r'Veredicto:\s+(.*)'
        product_image_alt_xpath = "//div[@class='td-post-content']/img[1]/@src"
        date_alt_xpath = "//div[contains(@class, 'td-ss-main-content')]//div[@class='td-post-title']/time[1]/@datetime"

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        if product["ProductName"]:
            matched_name = re.search(product_name_re, product["ProductName"], re.I)
            if matched_name:
                product["ProductName"] = matched_name.group(1)
            else:
                matched_name = re.search(product_name_re_2, product["ProductName"], re.I)
                if matched_name:
                    product["ProductName"] = matched_name.group(1)

        else:
            product["ProductName"] = review["TestTitle"]

        if not product["PicURL"]:
            product["PicURL"] = self.extract_xpath(response, product_image_alt_xpath)

        if not review["TestDateText"]:
            review["TestDateText"] = self.extract_xpath(response, date_alt_xpath)

        # TODO: write a function for collecting pros and cons that are specially formatted?
        pro_str = ''
        con_str = ''
        pro_elements = response.xpath(pros_element_xpath)
        for pro_element in pro_elements:
            pro = self.extract_all(pro_element.xpath('.//text()'))
            pro = pro.strip(';.')
            pro_str += pro + ' ; '
        pro_str = pro_str.strip(' ;')

        con_elements = response.xpath(cons_element_xpath)
        for con_element in con_elements:
            con = self.extract_all(con_element.xpath('.//text()'))
            con = con.strip(';.')
            con_str += con + ' ; '
        con_str = con_str.strip(' ;')

        review["TestPros"] = pro_str
        review["TestCons"] = con_str

        internal_id = self.extract_xpath(response, internal_id_xpath)
        if internal_id:
            matched_id = re.search(internal_id_re, internal_id)
            if matched_id:
                internal_id = matched_id.group(1)

            product_id = ProductIdItem()
            product_id['ProductName'] = product["ProductName"]
            product_id['source_internal_id'] = internal_id
            product_id['ID_kind'] = 'maistecnologia_com_internal_id'
            product_id['ID_value'] = internal_id

            product['source_internal_id'] = internal_id
            review['source_internal_id'] = internal_id

            yield product_id

        yield product

        review["DBaseCategoryName"] = "PRO"
        review["ProductName"] = product["ProductName"]
        review["TestDateText"] = date_format(review["TestDateText"],
                                             "%Y-%m-%dT%H:%M")

        yield review
