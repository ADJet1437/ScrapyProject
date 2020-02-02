# -*- coding: utf8 -*-
import re
from datetime import datetime, timedelta
from dateparser import parse

from scrapy import Selector
from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductIdItem


class WiredUkSpider(AlaSpider):
    name = 'wired_co_uk'
    allowed_domains = ['wired.co.uk']
    start_urls = ['http://www.wired.co.uk/reviews']

    def __init__(self, *args, **kwargs):
        super(WiredUkSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

    def parse(self, response):
        review_urls_xpath = \
            "//ul[@class='c-card-section__card-list js-c-card-section__card-list']//a/@href"
        review_urls = self.extract_list(response.xpath(review_urls_xpath))
        for url in review_urls:
            yield response.follow(url=url, callback=self.parse_review)

    def parse_review(self, response):
        product_xpaths = {
            "OriginalCategoryName":
            "//a[@class='a-header__tag__primary']//text()",
            "PicURL": "//*[@property='og:image']/@content"
        }

        review_xpaths = {
            "TestTitle": "//h1/text()",
            "TestSummary": "//meta[@name=name='og:description']/@content",
            "Author": "//span[@class='a-header__byline-name']//text()",
            "TestDateText": "//div[@class='a-author__article-date']/text()",
            "TestVerdict":
            "//h2[@id='verdict']/following-sibling::p[1]/text()",
            "TestPros":
            "//div[@class='a-review__item a-review__item--positive']"
            "//div[@class='a-review__value']//text()",
            "TestCons":
            "//div[@class='a-review__item a-review__item--negative']"
            "//div[@class='a-review__value']//text()"
        }

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        ori_date_text = review.get('TestDateText', '')
        splitted = ori_date_text.split(' ')[1:]
        date_text = ''
        for i in splitted:
            date_text += '{} '.format(i)
        date = date_format(date_text, '%d %B %Y')
        date_time = datetime.strptime(date, '%Y-%m-%d')
        if date_time < self.stored_last_date:
            return
        review["TestDateText"] = date

        review["DBaseCategoryName"] = "PRO"
        rating_xpath = "//div[@class='a-review__rating']//text()"
        rating_str = self.extract_all(response.xpath(rating_xpath))
        rated = rating_str.split('/')[0]
        if rated:
            review['SourceTestRating'] = rated
            review['SourceTestScale'] = 10

        if not review["Author"]:
            author_alt_xpath = "//*[@class='authorName']/text()"
            review["Author"] = self.extract_all(
                response.xpath(author_alt_xpath))

        if not review["TestTitle"]:
            title_alt_xpath = "//*[@property='og:title']/@content"
            review["TestTitle"] = self.extract_all(
                response.xpath(title_alt_xpath))

        title = review.get('TestTitle', '')
        if title.startswith('Review'):
            product["ProductName"] = title.split(':')[1]
        elif 'review:' in title:
            product["ProductName"] = title.split('review')[0]
        else:
            product["ProductName"] = review["TestTitle"]

        review["ProductName"] = product["ProductName"]

        product_id = ProductIdItem()
        price_xpath = "//div[@class='a-review__item a-review__item--price']"\
            "//text()"
        price_str = self.extract_all(response.xpath(price_xpath))
        product_id['ID_kind'] = 'price'
        product_id['ID_value'] = price_str
        product_id['ProductName'] = product['ProductName']

        yield product
        yield review
        yield product_id
