# -*- coding: utf8 -*-
import re

from scrapy.http import Request
from datetime import datetime

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.lib.generic import date_format


class TheDigitalPictureSpider(AlaSpider):
    name = 'thedigitalpicture'
    allowed_domains = ['the-digital-picture.com']
    start_urls = ['http://www.the-digital-picture.com/Reviews/']

    def __init__(self, *args, **kwargs):
        super(TheDigitalPictureSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

    def parse(self, response):
        """
        Handle the reviews index page on the-digital-picture and split it into
        pages to scrape

        :param response: The response from the requested page
        :return: Either a review or a request
        """

        review_indexes = self.extract_list(
            response.xpath('//*[@class="BlockMenu"]//li/a/@href'))

        for review_index_url in review_indexes:
            if 'the-digital-picture.com/Reviews/' in review_index_url:
                request = Request(review_index_url,
                                  callback=self.parse_review_index)
                yield request

    def parse_review_index(self, response):
        review_urls_xpath = '//div[@class="Category"]//a/@href'

        review_urls = self.extract_list(response.xpath(review_urls_xpath))
        for review_url in review_urls:
            request = Request(review_url, callback=self.parse_review)
            yield request

    def parse_review(self, response):
        category_xpaths = {
            "category_leaf": "(//ul[@itemprop='breadcrumb']/li[3])"
            "[1]/a/text()",
            "category_path": "(//ul[@itemprop='breadcrumb']/li[3])"
            "[1]/a/text()",
            "category_url": "(//ul[@itemprop='breadcrumb']/li[3])"
            "[1]/a/@href"
        }

        product_xpaths = {
            "ProductName": "//*[@itemprop='itemReviewed']/text()",
            "PicURL": "//*[@property='og:image']/@content"
        }

        review_xpaths = {
            "TestSummary": "//*[@itemprop='reviewBody']/p[1]//text()|//h2["
            "contains(text(), 'Summary')][last()]/following-sibling::p/text()",
            "SourceTestRating": "//*[@itemprop='reviewRating']/@content",
            "Author": "//*[@itemprop='author']/a/text()",
            "TestDateText": "//*[@itemprop='datePublished']/text()"
        }

        product_id_xpaths = {
            "ID_value": "//*[@class='EquipmentMenu']/"
            "span[contains(text(),'Manufacturer ID: ')]/text()"
        }

        category = self.init_item_by_xpaths(
            response, "category", category_xpaths)
        category["category_leaf"] = category["category_leaf"].replace(
            'Review', '').strip()
        yield category
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        date_str = review['TestDateText']
        if not date_str:
            text = response.text
            test_text = re.findall(r'Date/Time: ([^,]*) ', text)
            date_test = test_text[0].split(' ')[0]
            date_str = date_format(date_test, '%m/%d/%Y')
            review['TestDateText'] = date_str
        # incremental 
        date_time = datetime.strptime(date_str, '%Y-%m-%d')
        if date_time < self.stored_last_date:
            return

        # Summary
        test_summary = review['TestSummary']
        if not test_summary:
            sum_xpath = "//div[@style='margin-top:5px;']//text()"
            summary = self.extract_all(response.xpath(sum_xpath))
            review['TestSummary'] = summary

        review["TestTitle"] = product["ProductName"]
        review["TestSummary"] = re.sub(
            '\s', ' ',  review["TestSummary"], flags=re.MULTILINE)
        review["TestUrl"] = response.url
        review["DBaseCategoryName"] = "PRO"

        product["ProductName"] = product["ProductName"].replace(" Review", "")
        review["ProductName"] = product["ProductName"]

        product["TestUrl"] = response.url
        product["OriginalCategoryName"] = category["category_leaf"]

        mpn = self.init_item_by_xpaths(
            response, 'product_id', product_id_xpaths)
        if mpn["ID_value"]:
            mpn["ID_kind"] = "MPN"
            mpn["ProductName"] = product["ProductName"]
            mpn["ID_value"] = mpn["ID_value"].replace("Manufacturer ID: ", "")
            yield mpn

        yield product
        yield review
