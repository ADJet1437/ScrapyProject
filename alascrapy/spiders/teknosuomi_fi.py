# -*- coding: utf8 -*-
from datetime import datetime
import re

from alascrapy.lib.dao import incremental_scraping as incremental_utils
from alascrapy.spiders.base_spiders import ala_spider as spiders


class TeknosuomiFiSpider(spiders.AlaSpider):
    name = 'teknosuomi_fi'
    allowed_domains = ['teknosuomi.fi']
    start_urls = ['https://www.teknosuomi.fi/category/mobiili/']

    def __init__(self, *args, **kwargs):
        super(TeknosuomiFiSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf['source_id'])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):
        next_page_xpath = '//a[@class="next page-numbers pagenav"]/@href'
        next_page_link = response.xpath(next_page_xpath).extract()
        if len(next_page_link) > 0:
            yield response.follow(url=next_page_link[0], callback=self.parse)

        reviews_xpath = '//p[@class="readmore"]/a/@href'
        review_links = response.xpath(reviews_xpath).extract()
        for link in review_links:
            yield response.follow(url=link, callback=self.parse_review_page)

    def parse_review_page(self, response):
        product = self.parse_product(response)
        review = self.parse_review(response)
        yield product
        yield review

    def get_sii(self, response):
        sii_xpath = '//link[@rel="shorturl"]/@href'
        # Extracts the shortlink for the review page, eg. http://droid.fi/NuSkx
        short_link = self.extract(response.xpath(sii_xpath))
        sii_match = re.search('.*/(.*)$', short_link)
        if sii_match:
            # group(1) will return the matched group on the regex,
            # re.search('.*/(.*)$', 'http://droid.fi/NuSkx').group(1) # 'NuSkx'
            return sii_match.group(1)
        return None

    def parse_product(self, response):
        product_xpaths = {
            'OriginalCategoryName': '//div[@class="rt-block"]//a/text()',
            'PicURL': '//meta[@property="og:image"]/@content',
            'ProductName': '//meta[@property="og:title"]/@content',
        }
        product = self.init_item_by_xpaths(response, 'product', product_xpaths)

        product['TestUrl'] = response.url
        product['source_id'] = self.spider_conf['source_id']
        product['source_internal_id'] = self.get_sii(response)

        return product

    def parse_review(self, response):
        review_xpaths = {
            'Author': '//meta[@itemprop="author"]/@content',
            'ProductName': '//meta[@property="og:title"]/@content',
            'TestDateText': '//meta[@itemprop="datePublished"]/@content',
            'TestSummary': '//meta[@property="og:description"]/@content',
            'TestTitle': '//meta[@property="og:title"]/@content',
        }

        review = self.init_item_by_xpaths(response, 'review', review_xpaths)

        review['TestUrl'] = response.url
        review['source_id'] = self.spider_conf['source_id']
        review['source_internal_id'] = self.get_sii(response)
        review['DBaseCategoryName'] = 'PRO'

        return review
