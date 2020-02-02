# -*- coding: utf8 -*-
import re
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider

TEST_SCALE = 10
MAX_SENTENCES = 2


class EuropeanConsumersChoiceSpider(AlaSpider):
    name = 'europeanconsumerschoice_org'
    allowed_domains = ['europeanconsumerschoice.org']
    start_urls = [
        'https://www.europeanconsumerschoice.org/hi-tech/']

    def parse(self, response):
        review_urls_xpath = "//figure/a/@href"
        review_urls = self.extract_list(response.xpath(review_urls_xpath))

        for review_url in review_urls:
            yield response.follow(review_url,
                                  callback=self.parse_review_product)

    def parse_review_product(self, response):
        product = self.parse_product(response)
        review = self.parse_review(response)
        yield product
        yield review

    def get_source_internal_id(self, response):
        SI_id_xpath = "//script[contains(text(),'pageId')]/text()"
        source_int_id = self.extract(response.xpath(SI_id_xpath))
        source_internal_id = re.findall(r'"pageId":(\d+)', source_int_id)
        source_internal_id = source_internal_id[0]
        return source_internal_id

    def parse_product(self, response):
        product_xpaths = {
            'PicURL': '(//figure/img)[1]/@src',
            'ProductName': "//meta[@property='og:title']/@content",
            "OriginalCategoryName": "substring-after(//meta"
            "[@property='og:title']/@content, '|')"
        }

        product = self.init_item_by_xpaths(response, 'product', product_xpaths)
        product["ProductName"] = product["ProductName"].split('|')[0]
        product["source_internal_id"] = self.get_source_internal_id(response)

        product["OriginalCategoryName"] = product["OriginalCategoryName"]\
            .replace("test and reviews", '').replace("Test and reviews", '').\
            replace("Test & reviews", '').replace("Test & review", '').\
            replace("test & reviews", '').replace("Test and review", '').\
            replace("reviews", '')

        return product

    def parse_review(self, response):
        review_xpaths = {
            'ProductName': "//meta[@property='og:title']/@content",
            'TestTitle': '//meta[@property="og:title"]/@content'
        }

        review = self.init_item_by_xpaths(response, 'review', review_xpaths)
        review["ProductName"] = review["ProductName"].split('|')[0]
        review["source_internal_id"] = self.get_source_internal_id(response)
        review['DBaseCategoryName'] = 'PRO'

        source_rating_xpath = '//div[@class="cc-m-textwithimage-inline-rte"]'\
            '/div/descendant-or-self::*/text()'
        source_rating = self.extract_all(response.xpath(source_rating_xpath))
        source_test_rating = re.findall(r'Global notation : (\d*[.,]?\d*$)',
                                        source_rating)
        review['SourceTestRating'] = source_test_rating[0]
        if review["SourceTestRating"]:
            review["SourceTestScale"] = TEST_SCALE

        summary_xpath = '//div[@class="j-module n j-text "]/p/text()|'\
            '//div[@class="j-module n j-text "]/p/span/text()'
        test_summary = self.extract(response.xpath(summary_xpath))

        if len(test_summary) > 100:
            test_summary = '.'.join(
                test_summary.split('.')[0:MAX_SENTENCES]) + '.'
            review["TestSummary"] = test_summary

        return review
