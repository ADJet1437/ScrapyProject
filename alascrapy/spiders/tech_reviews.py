# -*- coding: utf8 -*-

from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format


class TechReviewsSpider(AlaSpider):
    name = 'tech_reviews'
    allowed_domains = ['tech-reviews.co.uk']
    start_urls = ['http://tech-reviews.co.uk/category/reviews/']
                        

    def parse(self, response):
        next_page_xpath = "//a[@class='next page-numbers']/@href"
        review_url_xpath = "//h2[@class='home']/a/@href"
        
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
        product_xpaths = { "PicURL": "//*[@property='og:image']/@content", 
                            "OriginalCategoryName":"//a[@rel='category tag'][not(contains(text(),'Reviews'))][1]/text()"
                         }

        review_xpaths = { "TestTitle": "//*[@property='og:title']/@content",
                          "TestSummary": "//*[@property='og:description']/@content",
                          "Author": "//a[@rel='author']/text()",
                          "TestDateText": "//time[@class='time']/@datetime",
                          "TestPros":"//div[@class='pros-cons']/ul[@class='left']//li//text()", 
                          "TestCons":"//div[@class='pros-cons']/ul[@class='right']//li//text()",
                          "TestVerdict":"//div[@id='verdict']/p//text()"
                        }

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        
        product["ProductName"] = review["TestTitle"].replace("Review", "").strip()
        yield product
        
        review["DBaseCategoryName"] = "PRO"
        if review["TestDateText"]:
            review["TestDateText"] = date_format(review["TestDateText"], "%d %B %Y")
            review["ProductName"] = product["ProductName"]
            if not review["TestVerdict"]:
                verdict_page_xpath = "//header/p/a[last()]/@href"
                test_verdict_xpath = "//*[contains(text(),'Conclusion')]//following-sibling::p[1]/text()"
                test_pros_xpath = "//*[contains(text(),'Pros')]//following-sibling::ul[1]/li/text()"
                test_cons_xpath = "//*[contains(text(),'Cons')]//following-sibling::ul[1]/li/text()"
                verdict_page_url = self.extract(response.xpath(verdict_page_xpath))
                if verdict_page_url:
                    verdict_page_url = get_full_url(response, verdict_page_url)
                    request = Request(verdict_page_url, callback=self.get_test_verdict)
                    request.meta['review'] = review
                    request.meta['test_verdict_xpath'] = test_verdict_xpath
                    request.meta['test_pros_xpath'] = test_pros_xpath
                    request.meta['test_cons_xpath'] = test_cons_xpath
                    yield request
                else:
                    review["TestPros"] = self.extract(response.xpath(test_pros_xpath))
                    review["TestCons"] = self.extract(response.xpath(test_cons_xpath))
                    review["TestVerdict"] = self.extract(response.xpath(test_verdict_xpath))
                    if not review["TestVerdict"]:
                        review["TestVerdict"] =  self.extract(response.xpath("//*[contains(text(),'Verdict')]//following-sibling::p[1]/text()"))
                    yield review
        else:
            yield review
            
    def get_test_verdict(self, response):
        review = response.meta['review']
        test_verdict_xpath = response.meta['test_verdict_xpath']
        test_pros_xpath = response.meta['test_pros_xpath']
        test_cons_xpath = response.meta['test_cons_xpath']
        review["TestPros"] = self.extract(response.xpath(test_pros_xpath))
        review["TestCons"] = self.extract(response.xpath(test_cons_xpath))
        review["TestVerdict"] = self.extract(response.xpath(test_verdict_xpath))
        if not review["TestVerdict"]:
            review["TestVerdict"] =  self.extract(response.xpath("//*[contains(text(),'Verdict')]//following-sibling::p[1]/text()"))
        yield review
