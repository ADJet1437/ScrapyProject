# -*- coding: utf8 -*-

from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format


class TimesofindiaIndiatimesSpider(AlaSpider):
    name = 'timesofindia_indiatimes'
    allowed_domains = ['timesofindia.indiatimes.com']
    start_urls = ['http://timesofindia.indiatimes.com/tech/reviews']


    def parse(self, response):
        next_page_xpath = "//a[@class='next']/@href"
        review_url_xpath = "//div[@class='column1']//h4/a/@href"
        
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
                          "TestSummary": "//*[@name='og:description']/@content",
                          "Author": "//span[@itemprop='reviewer']/text()",
                          "SourceTestRating": "//div[contains(@class, 'expert-rating')]//span[@itemprop='rating']/text()",
                          "TestDateText": "//div[@class='review']//span[@class='metadata']/text()[last()]",
                          "TestPros":"//div[@class='features']/div/text()", 
                          "TestVerdict":"//div[@class='Normal']/text()[last()]"
                        }

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        
        title = review["TestTitle"].lower()
        review["ProductName"] = title.replace("review", "").strip(":")
        if ":" in review["ProductName"]:
            review["ProductName"] = review["ProductName"].split(":")[0]
        review["ProductName"] = review["ProductName"].replace("- the times of india", "").strip()
        product["ProductName"] = review["ProductName"]
        yield product
        
        review["DBaseCategoryName"] = "PRO"
        review["SourceTestScale"] = "5"
        review["ProductName"] = product["ProductName"]
        if review["TestDateText"]:
            review["TestDateText"] = date_format(review["TestDateText"], "%d %B %Y")
        yield review
