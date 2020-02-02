# -*- coding: utf8 -*-

from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format


class PcquestSpider(AlaSpider):
    name = 'pcquest'
    allowed_domains = ['pcquest.com']
    start_urls = ['http://www.pcquest.com/']
    
    def parse(self, response):
        category_xpath = "//ul[@rel='Main Menu']/li[2]//ul[@class='sub-menu']//a/@href"
        category_urls = self.extract_list(response.xpath(category_xpath))
        for category_url in category_urls:
            category_url = get_full_url(response, category_url)
            request = Request(category_url, callback=self.parse_category)
            yield request

    def parse_category(self, response):
        next_page_xpath = "//a[@class='next page-numbers']/@href"
        review_url_xpath = "//div[@class='home-container']//h3/a/@href"
        category_name_xpath = "//div[@class='main-title']/h2//text()"

        review_urls = self.extract_list(response.xpath(review_url_xpath))
        for review_url in review_urls:
            review_url = get_full_url(response, review_url)
            request = Request(review_url, callback=self.parse_review)
            request.meta['category_name'] = self.extract(response.xpath(category_name_xpath))
            yield request

        next_page = self.extract(response.xpath(next_page_xpath))
        next_page = get_full_url(response, next_page)
        request = Request(next_page, callback=self.parse_category)
        yield request

    def parse_review(self, response):
        product_xpaths = { "PicURL": "//*[@property='og:image']/@content"
                         }

        review_xpaths = { "TestTitle": "//*[@property='og:title']/@content",
                          "TestSummary": "//*[@property='og:description']/@content",
                          "Author": "//a[@rel='author']/text()",
                          "TestDateText": "//*[contains(@property, 'published_time')]/@content", 
                        }
        category_name = response.meta['category_name']
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        product["ProductName"] = review['TestTitle']
        product["OriginalCategoryName"] = category_name
        yield product
        
        review["ProductName"] = product["ProductName"]
        review["DBaseCategoryName"] = "PRO"
        review["SourceTestScale"] = "5"
        if review["TestDateText"]:
            review["TestDateText"] = date_format(review["TestDateText"], "%d %B %Y")
        yield review
