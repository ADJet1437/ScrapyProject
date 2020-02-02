# -*- coding: utf8 -*-

from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format


class TechmagnifierSpider(AlaSpider):
    name = 'techmagnifier'
    allowed_domains = ['techmagnifier.com']
    start_urls = ['http://www.techmagnifier.com/review']

    def parse(self, response):
        article_xpath = "//article"
        next_page_xpath = "//a[@class='nextpostslink']/@href"
        review_url_xpath = ".//div[contains(@class, 'entry')]//a[@rel='bookmark']/@href"
        rating_link_xpath = "//img[contains(@title, 'Star')]/@src"

        articles = response.xpath(article_xpath)
        for article in articles:
            review_url = self.extract(article.xpath(review_url_xpath))
            review_url = get_full_url(response, review_url)
            request = Request(review_url, callback=self.parse_review)
            rating_link = self.extract(article.xpath(rating_link_xpath))
            rating_value = rating_link.split("/")[-1].replace("-stars.png", "")
            request.meta['rating_value'] = rating_value
            yield request

        next_page = self.extract(response.xpath(next_page_xpath))
        if next_page:
            next_page = get_full_url(response, next_page)
            request = Request(next_page, callback=self.parse)
            yield request
        
        
    def parse_review(self, response):
        product_xpaths = { "PicURL": "//div[@class='productzoome']/img/@src", 
                            "OriginalCategoryName":"//div[@class='breadcrumbs']//span[@property='itemListElement'][last()]//text()"
                         }

        review_xpaths = { "TestTitle": "//*[@property='og:title']/@content",
                          "TestSummary": "//*[@property='og:description']/@content",
                          "Author": "//*[@class='author-name'][1]//text()",
                          "TestVerdict": "//*[@class='entry-title'][contains(text(),'Verdict')]//following-sibling::p[1]/text()",
                          "TestDateText": "//span[@itemprop='datePublished']/text()", 
                          "TestPros":"//div[@class='pros']//p/text()", 
                          "TestCons":"//div[@class='cons']//p/text()"
                        }
        
        rating_value = response.meta['rating_value']
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        title = review["TestTitle"].lower()
        review["ProductName"] = title.replace("review", "").strip(":")
        if ":" in review["ProductName"]:
            review["ProductName"] = review["ProductName"].split(":")[0]
        review["SourceTestRating"] = rating_value
        review["DBaseCategoryName"] = "PRO"
        review["SourceTestScale"] = "5"
        if review["TestDateText"]:
            review["TestDateText"] = date_format(review["TestDateText"], "%d %B %Y")
        yield review
        
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product["ProductName"] = review["ProductName"]
        if product["OriginalCategoryName"]:
            product["OriginalCategoryName"] = product["OriginalCategoryName"].replace("Reviews", "").strip()
        yield product
