# -*- coding: utf8 -*-

import re

from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url


class TelefoninoNetSpider(AlaSpider):
    name = 'telefonino_net'
    allowed_domains = ['telefonino.net']
    start_urls = ['http://www.telefonino.net/Cellulari/prove.html']

    rating_re = re.compile('(\d+)\s*/\s*(\d+)')

    def parse(self, response):
        brand_name_xpath = './text()'
        brand_url_xpath = './@href'
        brand_list_sel = response.xpath("//div[@id='links']/ul/li/a")

        for brand in brand_list_sel:
            brand_name = self.extract(brand.xpath(brand_name_xpath))
            brand_url = self.extract(brand.xpath(brand_url_xpath))
            brand_url = get_full_url(response.url, brand_url)
            request = Request(brand_url, callback=self.parse_brand_list)
            request.meta['brand']=brand_name
            yield request


    def parse_brand_list(self, response):
        review_urls_xpath = "//div[@class='listaModelli']/div/a[not(contains(text(), 'Prezzo'))]/@href"
        review_urls = self.extract_list(response.xpath(review_urls_xpath))

        next_page_xpath = "(//span[" \
                          "@class='linkPaginazione']/following-sibling::a[" \
                          "@class='linkPaginazione'])[1]/@href"

        for review_url in review_urls:
            review_url = get_full_url(response.url, review_url)
            request = Request(review_url, callback=self.parse_review)
            request.meta['brand']=response.meta['brand']
            yield request

        next_page_url = self.extract(response.xpath(next_page_xpath))
        if next_page_url:
            next_page_url = get_full_url(response.url, next_page_url)
            request = Request(next_page_url, callback=self.parse_brand_list)
            request.meta['brand']=response.meta['brand']
            yield request


    def parse_review(self, response):
        review_list_xpath = "//div[@class='contenuto']/table//span/a/@href"
        review_list = self.extract_list(response.xpath(review_list_xpath))
        if review_list:
            for review_url in review_list:
                review_url = get_full_url(response.url, review_url)
                request = Request(review_url, callback=self.parse_review)
                request.meta['brand']=response.meta['brand']
                yield request
            return

        product_xpaths = { "ProductName": "//div[@class='topbox']/h3/text()",
                           "PicURL": "//div[@id='dbmodelli_image']/img/@src"
                         }

        review_xpaths = { "TestSummary": "//div[@id='dbmodello_descrizione']//text()",
                        }

        rating_xpath = "//div[@id='dbmodello_votazione']//span/text()"

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product["PicURL"] = get_full_url(response.url, product["PicURL"])
        product["OriginalCategoryName"] = 'Cellulari'
        product["ProductManufacturer"] = response.meta['brand']

        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        review["TestTitle"] = product["ProductName"]
        review["TestUrl"] = product["TestUrl"]
        review["ProductName"] = product["ProductName"]
        review["DBaseCategoryName"] = "PRO"

        rating = self.extract_all(response.xpath(rating_xpath), separator=' ')
        if rating:
            match = re.search(self.rating_re, rating)
            if match:
                review["SourceTestRating"] = match.group(1)
                review["SourceTestScale"] = match.group(2)
        else:
            print response.url
            pass #Do nothing this only happens in older phones we do not care about

        yield product

        verdict_page_xpath = "//a[contains(@href,'pagella')]/@href"
        verdict_page = self.extract(response.xpath(verdict_page_xpath))
        if verdict_page:
            verdict_page = get_full_url(response.url, verdict_page)
            request = Request(verdict_page, callback=self.parse_review_verdict)
            request.meta['review']=review
            yield request
        else:
            yield review

    def parse_review_verdict(self, response):
        review = response.meta['review']
        verdict_xpath = "(//b[text()='VOTO GENERALE']/../following-sibling::p)[1]/text()"
        review['TestVerdict'] = self.extract(response.xpath(verdict_xpath))
        yield review



