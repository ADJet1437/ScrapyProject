# -*- coding: utf8 -*-
from datetime import datetime

import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.items import ProductIdItem
from alascrapy.lib.generic import date_format, get_full_url


class GizmodoComSpider(AlaSpider):
    name = 'gizmodo_com'
    allowed_domains = ['gizmodo.com']
    start_urls = ['https://gizmodo.com/c/reviews/other-gadgets',
                  'https://gizmodo.com/c/reviews/smartphones',
                  'https://gizmodo.com/c/reviews/wearables',
                  'https://gizmodo.com/c/reviews/laptops-tablets',
                  'https://gizmodo.com/c/reviews/cameras',
                  'https://gizmodo.com/c/reviews/smart-home',
                  'https://gizmodo.com/c/reviews/headphones',
                  'https://gizmodo.com/c/reviews/e-readers',
                  'https://gizmodo.com/c/reviews/vr']

    def __init__(self, *args, **kwargs):
        super(GizmodoComSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

    def parse_price(self, product, response):
        price_xpath = "(//h2[contains(text(),'Price')]"\
            "/following-sibling::p)/text()"
        price_str = (self.extract(response.xpath(price_xpath))).encode('utf-8')

        if price_str:
            return ProductIdItem.from_product(
                product,
                kind='price',
                value=(price_str).split("$")[1]
            )

    def parse(self, response):
        contents = response.xpath("//article")
        for content in contents:
            ori_date_str = self.extract(content.xpath(".//time/@datetime"))
            date_str = date_format(ori_date_str, '%Y-%m-%d')
            date_time = datetime.strptime(date_str, '%Y-%m-%d')
            if date_time < self.stored_last_date:
                return
            else:
                review_url = self.extract(content.xpath(
                    "./div/div/div/a/@href"))
                yield response.follow(review_url, callback=self.parse_review)

    def get_source_id(self, response):
        original_url = response.url
        # example of response.url = https://gizmodo.com/gopros-hero6-is-the-king-of-action-1820647482
        PRODUCT_INDEX = -1
        sid = original_url.split('-')[PRODUCT_INDEX]
        return sid

    def parse_review(self, response):
        product_xpaths = {"PicURL": "(//*[@property='og:image'])[1]/@content",
                          "ProductName": "(//h1[@class='review-box__title'])"
                          "[1]/text()",
                          "OriginalCategoryName": "(//header//a[2])[1]/text()"
                          }
        review_xpaths = {"TestTitle": "//*[@property='og:title']/@content",
                         "ProductName": "(//h1[@class='review-box__title'])[1]"
                         "/text()",
                         "TestSummary": "//*[@property='og:description']"
                         "/@content",
                         "Author": "//meta[@name='author']/@content",
                         "TestDateText": "//time/@datetime",
                         "TestPros": "(//h2[contains(text(),'Like')]/"
                         "following-sibling::p)[1]/text()",
                         "TestCons": "(//h2[contains(text(),'No Like')]"
                         "/following-sibling::p)[1]/text()"
                         }

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        ori_date_text = review['TestDateText']
        date_str = date_format(ori_date_text, '%Y-%m-%d')
        review['TestDateText'] = date_str
        product["source_internal_id"] = self.get_source_id(response)

        if not product['ProductName']:
            product['ProductName'] = self.extract(
                response.xpath("//*[@property='og:title']/@content"))

        if not review['ProductName']:
            review['ProductName'] = product['ProductName']

        review["DBaseCategoryName"] = "PRO"
        review["source_internal_id"] = self.get_source_id(response)
        product_id = self.parse_price(product, response)

        if review.get('TestPros', ''):
            # filter some products
            yield product_id
            yield product
            yield review
