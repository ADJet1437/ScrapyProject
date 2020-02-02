# -*- coding: utf-8 -*-

import dateparser
from datetime import datetime

from dateutil.parser import parse

from scrapy import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format
from alascrapy.items import CategoryItem

from alascrapy.lib import extruct_helper
import alascrapy.lib.dao.incremental_scraping as incremental_utils


class TechgearlabComSpider(AlaSpider):
    name = 'techgearlab_com'
    allowed_domains = ['techgearlab.com']
    start_urls = ['https://www.techgearlab.com/reviews']

    def __init__(self, *args, **kwargs):
        super(TechgearlabComSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):
        all_categories_xpath = '//div[@class="inline tag_list"]/ul/li/a/@href'
        all_categories_urls = self.extract_list(
            response.xpath(all_categories_xpath)
        )
        for category_url in all_categories_urls:
            category_url = get_full_url(response, category_url)
            request = Request(category_url, callback=self.parse_category)
            yield request

    def parse_category(self, response):
        latest_review_date_xpath = "//span[@class='tag_tile_age']//text()"
        next_page_xpath = "(//*[@rel='next'])[1]/@href"
        review_url_xpath = "//div[@class='tag_tile_text_area']/a/@href"

        review_urls = self.extract_list(response.xpath(review_url_xpath))
        for review_url in review_urls:
            review_url = get_full_url(response, review_url)
            request = Request(review_url, callback=self.parse_review)
            yield request

        # incremental scraping, avoid scrapy the reviews already exist
        latest_review_date_text = self.extract_xpath(
            response, latest_review_date_xpath
        )
        latest_review_date = dateparser.parse(
            latest_review_date_text,
            date_formats=['%Y-%m-%d']
        )
        if latest_review_date and latest_review_date < self.stored_last_date:
            return

        next_page = self.extract(response.xpath(next_page_xpath))
        if next_page:
            next_page = get_full_url(response, next_page)
            request = Request(next_page, callback=self.parse_category)
            yield request

    def parse_review(self, response):
        product_xpaths = {"PicURL": "//*[@property='og:image']/@content"}

        review_xpaths = {
            "TestTitle": "//*[@property='og:title']/@content",
            "TestSummary": '//meta[@property="og:description"]/@content',
            "TestVerdict": '//a[@id="conclusion"]/following::p[1]/text()',
            "TestPros": '//div[@class="iconProText"]/text()',
            "TestCons": '//div[@class="iconConText"]/text()',
            'Author': '//div[@class="small"]/a/text()',
        }

        product_name = ''
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        # utilize structured data
        review_json_ld = extruct_helper.extract_json_ld(
            response.text, 'Review')
        if review_json_ld:
            review = extruct_helper.review_item_from_review_json_ld(
                review_json_ld, review)
            product_name = review_json_ld.get(
                'itemReviewed', {}).get('name', '')
            product_name = product_name.split('review')[0].strip()

        # incremental
        if review.get('TestDateText', ''):
            review['TestDateText'] = date_format(review['TestDateText'], '')

        else:
            test_date_xpath = '//div[@class="small"][2]/text()'
            test_date = self.extract(response.xpath(test_date_xpath))
            test_date = parse(test_date)
            test_date = test_date.strftime("%Y-%m-%d")
            review['TestDateText'] = test_date

        if not product_name:
            title_xpath = "//h1/text()"
            title = self.extract(response.xpath(title_xpath))
            if title:
                product_name = title.split('review')[0].strip()

        product['ProductName'] = product_name
        review['ProductName'] = product['ProductName']

        category_path_xpath = "//span[@itemprop='name']/text()"
        all_category_names = self.extract_all(
            response.xpath(category_path_xpath), separator=' | ')
        product['OriginalCategoryName'] = all_category_names


        source_int_id = response.url
        source_int_id = source_int_id.split('/')[-1]
        product['source_internal_id'] = source_int_id
        review['source_internal_id'] = source_int_id

        if product.get('OriginalCategoryName', ''):
            category = CategoryItem()
            category['category_path'] = product['OriginalCategoryName']
            yield category

        yield product

        award_xpath = "//td/div[2]/img[contains(@alt, 'Award')]"
        award = response.xpath(award_xpath)
        if award:
            award_name = self.extract_xpath(award, './@alt')
            award_image_url = self.extract_xpath(award, './@src')
            if award_name and award_image_url:
                review['award'] = 'TechGearLab ' + award_name
                review['AwardPic'] = award_image_url

        review["DBaseCategoryName"] = "PRO"

        yield review
