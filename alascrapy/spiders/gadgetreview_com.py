# -*- coding: utf8 -*-
from datetime import datetime
import re

from alascrapy.lib.dao import incremental_scraping as incremental_utils
from alascrapy.spiders.base_spiders import ala_spider as spiders


class GadgetReviewComSpider(spiders.AlaSpider):
    name = 'gadgetreview_com'
    allowed_domains = ['gadgetreview.com']
    start_urls = [
        'http://www.gadgetreview.com/reviews/electronics',
        'http://www.gadgetreview.com/reviews/gaming',
        'http://www.gadgetreview.com/reviews/mobiles',
        'http://www.gadgetreview.com/reviews/kitchen-gadgets',
        'http://www.gadgetreview.com/reviews/drone-reviews',
    ]

    def parse(self, response):
        next_page_xpath = u'//a[text()="›"]/@href'
        next_page_link = self.extract(response.xpath(next_page_xpath))
        if next_page_link:
            yield response.follow(url=next_page_link, callback=self.parse)

        reviews_xpath = '//article//a[@rel="bookmark"]/@href'
        review_links = response.xpath(reviews_xpath).extract()
        for link in review_links:
            # Most articles (not reviews) has 'best-...' and are not useful
            if 'best-' not in link:
                yield response.follow(url=link,
                                      callback=self.parse_review_page)

    def parse_review_page(self, response):
        product = self.parse_product(response)
        review = self.parse_review(response)
        yield product
        yield review

    def get_sii(self, response):
        sii_xpath = '//body/@class'
        sii_regex = r'postid-(\d+)'

        sii = self.extract(response.xpath(sii_xpath))
        sii_match = re.search(sii_regex, sii)

        if not sii:
            return None

        return sii_match.groups()[0]

    def get_product_name(self, response):
        product_name_xpath = '//figure/img/@alt|//title/text()'
        product_name = self.extract(response.xpath(product_name_xpath))
        if not product_name:
            return None

        product_name = product_name.replace(' Review Roundup', '')
        return product_name

    def parse_product(self, response):
        product_xpaths = {
            'OriginalCategoryName': '//span[@class="ft-scategories"]/a/text()',
            'PicURL': '//meta[@property="og:image"]/@content',

            'ProductManufacturer': '//a[contains('
            '@href, "campaign=brand")]/text()',
        }
        product = self.init_item_by_xpaths(response, 'product', product_xpaths)

        product['TestUrl'] = response.url
        product['source_id'] = self.spider_conf['source_id']
        product['source_internal_id'] = self.get_sii(response)
        product['ProductName'] = self.get_product_name(response)

        return product

    def parse_review(self, response):
        review_xpaths = {
            'Author': '//span[@rel="author"]/text()',
            'ProductName': '//figure/img/title|//title/text()',
            'TestCons': '//h2[text()="Cons"]/'
            'following-sibling::ul[1]/li/text()',
            'TestPros': '//h2[text()="Pros"]/'
            'following-sibling::ul[1]/li/text()',
            'TestSummary': '//meta[@property="og:description"]/@content',
            'TestTitle': '//meta[@property="og:title"]/@content',

            'TestVerdict': '//*[text()="Bottom Line"]/'
            'following-sibling::p[1]/text()',

            'TestDateText': 'substring-before('
            '//meta[@property="article:published_time"]/@content, "T")',
        }

        review = self.init_item_by_xpaths(response, 'review', review_xpaths)

        review['TestUrl'] = response.url
        review['source_id'] = self.spider_conf['source_id']
        review['DBaseCategoryName'] = 'PRO'
        review['source_internal_id'] = self.get_sii(response)
        review['ProductName'] = self.get_product_name(response)

        return review
