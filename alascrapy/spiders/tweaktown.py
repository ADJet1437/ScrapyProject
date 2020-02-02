# -*- coding: utf8 -*-


from datetime import datetime

from scrapy.http import Request

import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url

class TweakTownSpider(AlaSpider):
    name = 'tweaktown'
    allowed_domains = ['tweaktown.com']
    start_urls = ['http://www.tweaktown.com/reviews/index.html']

    def __init__(self, *args, **kwargs):
        super(TweakTownSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(self.mysql_manager, self.spider_conf["source_id"])

    def parse(self, response):
        category_xpaths = "//ul[@id='content-tags']/li/a/@href"

        category_urls = self.extract_list(
            response.xpath(category_xpaths))

        for category_url in category_urls:
            category_url = get_full_url(response, category_url)    
            request = Request(category_url, callback=self.parse_category)
            yield request

    def continue_to_next_page(self, response):
        if not self.stored_last_date:
            return True

        review_date_xpath = "(//div[@class='side_detail'])[last()]//strong[contains(text(),'Posted:')]/following-sibling::p/text()"
        last_date_string = self.extract(response.xpath(review_date_xpath))

        last_review_date = datetime.strptime(last_date_string, "%b %d, %Y")
        if self.stored_last_date > last_review_date:
            return False
        else:
            return True

    def parse_category(self, response):
        review_urls_xpaths = "//div[@class='side_detail']/a/@href"
        next_page_xpath = "//div[@id='page-selection-area']//a[@class='page' and text()='Next']/@href"

        review_urls = self.extract_list(
            response.xpath(review_urls_xpaths))

        for review_url in review_urls:
            if 'reviews/' in review_url and not 'movie-review' in review_url:
                review_url = get_full_url(response, review_url) 
                request = Request(review_url, callback=self.parse_review)
                yield request

        if self.continue_to_next_page(response):
            next_page = self.extract(response.xpath(next_page_xpath))
            next_page = get_full_url(response, next_page)
            request = Request(next_page, callback=self.parse)
            yield request


    def parse_review(self, response):
        review_last_page_xpath = "(//*[@class='index-mobile']//li)[last()]/a/@href"

        category_path_xpath = "//div[@id='content-crumbbar']//a//text()"
        category_xpaths = { "category_leaf": "(//div[@id='content-crumbbar']//a)[last()]//text()",
                            "category_url": "(//div[@id='content-crumbbar']//a)[last()]/@href"
                          }

        product_xpaths = { "PicURL": "(//*[@property='og:image'])[1]/@content",
                           "ProductName": "//span[@itemprop='itemReviewed']/meta[@itemprop='name']/@content",
                           "ProductManufacturer": "//div[@id='rating-bar']/*[contains(text(),'Manufacturer')]/following-sibling::a/text()"
                         }

        review_xpaths = { "TestTitle": "//div[@itemtype='http://schema.org/Review']/meta[@itemprop='name']/@content",
                          "TestSummary": "//div[@itemtype='http://schema.org/Review']/meta[@itemprop='description']/@content",
                          "Author": "//span[@itemprop='author']/meta[@itemprop='name']/@content",
                          "TestDateText": "//div[@itemtype='http://schema.org/Review']/meta[@itemprop='datePublished']/@content",
                          "SourceTestRating": "//span[@itemprop='reviewRating']/meta[@itemprop='ratingValue']/@content",
                          "ProductName": "//span[@itemprop='itemReviewed']/meta[@itemprop='name']/@content"
                        }

        category = self.init_item_by_xpaths(response, "category", category_xpaths)
        category['category_path'] = self.extract_all(
            response.xpath(category_path_xpath),
            separator=" | ")
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product["OriginalCategoryName"] = category['category_path']
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        review["DBaseCategoryName"] = "PRO"
        yield category
        yield product
        yield review
