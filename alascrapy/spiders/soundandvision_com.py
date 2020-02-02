# -*- coding: utf8 -*-
import re

from datetime import datetime
import dateparser
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import CategoryItem


class Soundandvision_comSpider(AlaSpider):
    name = 'soundandvision_com'
    allowed_domains = ['soundandvision.com']
    start_urls = ['https://www.soundandvision.com/equipment-reviews']

    #custom_settings = {'COOKIES_ENABLED': True,
    #                   'DOWNLOAD_DELAY': 8}
    def __init__(self, *args, **kwargs):
        super(Soundandvision_comSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):
        category_xpath="//div[@class='listcell2']/a/@href"
        category_urls = self.extract_list(response.xpath(category_xpath))
        for category_url in category_urls:
            category_url = get_full_url(response, category_url)
            yield response.follow(url=category_url, callback=self.parse_category)

    def parse_category(self, response):
        latest_date_xpath = "//div[contains(@class,'row-first')]/span[contains(@class,'field-created')]/span[contains(@class,'field')]/text()"

        # get the date of latest review of the page
        latest_date_text = self.extract(response.xpath(latest_date_xpath))
        latest_date = dateparser.parse(latest_date_text)

        if latest_date and latest_date < self.stored_last_date:
            return

        product_xpath = "//div[contains(@class,'views-field-title')]//a/@href"
        product_urls = self.extract_list(response.xpath(product_xpath))
        for product_url in product_urls:
            product_url = get_full_url(response, product_url)
            yield response.follow(url=product_url, callback=self.parse_review)

        next_page_xpath = "//a[contains(@title,'next')]/@href"
        next_page_url = self.extract(response.xpath(next_page_xpath))
        next_page_url = get_full_url(response,next_page_url)
        # go to next page
        if next_page_url:
            yield response.follow(url=next_page_url, callback=self.parse_category)

    def parse_review(self, response):
        product_xpaths = {
            "PicURL": "(//meta[@property='og:image']/@content)",
        }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product_name_xpath = "//meta[@itemprop='name']/@content"
        product_name = self.extract(response.xpath(product_name_xpath))
        product_name = product_name.replace('Review','')
        product["ProductName"] = product_name
        source_internal_id_xpath = "//link[@rel='shortlink']/@href"
        source_internal_id_re = r'node/([0-9]+)'
        product['source_internal_id'] = response.xpath(source_internal_id_xpath).re_first(source_internal_id_re)
        original_category_xpath = "//h1/a[contains(@href,'category')]/text()"
        original_category = self.extract(response.xpath(original_category_xpath))
        original_category = original_category.replace('REVIEWS', '')
        product["OriginalCategoryName"] = original_category

        category = CategoryItem()
        category['category_path'] = original_category
        yield category
        yield product

        review_xpaths = {
            "TestTitle": "//*[@property='og:title']/@content",
            "TestSummary": "//div[@class='field-item even']/p[2]/text()",
            "Author": "//div[contains(@class,'submitted-author')]/a/text()",
            "TestDateText": "//meta[@property='article:published_time']/@content",
        }
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        if review["TestDateText"]:
            review["TestDateText"] = date_format(review["TestDateText"], "%Y-%m-%d")

        review["ProductName"] = product["ProductName"]
        review["DBaseCategoryName"] = "PRO"
        review['source_internal_id'] = product['source_internal_id']

        pro_list_xpath = "//b[./text()='Plus']/following-sibling::text()"
        pro_list = self.extract_list(response.xpath(pro_list_xpath))

        con_list_xpath = "//b[./text()='Minus']/following-sibling::text()"
        con_list = self.extract_list(response.xpath(con_list_xpath))

        # the xpath for pro_list extract both pros and cons, remove cons from pro_list
        pro_list = [item for item in pro_list if item not in con_list]

        review['TestPros'] = '; '.join(pro_list)
        review['TestCons'] = '; '.join(con_list)

        award_xpath = "//div[contains(@class,'rating')]/img/@src"
        award_url = self.extract(response.xpath(award_xpath))
        award_url = get_full_url(response, award_url)
        review['AwardPic'] = award_url
        if award_url:
            review['award'] = 'Sound & Vision TOP PICK'

        yield review












