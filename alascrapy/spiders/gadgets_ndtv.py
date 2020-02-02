# -*- coding: utf8 -*-

from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format
from alascrapy.items import CategoryItem

class GadgetsNdtvSpider(AlaSpider):
    name = 'gadgets_ndtv'
    allowed_domains = ['gadgets.ndtv.com']
    start_urls = ['http://gadgets.ndtv.com/reviews']

    def parse(self, response):
        next_page_xpath = "//div[@class='pagination']/a[contains(text(), '>')][1]/@href"
        review_url_xpath = "//div[@class='caption_box']/div[@class='caption']/a/@href"

        review_urls = self.extract_list(response.xpath(review_url_xpath))
        for review_url in review_urls:
            review_url = get_full_url(response, review_url)
            request = Request(review_url, callback=self.parse_review)
            yield request

        next_page = self.extract(response.xpath(next_page_xpath))
        next_page = get_full_url(response, next_page)
        request = Request(next_page, callback=self.parse)
        yield request

    def parse_review(self, response):
        product_xpaths = { "PicURL": "//*[@property='og:image']/@content"
                         }

        review_xpaths = { "TestTitle": "//*[@property='og:title']/@content",
                          "TestSummary": "//*[@property='og:description']/@content",
                          "Author": "//span[@rel='author']/text()",
                          "SourceTestRating": "//span[@class='rating']/text()[last()]",
                          "TestDateText": "//span[@itemprop='datePublished']/text()", 
                          "TestVerdict": "//*[@class='hreview']//*[contains(text(),'Verdict')]//following-sibling::text()[1]",
                          "TestPros":"//ul[@class='good']/li[not(@class)]/text()", 
                          "TestCons":"//ul[@class='bad']/li[not(@class)]/text()"
                        }
        category_xpath = "//div[@class='gad_breadcrums']/div[2]//span/text()"
        category_url = "//div[@class='gad_breadcrums']/div[2]//a/@href"
        category = CategoryItem()
        category["category_leaf"] = self.extract(response.xpath(category_xpath))
        category["category_path"] = category["category_leaf"]
        category["category_url"] = get_full_url(response, self.extract(response.xpath(category_url)))
        yield category

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        title = review["TestTitle"].lower()
        review["ProductName"] = title.replace("review", "").strip(":")
        if ":" in review["ProductName"]:
            review["ProductName"] = review["ProductName"].split(":")[0]
        product["ProductName"] = review["ProductName"]
        product["OriginalCategoryName"] = category['category_path']
        yield product
        
        review["DBaseCategoryName"] = "PRO"
        review["SourceTestScale"] = "5"
        if review["TestDateText"]:
            review["TestDateText"] = date_format(review["TestDateText"], "%d %B %Y")
        rating_xpath_2 = "//li[contains(text(),'Overall:')]/text()"
        pros_xpath_2 ="//ul[@class='storyelementlist'][1]//text()"
        cons_xpath_2 = "//ul[@class='storyelementlist'][2]//text()"
        if not review["SourceTestRating"]:
            review["SourceTestRating"] = get_full_url(response, self.extract(response.xpath(rating_xpath_2)))
            if review["SourceTestRating"]:
                review["SourceTestRating"] = review["SourceTestRating"].replace("Overall:", "").strip()
        if not review["TestPros"] and not review["TestCons"]:
            review["TestPros"] = self.extract_all(response.xpath(pros_xpath_2))
            review["TestCons"] = self.extract_all(response.xpath(cons_xpath_2))
        yield review
