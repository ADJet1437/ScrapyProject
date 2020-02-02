# -*- coding: utf8 -*-
from datetime import datetime
import dateparser
from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import date_format
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ReviewItem, ProductItem

class Activegearreview_comSpider(AlaSpider):
    name = 'activegearreview_com'
    allowed_domains = ['activegearreview.com']
    start_urls = ['https://activegearreview.com/category/electronics/']

    def __init__(self, *args, **kwargs):
        super(Activegearreview_comSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):

        review_divs_xpath = "//div[@id='grid-wrapper']"
        review_divs = response.xpath(review_divs_xpath)

        for review_div in review_divs:
            date_xpath = ".//div/p[@class='post-date']/time[@class='published updated']/@datetime"
            dates = (review_div.xpath(date_xpath)).getall()
            for date in dates:
                review_date = dateparser.parse(date)
                if review_date > self.stored_last_date:
                    review_urls_xpath = ".//h2[@class='post-title entry-title']/a/@href"
                    review_urls = (review_div.xpath(review_urls_xpath)).getall()
                    for review_url in review_urls:
                        yield Request(url=review_url, callback=self.parse_items)

        next_page_xpath = "(//nav/ul/li/a/@href)[last()]"
        next_page = self.extract(response.xpath(next_page_xpath))

        review_date_xpath = "(//div/p[@class='post-date']/time[@class='published updated']/@datetime)[last()]"
        review_date = self.extract(response.xpath(review_date_xpath))
        oldest_review_date = dateparser.parse(review_date)

        if next_page:
            if oldest_review_date > self.stored_last_date:
                yield response.follow(next_page, callback=self.parse)

    def parse_items(self, response):

        product_xpaths = { "PicURL": "//meta[@property='og:image']/@content",
                           "OriginalCategoryName": "//meta[@property='article:tag']/@content"
                         }

        review_xpaths = { "TestSummary": "//meta[@property='og:description']/@content",
                          "Author": "(//span[@class='vcard author']/span/a/text())[1]",
                          "TestTitle": "//meta[@property='og:title']/@content"
                        }

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        source_internal_id = str(self.extract(response.xpath("//link[@rel='shortlink']/@href"))).split("=")[1]
        review['source_internal_id'] = source_internal_id
        product['source_internal_id'] = source_internal_id

        review["DBaseCategoryName"] = "PRO"

        product['OriginalCategoryName'] = str(product['OriginalCategoryName']).replace(" ", " | ")

        productname = review['TestTitle'].split("-")[0].replace("Review", "")
        review['ProductName'] = productname
        product['ProductName'] = productname

        date = self.extract(response.xpath("//meta[@property='article:published_time']/@content"))
        date = str(date).split("T")[0]
        review['TestDateText'] = date_format(date, '%Y-%m-%d')

        yield product
        yield review