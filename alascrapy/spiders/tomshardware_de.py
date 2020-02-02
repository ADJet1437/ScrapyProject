# -*- coding: utf8 -*-
from datetime import datetime

import dateparser

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url
from alascrapy.items import ReviewItem, ProductItem, CategoryItem
from alascrapy.lib import extruct_helper

import alascrapy.lib.dao.incremental_scraping as incremental_utils

# stop scheduling this spider due to the poor quality of the reviews. 
# 2018-08-30


class Tomshardware_deSpider(AlaSpider):
    name = 'tomshardware_de'
    allowed_domains = ['tomshw.de']
    start_urls = ['https://www.tomshw.de/testberichte/']

    def __init__(self, *args, **kwargs):
        super(Tomshardware_deSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):
        print('1. got into the parse')
        review_xpath = '//h2[@class="entry-title"]/a/@href'
        review_urls = self.extract_list(response.xpath(review_xpath))
        for review_url in review_urls:
            review_url = get_full_url(response, review_url)
            yield response.follow(url=review_url,
                                  callback=self.parse_review)

        # get the date of latest review of the page
        latest_date_xpath = "(//time)[1]/text()"
        latest_date_text = self.extract(response.xpath(latest_date_xpath))
        latest_date = dateparser.parse(latest_date_text)
        if latest_date and latest_date < self.stored_last_date:
            return

        # Next page
        next_page_url_re = r'(.*)[0-9]+'
        current_page_num_re = r'-([0-9]+)'
        page_xpath = "//meta[@property='og:url']/@content"
        if response.xpath(page_xpath).re_first(next_page_url_re):
            next_page_url = response.xpath(page_xpath).re_first\
                    (next_page_url_re) + str(int(float(response.xpath
                    (page_xpath).re_first(current_page_num_re))) + 1) + ".html"
        else:
            next_page_url = 'http://www.tomshardware.de/artikel/testbericht' \
                            '/page-2.html'
        if next_page_url:
            yield response.follow(url=next_page_url, callback=self.parse)

    def parse_review(self, response):
        print('2. got to the parse_review page with {}').format(response.url)
        review = ReviewItem()
        category = CategoryItem()

        category_json_ld = extruct_helper.extract_json_ld(response.body,
                                                          'BreadcrumbList')
        if not category_json_ld:
            print('no category can be found')
            return
        category = extruct_helper.category_item_from_breadcrumbs_json_ld(
            category_json_ld)
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = {
            "PicURL": "//meta[@property='og:image']/@content",
            #"ProductName": "//meta[@property='og:title']/@content"
        }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        if category:
            CategoryName = category['category_path']
            product["OriginalCategoryName"] = CategoryName.replace\
                (' | Testbericht', '')
        source_internal_id_re = r'Review_([0-9]+)'
        source_internal_id_xpath = "//article[contains(@id,'Review')]/@id"
        product["source_internal_id"] = response.xpath\
            (source_internal_id_xpath).re_first(source_internal_id_re)
        product_name_re = r'.de/(.*),testberichte'
        product_name_xpath = "//meta[@property='og:url']/@content"
        product_name = response.xpath(product_name_xpath).re_first\
            (product_name_re)
        product["ProductName"] = product_name.replace('-', ' ')
        yield product

        review_json_ld = extruct_helper.extract_json_ld\
            (response.body, 'Article')
        if review_json_ld:
            review = extruct_helper.review_item_from_article_json_ld(
                    review_json_ld, review)
        review["ProductName"] = product["ProductName"]
        review["DBaseCategoryName"] = "PRO"
        review["TestUrl"] = product["TestUrl"]
        review["source_internal_id"] = product["source_internal_id"]
        yield review




