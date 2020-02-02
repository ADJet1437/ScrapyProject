# -*- coding: utf8 -*-

import json
import re
from datetime import datetime
import dateparser
from scrapy.http import Request

import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.lib import extruct_helper
from alascrapy.lib.generic import date_format,get_full_url
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.items import ReviewItem, ProductItem

class AudioholicsComSpider(AlaSpider):
    name = 'audioholics_com'
    allowed_domains = ['audioholics.com']
    start_urls = ['https://www.audioholics.com/product-reviews']

    def __init__(self, *args, **kwargs):
        super(AudioholicsComSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(2019, 1, 1)

    def parse(self, response):

        review_divs_xpath = "//div[@class='listing-page-1']"
        review_divs = response.xpath(review_divs_xpath)

        for review_div in review_divs:
            date_xpath = ".//div//p/span/text()"
            dates = (review_div.xpath(date_xpath)).getall()
            for date in dates:
                r_date = date.encode('utf-8').strip('\n').split('—')
                review_date = dateparser.parse(date, date_formats=['%m %d, %Y, %H:%M'])
                if review_date:
                    if review_date > self.stored_last_date:
                        review_urls_xpath = ".//div/div[@class='post']/a/@href"
                        review_urls = (review_div.xpath(review_urls_xpath)).getall()
                        for review_url in review_urls:
                            r_url = 'https://www.audioholics.com' + str(review_url)
                            yield Request(url=r_url, callback=self.parse_review_page)
        
        last_page=5
        for i in range(2, last_page+1):
            next_page_url = 'https://www.audioholics.com/page/'+str(i)

        review_date_xpath = "(//div//p/span/text())[last()]"
        review_date = self.extract(response.xpath(review_date_xpath))
        oldest_review_date = dateparser.parse(review_date, date_formats=['%m %d, %Y, %H:%M'])

        if next_page_url:
            if oldest_review_date > self.stored_last_date:
                yield response.follow(next_page_url, callback=self.parse)

    def parse_review_page(self, response):
        product = self.parse_product(response)
        review = self.parse_review(response)
        yield product
        yield review

    def get_product_name(self, response):
        url = response.url
        name = url.split('/')[-1]
        name = name.replace('-', ' ')
        return name

    def parse_product(self, response):
        product_xpaths = {
            'PicURL': '//a[@class="lb-show"]/@href',
            'ProductName': '//div[@class="productDataBlock"]/ul/li[1]/strong/text()',
            'ProductManufacturer': '//div[@class="productDataBlock item"]/'
            'ul/li[contains(text(), "Manufacturer")]/strong/span/text()',
        }

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        if not product.get('ProductName', ''):
            product['ProductName'] = self.get_product_name(response)

        source_internal_id = str(response).split("/")[4]
        product['source_internal_id'] = source_internal_id.rstrip('>')
        
        breadcrumb_json_ld = extruct_helper.extract_json_ld(
            response.text, "BreadcrumbList")
        if breadcrumb_json_ld:
            items = breadcrumb_json_ld.get('itemListElement', None)
            if items and len(items) > 1:
                product['OriginalCategoryName'] = items[1].get(
                    'item', {}).get('name', '')

        return product

    def parse_review(self, response):

        review_json_ld = extruct_helper.extract_json_ld(
            response.text, "Review")
        article_json_ld = extruct_helper.extract_json_ld(
            response.text, "NewsArticle")

        if review_json_ld:
            review = extruct_helper.review_item_from_review_json_ld(
                review_json_ld)
        elif article_json_ld:
            review = extruct_helper.review_item_from_article_json_ld(
                article_json_ld)
        else:
            review = ReviewItem()

        review['DBaseCategoryName'] = 'PRO'
        if not review.get('TestUrl', ''):
            review['TestUrl'] = response.url

        review['ProductName'] = self.extract(response.xpath("//div[@class='productDataBlock']/ul/li[1]/strong/text()"))
        if not review.get('ProductName', ''):
            review['ProductName'] = self.get_product_name(response)

        source_internal_id = str(response).split("/")[4]
        review['source_internal_id'] = source_internal_id.rstrip('>')

        review['TestPros'] = self.extract(response.xpath("//div[@id='ahReviewPros']/ul/li/text()"))
        review['TestCons'] = self.extract(response.xpath("//div[@id='ahReviewCons']/ul/li/text()"))

        return review
