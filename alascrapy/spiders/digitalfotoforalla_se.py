# -*- coding: utf8 -*-
from datetime import datetime
import json

from scrapy.http import Request

from alascrapy.lib.dao import incremental_scraping as incremental_utils
from alascrapy.spiders.base_spiders import ala_spider as spiders
from alascrapy.items import ProductItem, ReviewItem


class DigitalfotoforallaSeSpider(spiders.AlaSpider):
    name = 'digitalfotoforalla_se'
    allowed_domains = ['digitalfotoforalla.se']
    domain = 'test.digitalfotoforalla.se'
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'COOKIES_ENABLED': True,
    }

    def __init__(self, *args, **kwargs):
        super(DigitalfotoforallaSeSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf['source_id'])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def start_requests(self):
        yield self.get_request(0)

    def get_request(self, page):
        request_url='http://{domain}/cms/wp-admin/admin-ajax.php?'\
                    'action=product-search' \
                    '&orderby=review_date' \
                    '&order=desc' \
                    '&page={page}'.format(domain=self.domain, page=page)

        request = Request(
            url=request_url, 
            callback=self.parse,
            method='GET',
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            meta={ 'next_page': page + 1 }
        )
        return request

    def parse(self, response):
        body = json.loads(response.text)
        nodes = body.get('data', {}).get('rows')
        total_num = body.get('data', {}).get('total', 0)
        ITEM_PER_PAGE = 10
        next_page_index = response.meta['next_page'] 
        # check the availiability of the next page
        if total_num - (ITEM_PER_PAGE * next_page_index) > 0:
            yield self.get_request(next_page_index)
        for node in nodes:
            review = self.parse_review(node, response)
            product = self.parse_product(node, response)
            yield review
            yield product

    def parse_product(self, node, response):
        product = ProductItem()

        meta_info = node.get('meta', {})
        product['ProductName'] = node.get('title', '')
        product['OriginalCategoryName'] = '|'.join(node.get('categories', ['']))
        product['ProductManufacturer'] = node.get('tags', [''])[0]
        product['PicURL'] = node.get('image', '')
        product['TestUrl'] = node.get('url', '')
        product['source_id'] = self.spider_conf['source_id']
        product['source_internal_id'] = meta_info.get('id', '')
        return product

    def parse_review(self, node, response):
        review = ReviewItem()

        # No author for the source page
        meta_info = node.get('meta', {})
        review['ProductName'] = node.get('title', '')
        review['source_internal_id'] = meta_info.get('id', '')
        review['TestDateText'] = meta_info.get('review_date', '')
        review['TestSummary'] = node.get('description', '')
        review['TestTitle'] = review.get('ProductName')
        review['TestUrl'] = node.get('url', '')
        review['SourceTestRating'] = meta_info.get('expert_evaluation_float', '')
        # source rating scale based on scale of 10
        if review.get('SourceTestRating'):
            review['SourceTestScale'] = 10
        review['source_id'] = self.spider_conf['source_id']
        review['DBaseCategoryName'] = 'PRO'

        if meta_info.get('conclusion', ''):
            review['TestVerdict'] = meta_info.get('conclusion', '')
        if meta_info.get('reviewer', ''):
            review['Author'] = meta_info.get('reviewer', '')

        return review
