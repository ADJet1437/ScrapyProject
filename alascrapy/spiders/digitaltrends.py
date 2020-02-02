# -*- coding: utf8 -*-

import re
from datetime import datetime
from scrapy.http import Request
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format
from alascrapy.items import CategoryItem, ProductItem, ReviewItem
import alascrapy.lib.dao.incremental_scraping as incremental_utils

class DigitaltrendsSpider(AlaSpider):
    name = 'digitaltrends'
    allowed_domains = ['digitaltrends.com']
    start_urls = ['https://www.digitaltrends.com/product-reviews/']

    def __init__(self, *args, **kwargs):
        super(DigitaltrendsSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):
        
        review_divs_xpath = "//section[@class='b-grid b-page__grid']"
        review_divs = response.xpath(review_divs_xpath)

        for review_div in review_divs:
            date_xpath = './/div/span/time/@datetime'
            dates = (review_div.xpath(date_xpath)).getall()
            for date in dates:
                if date:
                    date = str(date).split("T")[0]
                    review_date = datetime.strptime(date, '%Y-%m-%d')
                    if review_date > self.stored_last_date:
                        review_urls_xpath = ".//h3/a/@href"
                        review_urls = (review_div.xpath(review_urls_xpath)).getall()
                        for review in review_urls:
                            yield Request(url=review, callback=self.parse_review)

        next_page_xpath = "//div[@class='b-paging__word b-paging__word--next']/a/@href"
        next_page = self.extract(response.xpath(next_page_xpath))
        if next_page:
            request = Request(next_page, callback=self.parse)
        
    def parse_review(self, response):

        date = self.extract(response.xpath('//meta[@property="article:published_time"]/@content'))
        r_date = str(date).split("T")[0]
        review_date = datetime.strptime(r_date, "%Y-%m-%d")
        if self.stored_last_date > review_date:
            return
        
        categories_xpath = "//div[@class='b-headline__crumbs']/span/span"
        cat_name_xpath = "./a/text()"
        cat_url_xpath = "./a/@href"
        categories = response.xpath(categories_xpath)
        for category in categories:
            category_url = self.extract(category.xpath(cat_url_xpath))
            category_name = self.extract(category.xpath(cat_name_xpath))

            category = CategoryItem()
            category["category_leaf"] = category_name
            category["category_path"] = category_name
            category["category_url"] = category_url
            yield category

            if self.should_skip_category(category):
              return 

        source_internal_id = str(self.extract(response.xpath("//link[@rel='shortlink']/@href"))).split("=")[1]
        award_xpath = "//div[@class='l-group-1']/div[contains(@class, 'm-award')]"
        javascript_xpath = "//script[contains(text(), 'dataLayer') and contains(text(), 'mpn')]/text()"

        product_xpaths = { "PicURL": "//*[@property='og:image']/@content",
                           "ProductName": "//*[@itemprop='itemReviewed']/*[@itemprop='name']/@content"
                         }

        review_xpaths = { "TestTitle": "//h1[contains(@class,'title')]/text()",
                          "TestSummary": "//meta[@name='description']/@content",
                          "Author": "//span[@class='b-byline__authors']/a/text()",
                          "TestVerdict": "//header/h2[@class='b-headline__sub-title']/text()",
                          "TestPros":"//div[3]/div/div/article/div[1]/ul[1]/li/text()",
                          "TestCons":"//div[@class='b-review']/ul[@class='b-review__list b-review__list--bad']/li/text()"
                        }

        summary_alt_xpath = "(//*[@itemprop='reviewBody']/p)[1]//text()"
        verdict_alt_path = "string(//span[@class='m-our-take']/following-sibling::p[1])"

        javascript = self.extract(response.xpath(javascript_xpath))

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        if not product["ProductName"]:
            product["ProductName"] = review["TestTitle"].replace('Review', '').replace('review', '').strip()

        product["OriginalCategoryName"] = category["category_path"]
        product["source_internal_id"] = source_internal_id
        yield product

        review["ProductName"] = product["ProductName"]
        review["source_internal_id"] = source_internal_id
        review["DBaseCategoryName"] = "PRO"
        
        review["TestDateText"] = r_date
        if not review["TestSummary"]:
            review["TestSummary"] = self.extract_all_xpath(response, summary_alt_xpath)
        if not review["TestVerdict"]:
            review["TestVerdict"] = self.extract(response.xpath(verdict_alt_path))
        award = response.xpath(award_xpath)
        if award:
            award_name = self.extract_all(award.xpath('.//text()'))
            review['award'] = award_name
        yield review