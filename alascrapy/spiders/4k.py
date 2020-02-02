# -*- coding: utf8 -*-
__author__ = 'leonardo'

import re

from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import strip, date_format
from alascrapy.items import CategoryItem
import alascrapy.lib.dao.incremental_scraping as incremental_utils


class FourkSpider(AlaSpider):
    name = '4k'
    allowed_domains = ['4k.com']
    start_urls = ['http://4k.com/archives/']

    category_re = re.compile('4k\.com/([^/]+)/')
    date_urls = re.compile('4k\.com/\d{4}/\d{2}')

    review_re = category_re = re.compile('4k\.com/([^/]+)/[^/]+')

    def __init__(self, *args, **kwargs):
        super(FourkSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(self.mysql_manager, self.spider_conf["source_id"])

    def parse(self, response):
        review_urls_xpaths = "//div[@class='content-inner']//ul/li/a/@href"
        review_urls = self.extract_list(response.xpath(review_urls_xpaths))
        for review_url in review_urls:
            if '4k.com/news/' in review_url:
                continue
            if '4k.com/category/' in review_url:
                continue
            if '4k.com/video/' in review_url:
                continue
            if re.search(self.date_urls, review_url):
                continue
            if not re.search(self.review_re, review_url):
                continue

            request = Request(review_url, callback=self.parse_reviews)
            yield request

    def parse_reviews(self, response):
        if response.xpath("//h1[@itemprop='itemReviewed']"):
            product_xpaths = { "PicURL": "(//*[@property='og:image'])[1]/@content",
                               "ProductManufacturer": "(//span[@class='detail-label' and text()='Manufacture']/following-sibling::span[@class='detail-content'])[1]//text()"
                             }

            review_xpaths = { "TestTitle": "//h1[@itemprop='itemReviewed']/text()",
                              "TestSummary": "(//span[@class='detail-label' and text()='Overview']/following-sibling::span[@class='detail-content'])[1]/p[1]//text()",
                              "Author": "//span[@itemprop='author']/text()",
                              "SourceTestRating": "//meta[@itemprop='ratingValue']/@content",
                              "TestDateText": "//meta[@itemprop='datePublished']/@content",
                              "TestVerdict": "(//div[@class='bottomline']/p)[1]//text()"
                            }
            test_summary_alt_xpath = "(//span[@class='detail-label' and text()='Overall']/following-sibling::span[@class='detail-content'])[1]/p[1]//text()"
            pros_css = ".procon.pro"
            cons_css = ".procon.con"

            category = None
            match = re.search(self.category_re, response.url)
            if match:
                category = CategoryItem()
                category["category_leaf"] = match.group(1)
                category["category_path"] = match.group(1)
                yield category

            product = self.init_item_by_xpaths(response, "product", product_xpaths)
            review = self.init_item_by_xpaths(response, "review", review_xpaths)

            if category:
                product['OriginalCategoryName'] = category["category_path"]
            product['ProductName'] = strip(review['TestTitle'].replace('A Review of the', ''))
            review['ProductName'] = product['ProductName']
            pros_div = response.css(pros_css)
            review["DBaseCategoryName"] = "PRO"
            if not review['TestSummary']:
                review['TestSummary'] = self.extract_all(response.xpath(test_summary_alt_xpath))

            review['TestPros'] = self.extract_all(pros_div.xpath('./p/text()'),
                                                  separator=' ; ',
                                                  strip_unicode=[u'\u2022'])

            cons_div = response.css(cons_css)
            review['TestCons'] = self.extract_all(cons_div.xpath('./p/text()'),
                                                  separator=' ; ',
                                                  strip_unicode=[u'\u2022'])

            review['TestDateText'] = date_format(review['TestDateText'], '%b %d, %Y')

            yield product
            yield review

