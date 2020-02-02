# -*- coding: utf8 -*-

import json
from datetime import datetime
from scrapy.http import Request

import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.lib import extruct_helper
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.items import ReviewItem, ProductItem


class MediatotaalNlSpider(AlaSpider):
    name = 'mediatotaal_nl'
    allowed_domains = ['mediatotaal.nl']
    start_urls = ['http://mediatotaal.nl/?categories=review']

    def __init__(self, *args, **kwargs):
        super(MediatotaalNlSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):
        # Check if they send JSON-LD
        xpaths = {
            'review_links': '//a[@class="list-item__link"]/@href',
            'next_page': '//a[contains(concat(" ", normalize-space(@class),' +
            ' " "), " paginator__next ")]/@href'
        }
        review_links = response.xpath(xpaths['review_links']).extract()
        next_page_link = response.xpath(xpaths['next_page']).extract()
        # Checks if there is a "next_page" to extract more review links
        if len(next_page_link) > 0:
            yield response.follow(url=next_page_link[0], callback=self.parse)

        # Open the review links for parsing/extracting
        for link in review_links:
            yield response.follow(url=link, callback=self.parse_review_page)

    def parse_review_page(self, response):
        product = self.parse_product(response)
        review = self.parse_review(response)
        yield product
        yield review

    def parse_product(self, response):
        product_xpaths = {
            'source_internal_id':
                '//div[@data-widget="article-edit"]/@data-meta',
            'PicURL': '//*[@class="article-media-container"]//img/@src',
            'ProductName': '//section/header/h1/text()'
        }

        product = self.init_item_by_xpaths(response, "product", product_xpaths)

        product['source_internal_id'] = json.loads(
            product['source_internal_id']).get('id')

        product['TestUrl'] = response.url
        product['source_id'] = self.spider_conf["source_id"]

        return product

    def parse_review(self, response):
        review = ReviewItem()

        # Parsing using XPath
        xpaths = {
            'TestSummary': '//meta[@property="og:description"]/@content',
            'TestPros':
                '//*[@class="rs-review--positives"]//span/text()',
            'TestCons':
                '//*[@class="rs-review--negatives"]//span/text()',
            'source_internal_id':
                '//div[@data-widget="article-edit"]/@data-meta',
            'ProductName': '//section/header/h1/text()',
        }

        # Extract
        data = {}
        for key in xpaths:
            data[key] = response.xpath(xpaths[key]).extract()

        # Process
        if(len(data['source_internal_id']) > 0):
            data['source_internal_id'] = json.loads(
                data['source_internal_id'][0]).get('id')
        data['TestPros'] = ';'.join(data['TestPros'])
        data['TestCons'] = ';'.join(data['TestCons'])
        data['TestSummary'] = data['TestSummary'][0]
        data['ProductName'] = data['ProductName'][0]

        for key in xpaths:
            review[key] = data[key]

        # Parsing using JSON-LD
        # Populates:
        # Author, SourceTestRating, SourceTestScale, TestDateText, TestTitle

        review_json_ld = extruct_helper.extract_json_ld(
            response.text, 'Review')

        if review_json_ld:
            review = extruct_helper.review_item_from_review_json_ld(
                review_json_ld, review)

        review['TestUrl'] = response.url
        review['source_id'] = self.spider_conf["source_id"]
        review['DBaseCategoryName'] = 'PRO'

        # There are some occurences of "null" in the TestTile and TestSummary
        if review['TestTitle'] == 'null':
            review['TestTitle'] = review['ProductName']
        if review['TestSummary'] == 'null':
            review['TestSummary'] = ''

        return review
