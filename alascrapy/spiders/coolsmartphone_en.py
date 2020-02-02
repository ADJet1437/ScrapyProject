# -*- coding: utf8 -*-
import scrapy

import re

from datetime import datetime

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider

import alascrapy.lib.dao.incremental_scraping as incremental_utils


class Coolsmartphone_enSpider(AlaSpider):
    name = 'coolsmartphone_en'
    allowed_domains = ['www.coolsmartphone.com']
    start_urls = ['https://www.coolsmartphone.com/category/reviews/']

    def __init__(self, *args, **kwargs):
        super(Coolsmartphone_enSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

    def parse(self, response):
        link_xpaths = '//header/h2/a/@href'
        links = self.extract_list(response.xpath(link_xpaths))

        for link in links:
            yield response.follow(link, callback=self.parse_review)

        next_page_xpath = '//a[@class="next page-numbers"]/@href'
        next_page = self.extract(response.xpath(next_page_xpath))

        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_review(self, response):
        product_xpaths = {
            'PicURL': '//meta[@property="og:image"]/@content',

            'OriginalCategoryName': '//meta[@property="article:tag"]'
                                    '[last()]/@content',

            'TestUrl': '//meta[@property="og:url"]/@content',
        }

        review_xpaths = {
            'TestSummary': '//*[@property="og:description"]/@content',
            'Author': '//span[@class="post-by"]/a/text()',

            'TestVerdict': '//div[@class="thecontent clearfix"]'
                           '/p[last()]/text()',

            'TestDateText': 'substring-before(//meta[@property='
                            '"article:published_time"]/@content, "T")',

            'SourceTestRating': '//div[@class="review-final-score"]/h3/text()',
            'TestUrl': '//meta[@property="og:url"]/@content',
        }

        review = self.init_item_by_xpaths(response, 'review', review_xpaths)
        product = self.init_item_by_xpaths(response, 'product', product_xpaths)

        date_text = review.get('TestDateText')
        date_time_to_compare = datetime.strptime(date_text, '%Y-%m-%d')
        if date_time_to_compare < self.stored_last_date:
            return

        title_xpath = '//meta[@property="og:title"]/@content'
        title = self.extract(response.xpath(title_xpath))

        product_name = title.split(' -')[0]

        review['TestTitle'] = title
        review['ProductName'] = product_name
        product['ProductName'] = product_name

        rating_xpath = '//div[@class="review-final-score"]/h3/text()'
        test_rating = self.extract(response.xpath(rating_xpath))
        TEST_SCALE = 100

        if test_rating:
            review['SourceTestRating'] = test_rating
            review['SourceTestScale'] = TEST_SCALE

        source_int_id_xpath = '//body[@id]/@class'
        source_int_id = self.extract(response.xpath(source_int_id_xpath))
        s_internal_id = re.findall(r'\d+', source_int_id)[0]

        review['DBaseCategoryName'] = 'PRO'
        review['source_internal_id'] = s_internal_id
        product['source_internal_id'] = s_internal_id

        yield review
        yield product
