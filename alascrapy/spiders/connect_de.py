# -*- coding: utf8 -*-
import re

from alascrapy.items import ProductIdItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider

TEST_SCALE = 100


class Connect_deSpider(AlaSpider):
    name = 'connect_de'
    allowed_domains = ['connect.de']
    start_urls = ['https://www.connect.de/testbericht/alle/2018-05/']

    def parse(self, response):
        archive_urls_xpath = "//a[contains(@href, 'alle/2')]/@href"
        archive_urls = self.extract_list(response.xpath(archive_urls_xpath))

        if archive_urls:
            for archive_url in archive_urls:
                yield response.follow(archive_url, callback=self.parse_archive)

    def parse_archive(self, response):
        review_url_xpath = "//h3/a[@class='teaser__link']/@href"
        review_urls = self.extract_list(response.xpath(review_url_xpath))

        for review_url in review_urls:
            yield response.follow(review_url,
                                  callback=self.parse_review_product)

    def parse_review_product(self, response):
        product = self.parse_product(response)
        review = self.parse_review(response)
        product_id = self.parse_price(product, response)
        yield product
        yield review
        yield product_id

    def get_source_int_id(self, response):
        source_int_id = "//meta[@property='og:url']/@content"
        SID = self.extract(response.xpath(source_int_id))
        matches = re.search("(\d+)(?=\.html)", SID, re.IGNORECASE)
        source_internal_id = matches.group(1)
        return source_internal_id

    def parse_product(self, response):
        product_xpaths = {
            'ProductName': "//h1[@itemprop='headline']/text()",
            'PicURL': '//meta[@property="og:image"]/@content',
            "OriginalCategoryName": '//span[@class="content__kicker"]/text()'
        }

        product = self.init_item_by_xpaths(response, 'product', product_xpaths)
        product["ProductName"] = product["ProductName"].replace(
            'im Test', '')
        product["source_internal_id"] = self.get_source_int_id(response)
        return product

    def parse_price(self, product, response):
        price_xpath = "//div[@class="\
            "'inline_plusminuslist__amazon_section_price']/text()"
        price_str = self.extract(response.xpath(price_xpath))

        if price_str:
            return ProductIdItem.from_product(
                product,
                kind='price',
                value=price_str
            )

    def parse_review(self, response):
        review_xpaths = {
            'ProductName': "//h1[@itemprop='headline']/text()",
            'TestTitle': "substring-before("
            "//meta[@property='og:title']/@content,'-')",
            'Author': '//span[@itemprop="author"]/span/text()',
            "SourceTestRating": "substring-before(//div["
            "@itemprop='ratingValue']/text(),'%')",
            "TestDateText": "//span[@class='content__date']/@content",
            'TestSummary': '//meta[@name="description"]/@content',
            'TestPros': "//h3[contains(text(), 'Pro')]"
            "/following-sibling::ul/li/text()",
            'TestCons': "//h3[contains(text(), 'Contra')]"
            "/following-sibling::ul/li/text()",
            'TestVerdict': "//h3[contains(text(), 'Fazit')]"
            "/following-sibling::span/text()"
        }

        review = self.init_item_by_xpaths(response, 'review', review_xpaths)

        review["source_internal_id"] = self.get_source_int_id(response)
        review["ProductName"] = review["ProductName"].replace(
            'im Test', '')

        if review["SourceTestRating"]:
            review["SourceTestScale"] = TEST_SCALE

        review['DBaseCategoryName'] = 'PRO'

        return review
