import json
from scrapy.http import Request
from alascrapy.items import ProductItem, CategoryItem, ReviewItem, ProductIdItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format

class FotografiNoSpider(AlaSpider):
    name = 'fotografi_no_reviews'
    start_urls = ['http://www.fotografi.no/artikler/tester']
    allowed_domains = ['fotografi.no']

    def parse(self, response):

        review_urls_xpath = "//a[@class='read-more-link']/@href"
        next_page_xpath = "//div[nav-links]/a[@class= 'next page-numbers']/@href"

        review_urls = self.extract_list(response.xpath(review_urls_xpath))

        for review_url in review_urls:
            request = Request(review_url, callback=self.parse_review)
            request.meta['category'] = 'Cameras'
            yield request

        next_page = self.extract(response.xpath(next_page_xpath))
        if next_page:
            request = Request(next_page, callback=self.parse)
            yield request


    def parse_review(self, response):
        product = ProductItem()

        pic_url_xpath = "//div[@class='entr-title']//text()"

        product['ProductName'] = self.extract(response.xpath("//h1[@class='entry-title']//text()"))
        product['OriginalCategoryName'] = response.meta['category']
        product['PicURL'] = self.extract(response.xpath(pic_url_xpath))

        yield product

        testTitle_xpath = "//div[@class='entry-title']//text()"
        testSummary_xpath = "//article[@class='entry-content']/p//text()"
        author_xpath = "//span[@class='author vcard']/a/text()"
        testDateText_xpath = "//span/time[@class='entry-date published']/text()"

        review = ReviewItem()
        review["TestUrl"] = response.url
        review["DBaseCategoryName"] = "PRO"
        review["ProductName"] = product["ProductName"]
        review["TestTitle"] = self.extract_all(response.xpath(testTitle_xpath))
        review["TestSummary"] = self.extract_all(response.xpath(testSummary_xpath), " ")
        review["Author"] = self.extract(response.xpath(author_xpath))
        review["TestDateText"] = self.extract(response.xpath(testDateText_xpath))
