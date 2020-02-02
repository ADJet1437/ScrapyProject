# -*- coding: utf8 -*-
from datetime import datetime
import re
from scrapy.http import Request
import dateparser

from alascrapy.items import CategoryItem
from alascrapy.lib.generic import date_format
import alascrapy.lib.dao.incremental_scraping as incremental_utils
import alascrapy.lib.extruct_helper as extruct_helper
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider

class TomsguideEnSpider(AlaSpider):
    name = 'tomsguide_en'
    allowed_domains = ['tomsguide.com']
    start_urls = ['https://www.tomsguide.com/articles/review',
                  'https://www.tomsguide.com/articles/hands-on']

    def __init__(self, *args, **kwargs):
        super(TomsguideEnSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(2019, 1, 1)

    def parse(self, response):

        review_divs_xpath = "//div[@id='content']"
        review_divs = response.xpath(review_divs_xpath)

        for review_div in review_divs:
            date_xpath = './/header/p/time/@datetime'
            dates = (review_div.xpath(date_xpath)).getall()
            for date in dates:
                date = str(date).split("T")[0]
                review_date = datetime.strptime(date, '%Y-%m-%d')
                if review_date > self.stored_last_date:
                    review_urls_xpath = ".//div[@class='listingResults ']/div/a/@href"
                    review_urls = (review_div.xpath(review_urls_xpath)).getall()
                    for review in review_urls:
                        yield Request(url=review, callback=self.parse_review_page) 

        next_page_xpath = "//span[@class='listings-pagination-button listings-next ']/a/@href"
        next_page = self.extract(response.xpath(next_page_xpath))

        review_date_xpath = '(//header/p/time/@datetime)[last()]'
        review_date = self.extract(response.xpath(review_date_xpath))
        review_date = str(review_date).split("T")[0]
        oldest_review_date = datetime.strptime(review_date, "%Y-%m-%d")

        if next_page:
            if oldest_review_date < self.stored_last_date:
                yield response.follow(next_page, callback=self.parse)
        else:
            print('No next page found: {}'.format(response.url))

    def parse_review_page(self, response):
        
        original_url = response.url

        category_leaf_xpath = "//span[@class='no-wrap move-on-reviews']/a/text()"
        category_path_xpath = "//span[@class='no-wrap move-on-reviews']/a/text()"
        category_url_xpath = "//span[@class='no-wrap move-on-reviews']/a/@href"
        category = CategoryItem()
        category['category_url'] = self.extract(
            response.xpath(category_url_xpath))
        category['category_leaf'] = self.extract(
            response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(
            response.xpath(category_path_xpath), ' | ')

        if self.should_skip_category(category):
            return

        product_xpaths = {
            "ProductName": "//h1[@itemprop='headline']/text()",
            "PicURL": "//meta[@property='og:image']/@content",
        }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['TestUrl'] = original_url
    
        review_xpaths = {
            "TestTitle": "//*[@property='og:title']/@content",
            "Author": "//span[@class='no-wrap by-author']/a/span/text()",

            "TestSummary": "//meta[@name='description']/@content",

            "TestVerdict": "(//div[@id='article-body']/p/text())[last()]",
        }
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        review['TestUrl'] = response.url

        date_xpath_alt = "//meta[@name='pub_date']/@content"
        date = self.extract(response.xpath(date_xpath_alt))
        review["TestDateText"] = date.split("T")[0]

        rating_xpath = "//p[@class='byline']/span[@class='chunk rating']/span[@class='icon icon-star']"
        rating = self.extract_list(response.xpath(rating_xpath))
        if rating:
            review['SourceTestRating'] = rating.count('<span class="icon icon-star"> </span>')
            review['SourceTestScale'] = '5'

        review["DBaseCategoryName"] = "PRO"

        product_name = self.clean_product_name(review.get('TestTitle', ''))
        review['ProductName'] = product_name
        product['ProductName'] = product_name

        source_internal_id = str(response.url).split('/')[4]
        review['source_internal_id'] = source_internal_id
        product['source_internal_id'] = source_internal_id

        yield product
        yield review

    def clean_product_name(self, test_title):
        test_title = test_title.split(':')[0]
        test_title = test_title.replace('Review', '')
        test_title = test_title.strip()
        test_title = test_title.replace(' Hands-on', '')
        test_title = test_title.replace(' Hands-On', '')
        return test_title