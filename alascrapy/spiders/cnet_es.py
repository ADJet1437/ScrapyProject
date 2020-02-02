# -*- coding: utf8 -*-
import re

import alascrapy.lib.extruct_helper as extruct_helper
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.items import ProductIdItem

TESTSCALE = 10


class CnetESSpider(AlaSpider):
    name = 'cnet_es'
    allowed_domains = ['cnet.com']
    start_urls = ['https://www.cnet.com/es/analisis/']

    def parse(self, response):  
        review_urls_xpath = "//a[@class='assetHed'][not(contains("\
            "@href,'videos'))]/@href"
        review_urls = self.extract_list(response.xpath(review_urls_xpath))
        next_page_xpath = "//a[@class='next']/@href"

        for review_url in review_urls:
            yield response.follow(review_url,
                                  callback=self.parse_review_product)

        next_page = self.extract(response.xpath(next_page_xpath))
        if next_page:
            yield response.follow(next_page,
                                  callback=self.parse)

    def get_product_name(self, response):
        # example of response.url
        # https://www.cnet.com/es/analisis/bose-wireless-noise-masking-sleepbuds/primer-vistazo/
        url = response.url
        url_parsed = url.split('/')
        PRODUCT_INDEX = 5
        productname = url_parsed[PRODUCT_INDEX]
        return productname.replace('-', ' ').replace('review', '')

    def get_source_internal_id(self, response):
        body = response.text
        pattern = '"mfr":"[^"]*","productId":"([^"]*)"'
        match = re.findall(pattern, body)
        sid = ''

        if match:
            sid = match[0]

        return sid

    def parse_price(self, product, response):
        price_xpath = "//div[@class='price']/a/text()|"\
            "//a[@class='price']/text()|"\
            "//span[@class='msrp']/text()"
        price_str = self.extract(response.xpath(price_xpath))

        if price_str:
            return ProductIdItem.from_product(
                product,
                kind='price',
                value=price_str
            )

    def parse_review_product(self, response):

        product_xpaths = {
            "PicURL": '//meta[@property="og:image"][1]/@content'
        }

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['ProductName'] = self.get_product_name(response)
        sid = self.get_source_internal_id(response)
        if sid:
            product['source_internal_id'] = sid

        original_category_name_xpath = "//a[@section='topic']/text()|"\
            "//ul[@class='breadcrumb']/li[position()>1 and position()<last()]/a/text()"
        original_category_name = self.extract_all(
            response.xpath(original_category_name_xpath), " | ")
        if original_category_name:
            product["OriginalCategoryName"] = original_category_name

        yield product

        review_xpaths = {
            'source_internal_id': "substring-after(//script["
            "@type='text/javascript']/text(),'print/')",
            "TestSummary": '//meta[@property="og:description"]/@content',
            "Author": "//a[@rel='author']/span/text()",
            "TestTitle": '//meta[@property="og:title"]/@content',
            "TestDateText": "substring-before(//time[@class='dtreviewed']"
            "/@datetime|//meta[@property='article:published_time']/@content,'T')",
            'SourceTestRating':  "//div[@class='col-1 overall']/div/span/text()",
            'TestCons': "//p[@class='theBad']/span/text()",
            'TestPros': "//p[@class='theGood']/span/text()",
            'TestVerdict': "//p[@class='theBottomLine']/span/text()"

        }
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        review['ProductName'] = self.get_product_name(response)
        review['source_internal_id'] = self.get_source_internal_id(response)

        if review['SourceTestRating']:
            review['SourceTestScale'] = TESTSCALE

        review["DBaseCategoryName"] = "PRO"

        product_id = self.parse_price(product, response)
        yield product_id
        yield review
