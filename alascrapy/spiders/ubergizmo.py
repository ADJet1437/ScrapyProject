# -*- coding: utf8 -*-
import re
from datetime import datetime

from alascrapy.lib.generic import get_full_url, date_format
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils


class ubergizmoSpider(AlaSpider):
    name = 'ubergizmo'
    allowed_domains = ['ubergizmo.com']
    start_urls = ['https://www.ubergizmo.com/topic/reviews/']

    def __init__(self, *args, **kwargs):
        super(ubergizmoSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):
        print(response.url)
        print('==============================')
        review_url_xpaths = "//div[@class='postcontainer_home']/div/a/@href"
        review_urls = self.extract_list(response.xpath(review_url_xpaths))
        for review_url in review_urls:
            yield response.follow(url=review_url, callback=self.parse_review)
        # extract an oldest date on each page to decide whether go to next page
        oldest_date_time_xpath = "(//span[@class='byline'])[last()]/text()"
        original_datetime_str = self._get_date_time(response,
                                                    oldest_date_time_xpath)
        oldest_date_to_compare = self._get_date_time_to_compare(
            response, original_datetime_str)[1]
        next_page_xpath = "//div[@class='paginationcontainer']/div/a/@href"
        next_page = self.extract(response.xpath(next_page_xpath))
        if next_page:
            if oldest_date_to_compare < self.stored_last_date:
                return
            yield response.follow(next_page, callback=self.parse)
        else:
            print('No next page found: {}'.format(response.url))

    def parse_review(self, response):
        product_xpaths = {
            "PicURL": "//meta[@property='og:image']/@content",
            "OriginalCategoryName": "//span[@id='breadcrumbs']//a/text()"
        }

        review_xpaths = {
            "TestTitle": "//meta[@property='og:title']/@content",
            "TestSummary": "//meta[@property='og:description']/@content",
            "Author": "//span/a[@rel='author']/text()",
            "TestPros": "//div[@class='review_pros_container']/ul//li/text()",
            "TestCons": "//div[@class='review_cons_container']/ul//li/text()",
        }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        # product name
        product_name = ""
        title_xpath = "//meta[@property='og:title']/@content"
        title = self.extract(response.xpath(title_xpath))
        if ':' in title:
            product_name = title.split(':')[0].replace('Review', '')
        else:
            product_name = title.replace('Review', '')
        # source_internal_id
        source_int_id = self.extract(response.xpath(
            "//script[contains(text(),'article')]"))
        source_int_id_to_join = re.findall(r'article_(\d+)', source_int_id)
        source_internal_id = source_int_id_to_join[0]
        if review.get('TestPros', ''):
            # filter out some products do not have pros, cons
            date_time_xpath = "(//span[@class='byline'])/text()"
            original_datetime_str = self._get_date_time(response,
                                                        date_time_xpath)
            if original_datetime_str:
                date, date_to_compare = self._get_date_time_to_compare(
                    response, original_datetime_str)
                if date_to_compare < self.stored_last_date:
                    return
                review["TestDateText"] = date
                review["DBaseCategoryName"] = "PRO"
                review["ProductName"] = product_name
                Source_Test_Rating_xpath = self.extract(
                    response.xpath("//div[@class='postreviewrating']"))
                source_rate = re.findall(r'^\D*(\d+)',
                                         Source_Test_Rating_xpath)
                Source_Test_Rating = source_rate[0]
                if Source_Test_Rating:
                    TEST_SCALE = 10
                    review["SourceTestRating"] = Source_Test_Rating
                    review["SourceTestScale"] = TEST_SCALE
                review["source_internal_id"] = source_internal_id
                yield review

                product['ProductName'] = product_name
                product["source_internal_id"] = source_internal_id
                if product.get('OriginalCategoryName', ''):
                    ocn = product['OriginalCategoryName']
                    new_ocn = ocn.replace(' ', ' | ')
                    product['OriginalCategoryName'] = new_ocn
                yield product

    def _get_date_time_to_compare(self, response, date_str):
        date_time = date_format(date_str, '%d %b %Y')
        date_to_compare = datetime.strptime(date_time, '%Y-%m-%d')
        return date_time, date_to_compare

    def _get_date_time(self, response, date_xpath):
        date_str = self.extract_all(response.xpath(date_xpath))
        original_datetime_str = date_str.split(' ')[2]
        return original_datetime_str
