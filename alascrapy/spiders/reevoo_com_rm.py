# -*- coding: utf8 -*-

import re

from scrapy.http import Request

from alascrapy.spiders.base_spiders.rm_spider import RMSpider
from alascrapy.lib.generic import get_full_url, date_format
from alascrapy.items import ReviewItem


class ReevooRMSpider(RMSpider):
    name = 'reevoo_com_rm'
    allowed_domains = ['reevoo_com_rm']

    source_internal_id_re = re.compile("product_(\d+)")

    def parse(self, response):
        #Must use only product_page
        category_xpaths = { "category_leaf": "//ul[@id='breadcrumbs']/li[3]//text()", #1st is home and 2nd is All products
                            "category_path": "//ul[@id='breadcrumbs']/li[3]//text()"
                          }

        product_xpaths = { "PicURL": "(//*[@property='og:image'])[1]/@content",
                           "OriginalCategoryName": "//ul[@id='breadcrumbs']/li[3]//text()",
                           "ProductName": "//h1[@id='productName']/span/text()"
                         }

        category = self.init_item_by_xpaths(response, "category", category_xpaths)
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product["OriginalCategoryName"] = category["category_path"]
        product["source_internal_id"] = None

        source_internal_id_xpath = "//div[@class='product']/@id"
        source_internal_id =  self.extract(response.xpath(source_internal_id_xpath))
        match = re.match(self.source_internal_id_re, source_internal_id)
        if match:
            product["source_internal_id"] = match.group(1)
        yield category
        yield product
        yield self.get_rm_kidval(product, response)

        reviews_xpath="//div[@class='more-reviews']/div/a[contains(@href,'page')]/@href"

        review_url = self.extract(response.xpath(reviews_xpath))
        if review_url:
            review_url = get_full_url(response, review_url)
            request = Request(review_url, callback=self.parse_reviews,
                              dont_filter=True)
            request.meta['product'] = product
            yield request

    def parse_reviews(self, response):
        product = response.meta['product']
        review_container_xpath = "//div[@id='reviews']/div[contains(@id,'review_')]"

        author_xpath = ".//h4[@class='title']/span/span/text()"
        rating_xpath = ".//span[@class='score-border']//span[@class='value']/text()"
        date_xpath = ".//span[@class='date']/text()"
        pros_xpath = ".//dd[@class='pros']/text()"
        cons_xpath = ".//dd[@class='cons']/text()"

        next_page_url_xpath = "//a[@class='next_page']/@href"

        review_containers = response.xpath(review_container_xpath)

        for review_container in review_containers:
            review = ReviewItem()
            review['DBaseCategoryName'] = "USER"
            review['ProductName'] = product['ProductName']
            review['TestUrl'] = product['TestUrl']
            review['source_internal_id'] = product['source_internal_id']
            review['SourceTestRating'] =  self.extract(review_container.xpath(rating_xpath))
            review['Author'] = self.extract(review_container.xpath(author_xpath))
            review['TestDateText'] = self.extract(review_container.xpath(date_xpath))
            review['TestDateText'] = date_format(review['TestDateText'],'%d %b %Y')
            review['TestPros'] = self.extract(review_container.xpath(pros_xpath))
            review['TestCons'] = self.extract(review_container.xpath(cons_xpath))
            if review['TestPros'] or review['TestCons']:
                yield review


        next_page_url = self.extract(response.xpath(next_page_url_xpath))
        if next_page_url:
            next_page_url = get_full_url(response, next_page_url)
            request = Request(next_page_url, 
                callback=self.parse_reviews,
                dont_filter=True)
            request.meta['product'] = product
            yield request