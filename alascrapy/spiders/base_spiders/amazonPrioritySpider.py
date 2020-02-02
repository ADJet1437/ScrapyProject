# -*- coding: utf8 -*-
import requests
import traceback
import StringIO
import datetime
import os
import gzip
import csv
import sys
import re
from requests.auth import HTTPDigestAuth
from lxml import etree
import dateparser
from scrapy.http import Request


from alascrapy.lib.log import log_exception
from alascrapy.lib.amazon_graph import CategoryTree
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.items import ProductItem, CategoryItem, ReviewItem, AmazonProduct, ProductIdItem
from alascrapy.lib.amazon import AmazonAPI
from alascrapy.lib.generic import remove_querystring, normalize_price, \
    parse_float, download_file, md5, get_full_url, date_format
from alascrapy.lib.dao.amazon import get_feed_categories, update_feed_category
from alascrapy.lib.mq.mq_publisher import MQPublisher
from alascrapy.lib.dao.incremental_scraping import \
    get_latest_user_review_date, get_incremental, update_incremental


class AmazonPriorityReviewsSpider(AlaSpider):
    name = 'amazon_com_reviews_test'

    start_url_format = "https://www.amazon.com/product-reviews/%s/ref=cm_cr_dp_see_all_btm?ie=UTF8&showViewpoints=1&sortBy=recent"
    date_format = 'on %d %B %Y'
    amazon_kind = 'amazon_us_id'
    language = 'en'

    rating_re = re.compile('a-star-(\d)')
    custom_settings = {'COOKIES_ENABLED': True,
                       'DOWNLOADER_MIDDLEWARES':
                           {'alascrapy.middleware.forbidden_requests_middleware.ForbiddenRequestsMiddleware': None}}
    download_delay=3

    def __init__(self, *args, **kwargs):
        super(AmazonPriorityReviewsSpider, self).__init__(self, *args, **kwargs)


    def start_requests(self):

        query = "select pi.id_value from review.product_id pi " \
                "join review.products p on pi.prdid = p.id " \
                "join mamboinput.alascore a on p.al_id = a.al_id " \
                "where pi.kind = 7 and p.source_id =  %s " \
                "and TIMESTAMPDIFF(MONTH, p.updatetime,now()) < 4 " \
                "order by a.alascore desc, a.rank"

        self.mysql_manager.execute_select(query, self.spider_conf['source_id'])


        for asin in self.asins:
            start_url = self.start_url_format % asin
            request = Request(url=start_url, callback=self.parse_reviews)
            request.meta['asin'] = asin
            request.meta['last_review_in_db'] = get_latest_user_review_date(self.mysql_manager,
                                                             self.spider_conf['source_id'],
                                                             self.amazon_kind,
                                                             asin)
 
            yield request

    def _format_date(self, raw_review, date_xpath):
        date = self.extract_xpath(raw_review, date_xpath)
        date = date_format(date, self.date_format, languages=[self.language])
        return date


    def parse_reviews(self, response):
        print response.url
        asin = response.meta['asin']

        product_name_xpath = "//div[contains(@class, 'product-title')]//text()"
        reviews_xpath = "//div[@id='cm_cr-review_list']/div[@id]"
        next_page_xpath = "//div[@id='cm_cr-pagination_bar']//li[@class='a-last']/a/@href"

        title_xpath=".//a[contains(@class,'review-title')]/text()"
        review_url_xpath=".//a[contains(@class,'review-title')]/@href"
        summary_xpath = ".//span[contains(@class,'review-text')]/text()"
        author_xpath = ".//a[contains(@class,'author')]/text()"
        rating_xpath = ".//i[contains(@class, 'review-rating')]/@class"
        date_xpath = ".//span[contains(@class, 'review-date')]/text()"

        product_name = self.extract_xpath(response, product_name_xpath)
        product = ProductItem.from_response(response, product_name=product_name,
                                            source_internal_id=asin)

        reviews = response.xpath(reviews_xpath)
        date = ''

        for raw_review in reviews:
            rating = ''
            title = self.extract_xpath(raw_review, title_xpath)
            review_url = self.extract_xpath(raw_review, review_url_xpath)
            review_url = get_full_url(response.url, review_url)
            summary = self.extract_all_xpath(raw_review, summary_xpath)
            author = self.extract_xpath(raw_review, author_xpath)
            raw_rating = self.extract_xpath(raw_review, rating_xpath)
            match = re.search(self.rating_re, raw_rating)
            if match:
                rating = match.group(1)
            date = self._format_date(raw_review, date_xpath)

            review = ReviewItem.from_product(product, tp='USER', rating=rating,
                                             scale=5, date=date, author=author,
                                             summary=summary, url=review_url, title=title)
            yield review

        if not date:
            retries = response.meta.get('ama_retries', 0)
            if retries >= 8: #8 tor processes
                self.logger.warning("Max retries, blocked: %s" % response.url)
                return

            retryreq = response.request.copy()
            retryreq.meta['ama_retries'] = retries + 1
            retryreq.meta['dont_merge_cookies'] = True
            retryreq.dont_filter = True
            retryreq.cookies = {}
            yield retryreq
            return

        last_review_in_db = response.meta['last_review_in_db']

        last_date_in_page = dateparser.parse(date, ["%Y:%m:%d"])
        if last_date_in_page == 'None':
            print 'in here'
            last_date_in_page = self.parserdate(date)


        if last_review_in_db:
            if last_review_in_db > last_date_in_page:
                return

        next_page_url = self.extract_xpath(response, next_page_xpath)
        if next_page_url:
            next_page_url = get_full_url(response.url, next_page_url)
            request = Request(next_page_url, callback=self.parse_reviews)
            request.meta['asin'] = asin
            request.meta['last_review_in_db'] = last_review_in_db
            yield request




