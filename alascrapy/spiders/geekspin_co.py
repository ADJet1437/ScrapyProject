# -*- coding: utf8 -*-
from datetime import datetime
import dateparser
from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import date_format
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ReviewItem, ProductItem

class Geekspin_coSpider(AlaSpider):
    name = 'geekspin_co'
    allowed_domains = ['geekspin.co']
    start_urls = ['https://geekspin.co/tech/']

    def __init__(self, *args, **kwargs):
        super(Geekspin_coSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):

        review_divs_xpath = "(//ul[@class='g1-collection-items'])[3]"
        review_divs = response.xpath(review_divs_xpath)
        for review_div in review_divs:
            date_xpath = ".//time[@class='entry-date']/@datetime"
            dates = (review_div.xpath(date_xpath)).getall()
            for date in dates:
                date = str(date).split("T")[0]
                review_date = datetime.strptime(date, '%Y-%m-%d')
                if review_date > self.stored_last_date:
                    review_urls_xpath = ".//h3[@class='g1-gamma g1-gamma-1st entry-title']/a/@href"
                    review_urls = (review_div.xpath(review_urls_xpath)).getall()
                    for review_url in review_urls:
                        yield Request(url=review_url, callback=self.parse_items)

        last_page = 20
        for i in range(2, last_page+1):
            next_page_url = 'https://geekspin.co/tech/page/'+str(i)
            if next_page_url:
                last_date = self.extract(response.xpath('(//time[@class="entry-date"]/@datetime)[last()]'))
                date = str(last_date).split("T")[0]
                date_time = datetime.strptime(date, '%Y-%m-%d')
                if date_time > self.stored_last_date:
                    yield Request(next_page_url, callback=self.parse)

    def parse_items(self, response):

        product_xpaths = { "PicURL": "//meta[@property='og:image']/@content"
                         }

        review_xpaths = { "TestSummary": "//meta[@property='og:description']/@content",
                          "TestTitle": "//meta[@property='og:title']/@content",
                          "Author": "//span[@class='entry-author']/a/strong/text()",
                          "TestVerdict": "//h2[@class='entry-subtitle g1-gamma g1-gamma-3rd']/text()"
                        }

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        source_internal_id = str(self.extract(response.xpath("//link[@rel='shortlink']/@href"))).split("=")[1]
        review['source_internal_id'] = source_internal_id
        product['source_internal_id'] = source_internal_id

        review["DBaseCategoryName"] = "PRO"

        product_name = str(product['PicURL']).split("/")[7].replace("-", " ").replace("_", " ").split(".")[0]
        review["ProductName"] = product_name
        product["ProductName"] = product_name

        review_date = self.extract(response.xpath("//meta[@property='article:published_time']/@content"))
        date = str(review_date).split("T")[0]
        review['TestDateText'] = date_format(date, '%Y-%m-%d')

        yield product
        yield review
