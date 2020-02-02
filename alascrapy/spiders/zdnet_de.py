# -*- coding: utf8 -*-
from datetime import datetime
import dateparser
from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ReviewItem, ProductItem

class Zdnet_DeSpider(AlaSpider):
    name = 'zdnet_de'
    allowed_domains = ['zdnet.de']
    start_urls = ['http://www.zdnet.de/kategorie/mobility/laptops/',
                 'http://www.zdnet.de/kategorie/mobility/smartphones/',
                  'http://www.zdnet.de/kategorie/mobility/tablets/' ]

    def __init__(self, *args, **kwargs):
        super(Zdnet_DeSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):

        review_divs_xpath = "//div[@class='articleList clear']"
        review_divs = response.xpath(review_divs_xpath)

        for review_div in review_divs:
            date_xpath = ".//span[@class='date']/p/time/@datetime"
            dates = (review_div.xpath(date_xpath)).getall()
            for date in dates:
                review_date = dateparser.parse(date, date_formats=['%d. %m %Y, %H:%M'], languages=['de', 'es'])
                if review_date > self.stored_last_date:
                    review_urls_xpath = ".//h2/a/@href"
                    review_urls = (review_div.xpath(review_urls_xpath)).getall()
                    for review_url in review_urls:
                        yield Request(url=review_url, callback=self.parse_items)

        next_page_xpath = "//li[@class='next']/a/@href"
        next_page = self.extract(response.xpath(next_page_xpath))

        review_date_xpath = "(//span[@class='date']/p/time/@datetime)[last()]"
        review_date = self.extract(response.xpath(review_date_xpath))
        oldest_review_date = dateparser.parse(review_date, date_formats=['%d. %m %Y, %H:%M'], languages=['de', 'es'])

        if next_page:
            if oldest_review_date > self.stored_last_date:
                yield response.follow(next_page, callback=self.parse)

    def parse_items(self, response):

        product_xpaths = { "PicURL": "(//meta[@property='og:image'])[1]/@content",
                           "OriginalCategoryName": "//div[@id='breadcrumb']/a[last()]/text()"
                         }

        review_xpaths = { "TestSummary": "//meta[@name='description']/@content",
                          "TestTitle": "//meta[@property='og:title']/@content",
                          "TestVerdict": "//header/p/b/text()",
                          "Author": "//p/a[@class='url']/text()"
                        }

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        source_internal_id = str(response.url).split("/")[3].rstrip("/")
        review['source_internal_id'] = source_internal_id
        product['source_internal_id'] = source_internal_id

        review["DBaseCategoryName"] = "PRO"

        product_name = str(product["PicURL"]).split("/")[7].split(".")[0].replace("-", " ").replace("_", " ").strip(".jp")
        review["ProductName"] = product_name
        product["ProductName"] = product_name

        date = self.extract(response.xpath("//div[@class='byline']/p/a[2]/time/@datetime"))
        if not date:
            date = self.extract(response.xpath("//span[@class='byline']/p/a[2]/time/@datetime"))
        review['TestDateText'] = date_format(date, '%Y-%m-%d')

        yield product
        yield review
