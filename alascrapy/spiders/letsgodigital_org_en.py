# -*- coding: utf8 -*-
from datetime import datetime

import js2xml

from alascrapy.lib.dao import incremental_scraping as incremental_utils
from alascrapy.spiders.base_spiders import ala_spider as spiders


class LetsGoDigitalOrgEnSpider(spiders.AlaSpider):
    name = 'letsgodigital_org_en'
    allowed_domains = ['en.letsgodigital.org']
    start_urls = ['https://en.letsgodigital.org/']

    def __init__(self, *args, **kwargs):
        super(LetsGoDigitalOrgEnSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf['source_id'])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):
        categories_url_xpath = '//nav[@id="nav-categories"]/ul/li/a/@href'
        categories_links = response.xpath(categories_url_xpath).extract()
        for link in categories_links:
            yield response.follow(url=link, callback=self.parse_category_page)

    def parse_category_page(self, response):
        next_page_xpath = '//a[@class="next page-numbers"]/@href'
        next_page_link = response.xpath(next_page_xpath).extract()
        if len(next_page_link) > 0:
            yield response.follow(url=next_page_link[0], callback=self.parse)

        reviews_xpath = '//a[contains(@class, "review__link")]/@href'
        review_links = response.xpath(reviews_xpath).extract()
        for link in review_links:
            yield response.follow(url=link, callback=self.parse_review_page)

    def parse_review_page(self, response):
        product = self.parse_product(response)
        review = self.parse_review(response)
        yield product
        yield review

    def product_name_from_url(self, url):
        # sample Url: https://en.letsgodigital.org/smartphones/lg-v30s-thinq/
        parts = url.split('/')
        # ['https:', ..., 'lg-v30s-thinq', '']
        product_name = parts[-2]
        return product_name.replace('-', ' ')

    def get_sii(self, response):
        id_data_xpath = '//script[@type="text/javascript" and ' \
            'contains(text(), "pvcArgsFrontend")]/text()'
        post_id_xpath = '//property[@name="postID"]/string/text()'

        js_text = self.extract_xpath(response, id_data_xpath)
        parsed = js2xml.parse(js_text)
        sii = parsed.xpath(post_id_xpath)

        if sii and len(sii) > 0:
            return sii[0]

        return None

    def parse_product(self, response):
        product_xpaths = {
            'OriginalCategoryName': '//meta[@property="article:section"]'
            '/@content',
            'PicURL': '//meta[@property="og:image"]/@content',
        }

        product = self.init_item_by_xpaths(response, 'product', product_xpaths)

        product['ProductName'] = self.product_name_from_url(response.url)
        product['TestUrl'] = response.url
        product['source_id'] = self.spider_conf['source_id']
        product['source_internal_id'] = self.get_sii(response)

        return product

    def parse_review(self, response):
        review_xpaths = {
            'Author': '//div[@class="author__name"]/text()',
            'TestDateText': 'substring-before('
            '//meta[@property="article:published_time"]/@content, "T")',
            'TestSummary': '//meta[@property="og:description"]/@content',
            'TestTitle': '//meta[@property="og:title"]/@content',
        }

        review = self.init_item_by_xpaths(response, 'review', review_xpaths)

        review['TestUrl'] = response.url
        review['source_id'] = self.spider_conf['source_id']
        review['ProductName'] = self.product_name_from_url(response.url)
        review['DBaseCategoryName'] = 'PRO'  # 'USER'
        review['source_internal_id'] = self.get_sii(response)

        return review
