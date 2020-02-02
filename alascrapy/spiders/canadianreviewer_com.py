# -*- coding: utf8 -*-
from datetime import datetime
import dateparser
from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import date_format, get_full_url
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ReviewItem, ProductItem

class CanadianReviewerSpider(AlaSpider):
    name = 'canadianreviewer_com'
    allowed_domains = ['canadianreviewer.com']
    start_urls = ['http://www.canadianreviewer.com/cr/category/mobile',
                    'http://www.canadianreviewer.com/cr/category/tablets',
                    'http://www.canadianreviewer.com/cr/category/android']

    def __init__(self, *args, **kwargs):
        super(CanadianReviewerSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):

        review_divs_xpath = "//div[@id='content']"
        review_divs = response.xpath(review_divs_xpath)

        for review_div in review_divs:
            date_xpath = ".//span[@class='posted-on']/text()"
            dates = (review_div.xpath(date_xpath)).getall()
            for date in dates:
                date = str(date).replace(" at ", " ")
                review_date = dateparser.parse(date)
                if review_date:
                    if review_date > self.stored_last_date:
                        review_urls_xpath = ".//h2[@class='title']/a[@class='journal-entry-navigation-current']/@href"
                        review_urls = (review_div.xpath(review_urls_xpath)).getall()
                        for review_url in review_urls:
                            review_url = get_full_url(response, review_url)
                            yield Request(url=review_url, callback=self.parse_items)

        next_page_xpath = "//span[@class='paginationControlNextPageSuffix']/a/@href"
        next_page = self.extract(response.xpath(next_page_xpath))
        next_page_url = get_full_url(response, next_page)

        review_date_xpath = "(//span[@class='posted-on']/text())[last()]"
        review_date = self.extract(response.xpath(review_date_xpath))
        date = str(review_date).replace(" at ", " ")
        oldest_review_date = dateparser.parse(date)

        if next_page:
            if oldest_review_date > self.stored_last_date:
                yield response.follow(next_page_url, callback=self.parse)

    def parse_items(self, response):

        product_xpaths = { "PicURL": "//meta[@property='og:image']/@content",
                           "OriginalCategoryName": "(//span[@class='tag-element']/a/text())[2]"
                         }

        review_xpaths = { "TestSummary": "//meta[@property='og:description']/@content",
                          "TestTitle": "//meta[@property='og:title']/@content",
                          "Author": "///span[@class='posted-by']/a/text()[2]"
                        }

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        source_internal_id = str(response.url).split("/")[7].rstrip(".html")
        review['source_internal_id'] = source_internal_id
        product['source_internal_id'] = source_internal_id

        review["DBaseCategoryName"] = "PRO"

        product_name = str(response.url).split("/")[7].replace("-", " ").replace("_", " ").rstrip(".html")
        review["ProductName"] = product_name
        product["ProductName"] = product_name

        review_date = self.extract(response.xpath("(//span[@class='posted-on']/text())[2]"))
        date = str(review_date).replace(" at ", " ")
        review['TestDateText'] = str(dateparser.parse(date)).split(" ")[0]

        yield product
        yield review