# -*- coding: utf8 -*-

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format

from alascrapy.items import CategoryItem

import alascrapy.lib.dao.incremental_scraping as incremental_utils

from datetime import datetime
import dateparser
import re

class Techpulse_BeSpider(AlaSpider):
    name = 'techpulse_be'
    allowed_domains = ['techpulse.be']
    start_urls = ['http://www.techpulse.be/review/']

    review_url_xpath = "//div[@class='content']/a"
    last_date_xpath = "(//span[@class='post-date'])[last()]/text()"

    def __init__(self, *args, **kwargs):
        super(Techpulse_BeSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970,1,1)

    def parse(self, response):
        next_page_xpath = "(//*[@rel='next'])[1]/@href"

        reviews = response.xpath(self.review_url_xpath)
        for review in reviews:
            yield response.follow(review, callback=self.parse_review)

        last_date_text = self.extract(response.xpath(self.last_date_xpath))
        last_date_text = last_date_text.split(' om')[0]

        last_date = dateparser.parse(last_date_text)
        if last_date and last_date < self.stored_last_date:
            return

        next_page_url = self.extract(response.xpath(next_page_xpath))
        if next_page_url:
            yield response.follow(next_page_url, callback=self.parse)
    
    def parse_review(self, response):
        product_xpaths = {
                "PicURL":"(//*[@property='og:image'])[1]/@content"
            }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)

        category = self.get_category(response)
        if category:
            yield category
            if self.should_skip_category(category):
                return
            product['OriginalCategoryName'] = category['category_path']

        review_xpaths = {
                "SourceTestRating":"//span[contains(@class,'score')]/text()",
                "TestDateText":"//meta[@property='article:published_time']/@content",
                "TestPros":"//ul[@class='pros']//li//text()",
                "TestCons":"//ul[@class='cons']//li//text()",
                "TestSummary":"//meta[@property='og:description']/@content",
                "TestVerdict":"string(//*[text()='Conclusie']/following::p)",
                "Author":"//p[@class='meta']/a/text()",
                "TestTitle":"//*[@property='og:title']/@content",
            }
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        review['SourceTestRating'] = review['SourceTestRating'].split('/')[0]

        review_rating = review.get('SourceTestRating', 0)
        if review_rating and float(review_rating) == 0:
            review['SourceTestRating'] = ''

        if review and review['TestTitle']:
            title = review["TestTitle"].lower()
            if ":" in title:
                all_title_parts = title.split(":")
                for part in all_title_parts:
                    if 'review' in part:
                        review["ProductName"] = part.replace("review", "")
                        break

                if not review.get("ProductName"):
                    review["ProductName"] = all_title_parts[0]

            else:
                review["ProductName"] = title.replace("review", "")

            review["ProductName"] = review["ProductName"].strip("-: ")
            product["ProductName"] = review["ProductName"]

        source_internal_id_re = '/[^/]+/([0-9]+)/'
        match = re.search(source_internal_id_re, response.url)
        if match:
            source_internal_id = match.group(1)
            product['source_internal_id'] = source_internal_id
            review['source_internal_id'] = source_internal_id

        review['SourceTestRating'] = review['SourceTestRating'].split('/')[0]
        review["DBaseCategoryName"] = "PRO" 
        review["SourceTestScale"] = "10" 
        if review["TestDateText"]:
            review["TestDateText"] = date_format(review["TestDateText"], "%Y-%m-%d")

        yield product
        yield review

    def get_category(self, response):
        category_tags = ('bluetoothspeaker', 'speaker', 'drone', 'laptop', 'e-reader', 'tablet',
                         '3d-printer', 'router', 'webcam', 'projector', 'ssd',
                         'fitnesstracker', 'headset', 'smartwatch',
                         'smartphone', 'monitor', 'speaker', 'desktop')

        tag_xpath = "//meta[@property='article:tag']/@content"
        page_tags = self.extract_list(response.xpath(tag_xpath))

        print response.url
        print page_tags

        category_name = ''
        for category_tag in category_tags:
            if category_tag in page_tags:
                category_name = category_tag
                break

        if category_name:
            category = CategoryItem()
            category['category_path'] = category_name
            return category
