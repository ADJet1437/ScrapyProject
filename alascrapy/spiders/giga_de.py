# -*- coding: utf8 -*-
from datetime import datetime
import re

from alascrapy.lib.dao import incremental_scraping as incremental_utils
from alascrapy.spiders.base_spiders import ala_spider as spiders


class GigaDeSpider(spiders.AlaSpider):
    name = 'giga_de'
    allowed_domains = ['giga.de']
    start_urls = [
        'https://www.giga.de/tech/tests/',
        'https://www.giga.de/androidnews/tests',
        'https://www.giga.de/mac/tests/',
        'https://www.giga.de/windows/tests/',
        'https://www.giga.de/games/tests/',
    ]

    def __init__(self, *args, **kwargs):
        super(GigaDeSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf['source_id'])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):
        next_page_xpath = '//a[@rel="next"]/@href'
        next_page_link = response.xpath(next_page_xpath).extract()
        if len(next_page_link) > 0:
            yield response.follow(url=next_page_link[0], callback=self.parse)

        reviews_xpath = '//article//a/@href'
        review_links = response.xpath(reviews_xpath).extract()
        for link in review_links:
            yield response.follow(url=link, callback=self.parse_review_page)

    def parse_review_page(self, response):
        product = self.parse_product(response)
        review = self.parse_review(response)
        yield product
        yield review

    def get_sii(self, response):
        sii_xpath = '//img[@id="postview_pixel"]/@src'
        sii = response.xpath(sii_xpath).extract()
        if len(sii) == 0:
            return None

        sii = sii[0]
        # Gets last part of the url, example URL:
        # https://www.giga.de/api/core/tracking/access/post/4576458
        sii = sii.split('/')[-1]
        return sii

    def get_product_name(self, response):
        title_xpath = '//meta[@name="title"]/@content|//title/text()'
        title = response.xpath(title_xpath).extract()
        if len(title) == 0:
            return None

        title = title[0]
        product_name = title.split(':')[0]
        # removes ending ' im test' from titles, if they exist
        regex = r'\s?(im)?\s?(test)?$'
        product_name = re.sub(regex, '', product_name, flags=re.IGNORECASE)

        if not product_name:
            return title

        return product_name

    def parse_product(self, response):
        product_xpaths = {
            'PicURL': '//link[@rel="image_src"]/@href',
            'OriginalCategoryName': '//dl/dt[text()="Genres"]/'
            'following-sibling::dd[1]/a/text()',
            'ProductManufacturer': '//dl/dt[text()="Hersteller"]/'
            'following-sibling::dd[1]/a/text()',
        }
        product = self.init_item_by_xpaths(response, 'product', product_xpaths)

        product['TestUrl'] = response.url
        product['source_id'] = self.spider_conf['source_id']
        product['source_internal_id'] = self.get_sii(response)
        product['ProductName'] = self.get_product_name(response)

        return product

    def parse_review(self, response):
        review_xpaths = {
            'Author': '//span[@data-trigger="page-author-name"]/text()',
            'SourceTestRating': '//*[contains(text(), "Gesamt:")]/text()',
            'TestSummary': '//meta[@name="description"]/@content',
            'TestTitle': '//meta[@name="title"]/@content',
            'TestDateText': 'substring-before('
            '//meta[@property="article:published_time"]/@content, "T")',
        }

        review = self.init_item_by_xpaths(response, 'review', review_xpaths)

        review['TestUrl'] = response.url
        review['source_id'] = self.spider_conf['source_id']
        review['source_internal_id'] = self.get_sii(response)
        review['ProductName'] = self.get_product_name(response)
        review['DBaseCategoryName'] = 'PRO'

        rating = review['SourceTestRating']
        if rating:
            match = re.search(r'(\d+)', rating)
            if match:
                review['SourceTestRating'] = match.group(1)
                review['SourceTestScale'] = 100
            else:
                review['SourceTestRating'] = None

        return review
