# -*- coding: utf8 -*-

import re
from datetime import datetime
import dateparser

from urllib import unquote
from scrapy import Request

from alascrapy.items import CategoryItem, ProductItem, ReviewItem, \
    ProductIdItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import date_format, get_full_url
import alascrapy.lib.dao.incremental_scraping as incremental_utils


class PocketLintSpider(AlaSpider):
    name = 'pocket_lint'
    allowed_domains = ['pocket-lint.com']
    start_urls = ['https://www.pocket-lint.com/reviews']

    def __init__(self, *args, **kwargs):
        super(PocketLintSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        #self.stored_last_date = datetime(2019, 8, 1)

    def parse(self, response):

        review_divs_xpath = "//div[@class='content']//div"
        review_divs = response.xpath(review_divs_xpath)

        for review_div in review_divs:
            date_xpath = './/span/time/@datetime'
            dates = (review_div.xpath(date_xpath)).getall()
            for date in dates:
                review_date = date.split("+")[0].replace("T", " ")
                r_date = dateparser.parse(review_date)
                if r_date > self.stored_last_date:
                    review_urls_xpath = "./a/@href"
                    review_urls = (review_div.xpath(review_urls_xpath)).getall()
                    for review in review_urls:
                        yield Request(url=review, callback=self.parse_review)

    def parse_review(self, response):

        category_path_xpath = "//div[@class='breadcrumb']/ol/li/a/text()"
        category_leaf_xpath = "//div[@class='breadcrumb']/ol/li[2]/a/text()"
        url_xpath = "//div[@class='breadcrumb']/ol/li[2]/a/@href"
        category = CategoryItem()
        categoryurl = self.extract(response.xpath(url_xpath))
        category['category_url'] = get_full_url(response.url, categoryurl)
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ').replace('               ', '')
        if self.should_skip_category(category):
            return

        review_xpaths = {
            "TestTitle": "//header/h1/text()",
            "Author": "//span[@class='authors']/a/text()",
            "TestVerdict": "//div[@class='quick_verdict']/p/text()",
            "TestSummary": "//meta[@name='description']/@content",
            "TestPros": "//div[@class='for']/ul//li/text()",
            "TestCons": "//div[@class='against']/ul//li/text()"
        }
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        product = ProductItem()

        test_url = response.url
        internal_source_id = unquote(test_url).split('/')[-1].split('-')[0]
        review['source_internal_id'] = internal_source_id
        product['source_internal_id'] = internal_source_id
        # product name
        title = review['TestTitle']
        if 'initial' in title:
            product_name = title.split('initial')[0]
        elif 'review' in title:
            product_name = title.split('review')[0]
        else:
            product_name = title

        review['ProductName'] = product_name
        product['ProductName'] = product_name

        source_test_rating = self.extract(response.xpath(
            "//div[@class='sccore-flex']/span/span/text()"))
        if source_test_rating:
            review['SourceTestRating'] = source_test_rating
            review['SourceTestScale'] = '5'
        review['TestUrl'] = test_url

        date_str = self.extract(response.xpath("//time/@datetime"))
        date_time = date_format(date_str[0:10], "%Y-%m-%d")
        date_time_to_compare = datetime.strptime(date_time, '%Y-%m-%d')
        if self.stored_last_date > date_time_to_compare:
            return
        review['TestDateText'] = date_time
        review['DBaseCategoryName'] = 'PRO'

        product['TestUrl'] = test_url
        product['OriginalCategoryName'] = category['category_path']

        picture_src1 = self.extract(response.xpath(
            "//meta[@property='og:image']/@content"))
        picture_src = picture_src1
        # some source pic urls do not have https
        picture_src = get_full_url(response.url, picture_src)
        product['PicURL'] = picture_src

        yield review
        yield category
        yield product

        price = (self.extract(response.xpath(
                    "//p[3]/span[@class='price']/text()"))).encode('utf-8')
        if price:
            product_id = ProductIdItem()
            product_id['ID_kind'] = 'price'
            product_id['ID_value'] = price.lstrip(' £')
            product_id['ProductName'] = product_name
            product_id['source_internal_id'] = internal_source_id
            yield product_id