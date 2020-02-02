# -*- coding: utf8 -*-

from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format


class GizmodoInSpider(AlaSpider):
    name = 'gizmodo_in'
    allowed_domains = ['gizmodo.in']
    start_urls = ['http://www.gizmodo.in/topic/reviews']

    def parse(self, response):
        next_page_xpath = "//a[@class='next']/@href"
        review_url_xpath = "//div[@class='lhs']//div[@class='description']/h2/a/@href"

        review_urls = self.extract_list(response.xpath(review_url_xpath))
        for review_url in review_urls:
            review_url = get_full_url(response, review_url)
            request = Request(review_url, callback=self.parse_review)
            yield request

        next_page = self.extract(response.xpath(next_page_xpath))
        if next_page:
            next_page = get_full_url(response, next_page)
            request = Request(next_page, callback=self.parse)
            yield request
        
        
    def parse_review(self, response):
        product_xpaths = { "PicURL": "//*[@property='og:image']/@content"
                         }

        review_xpaths = { "TestTitle": "//*[@property='og:title']/@content",
                          "TestSummary": "//meta[@name='description']/@content",
                          "Author": "//span[@class='author']/text()",
                          "TestVerdict": "//*[contains(text(),'Buy It')]//ancestor-or-self::h4//following-sibling::p[1]//text()",
                          "TestDateText": "//span[@class='metadata']/text()"
                        }
                        
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        title = review["TestTitle"].lower()
        review["ProductName"] = title.replace("review", "").strip(":")
        if ":" in review["ProductName"]:
            review["ProductName"] = review["ProductName"].split(":")[0]
        review["DBaseCategoryName"] = "PRO"
        if review["TestDateText"]:
            review["TestDateText"] = date_format(review["TestDateText"], "%d %B %Y")
        if not review["Author"]:
            review["Author"] = self.extract(response.xpath("//span[@class='author']//text()"))
        if not review["TestVerdict"]:
            review["TestVerdict"] = self.extract_all(response.xpath("//*[contains(text(),'Buy It')]//ancestor-or-self::h2//following-sibling::p[1]//text()"))
        if not review["TestVerdict"]:
            review["TestVerdict"] = self.extract_all(response.xpath("//*[contains(text(),'Buy It')]//ancestor-or-self::h3//following-sibling::p[1]//text()"))
        if not review["TestVerdict"]:
            review["TestVerdict"] = self.extract_all(response.xpath("//*[contains(text(),'buy it')]//following-sibling::text()[1]"))
        if not review["TestVerdict"]:
            review["TestVerdict"] = self.extract_all(response.xpath("//*[contains(text(),'Summary')]//following-sibling::text()[1]"))
        yield review
        
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product["ProductName"] = review["ProductName"]
        yield product
