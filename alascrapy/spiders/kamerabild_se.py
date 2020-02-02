# -*- coding: utf8 -*-
from datetime import datetime

from scrapy.http.request import Request

from alascrapy.lib.dao import incremental_scraping as incremental_utils
from alascrapy.spiders.base_spiders import ala_spider as spiders


class KameraBildSpider(spiders.AlaSpider):
    name = 'kamerabild_se'
    allowed_domains = ['kamerabild.se']
    start_urls = ['https://www.kamerabild.se/tester']

    def __init__(self, *args, **kwargs):
        super(KameraBildSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf['source_id'])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def get_request(self, page):
        base_url = 'https://www.kamerabild.se/vyfix/article_lists/' \
            'panel_pane_2/2?page={page}'

        request = Request(
            url=base_url.format(page=page),
            meta={
                'next-page': page + 1
            }
        )

        return request

    def start_requests(self):
        # Creates request for the first (0) page
        yield self.get_request(0)

    def get_sii(self, response):
        sii_xpath = '//link[@rel="shortlink"]/@href'
        # Example sii: "https://www.kamerabild.se/node/545886"
        sii = self.extract(response.xpath(sii_xpath))
        # Gets lets url part
        return sii.split('/')[-1]

    def get_product_name(self, response):
        product_name_xpath = '//meta[@property="og:title"]/@content'
        # Example product_name: "Test: Palettegear – kul pryl, men klurig"
        # Example product_name: "Sony A7 III: Uppdaterad entusiastmodell"
        product_name = self.extract(response.xpath(product_name_xpath))
        # Gets everything before '–'
        product_name = product_name.split(u'–')[0]
        # Gets everything after 'Test:'
        product_name = product_name.split(u'Test:')[-1]
        # Gets everything before ':'
        product_name = product_name.split(u':')[0]
        # Gets lets url part
        return product_name.strip()

    def parse(self, response):
        reviews_xpath = '//div[@class="view-content"]/ul//h2/a/@href'
        review_links = response.xpath(reviews_xpath).extract()
        for link in review_links:
            yield response.follow(url=link, callback=self.parse_review_page)

        if len(review_links) > 0:
            yield self.get_request(response.meta.get('next-page'))

    def parse_review_page(self, response):
        product = self.parse_product(response)
        review = self.parse_review(response)
        yield product
        yield review

    def parse_product(self, response):
        product_xpaths = {
            'PicURL': 'substring-before('
            '//meta[@property="og:image"]/@content, "?")',
        }
        product = self.init_item_by_xpaths(response, 'product', product_xpaths)

        product['TestUrl'] = response.url
        product['source_id'] = self.spider_conf['source_id']
        product['source_internal_id'] = self.get_sii(response)
        product['ProductName'] = self.get_product_name(response)

        return product

    def parse_review(self, response):
        review_xpaths = {
            'Author': '//span[@class = "author-name"]/a/text()',
            'source_internal_id': '//link[@rel="shortlink"]/@href',
            'TestSummary': '//meta[@property="og:description"]/@content',
            'TestTitle': '//meta[@property="og:title"]/@content',

            'TestVerdict': '//h3[contains(text(), "Sammanfattning")]'
            '/following-sibling::p[1]/text()',

            'TestDateText': 'substring-before(normalize-space('
            '//li[@class="author"]/*[last()]), " ")',
        }

        review = self.init_item_by_xpaths(response, 'review', review_xpaths)

        review['TestUrl'] = response.url
        review['source_id'] = self.spider_conf['source_id']
        review['source_internal_id'] = self.get_sii(response)
        review['ProductName'] = self.get_product_name(response)
        review['DBaseCategoryName'] = 'PRO'

        return review
