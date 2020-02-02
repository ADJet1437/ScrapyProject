#!/usr/bin/env python

import re

from scrapy.http import Request

from alascrapy.items import CategoryItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import date_format

class HDblogItSpider(AlaSpider):
    name = 'hdblog_it'
    allowed_domains = ["hdblog.it"]
    start_urls = ['http://www.hdblog.it/recensioni/']

    product_name_re = re.compile("^(.*):.*")

    def parse(self, response):
        category_name_xpath = './span/text()'
        category_url_xpath = './@href'
        category_list_sel = response.xpath("//a[@class='review-item']")

        for category_sel in category_list_sel:
            category = CategoryItem()
            category['category_url'] = self.extract(category_sel.xpath(category_url_xpath))
            category['category_leaf'] = self.extract(category_sel.xpath(category_name_xpath))
            category['category_path'] = category['category_leaf']

            request = Request(category['category_url'],
                              callback=self.parse_category)
            request.meta['category']=category
            yield category
            yield request

    def parse_category(self, response):
        review_urls_xpath = "//article[@class='review_list_1']/a[1]/@href"
        next_page_xpath = "//a[contains(text(),'Prossima')]/@href"

        review_urls = self.extract_list(response.xpath(review_urls_xpath))
        for review_url in review_urls:
            request = Request(review_url, callback=self.parse_review)
            request.meta['category']=response.meta['category']
            yield request

        next_page_url = self.extract(response.xpath(next_page_xpath))
        if next_page_url:
            request = Request(next_page_url, callback=self.parse_category)
            request.meta['category']=response.meta['category']
            yield request


    def parse_review(self, response):
        category = response.meta['category']
        product_xpaths = { "PicURL": "//meta[@property='og:image']/@content"
                         }
        pic_alt_xpath = "(//div[@class='imageblock'])[1]//img/@src"

        review_xpaths = { "TestTitle": "//div[@id='hero']/h2/text()",
                          "TestSummary": "(//div[@class='textblock']/p)[1]//text()",
                          "TestDateText": "//div[@id='hero']/p/text()"
                        }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        #other field
        product["OriginalCategoryName"] = category['category_path']
        matches = re.search(self.product_name_re, review['TestTitle'])
        if matches:
             product['ProductName'] = matches.group(1)
        else:
            product['ProductName'] = review['TestTitle']

        if not product["PicURL"]:
            product["PicURL"] = self.extract(response.xpath(pic_alt_xpath))

        review["TestUrl"] = product["TestUrl"]
        review["ProductName"] = product["ProductName"]
        review["DBaseCategoryName"] = "PRO"
        review["TestDateText"] = date_format(review["TestDateText"], "%d %b %Y")
        yield product
        yield review

