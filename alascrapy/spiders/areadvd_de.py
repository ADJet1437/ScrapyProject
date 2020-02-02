# -*- coding: utf8 -*-
from datetime import datetime
import dateparser
from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import date_format
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ReviewItem, ProductItem

class Areadvd_DeSpider(AlaSpider):
    name = 'areadvd_de'
    allowed_domains = ['areadvd.de']
    start_urls = ['https://www.areadvd.de/tag/tv/',
                 'https://www.areadvd.de/tag/smartphone/',
                  'https://www.areadvd.de/tag/multimedia/',
                  'https://www.areadvd.de/tag/lautsprecher/']

    def __init__(self, *args, **kwargs):
        super(Areadvd_DeSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):

        review_divs_xpath = "//div[@id='content']"
        review_divs = response.xpath(review_divs_xpath)

        for review_div in review_divs:
            date_xpath = "./div[@class='list-posts']/text()"
            dates = (review_div.xpath(date_xpath)).getall()
            for date in dates:
                review_date = dateparser.parse(date, date_formats=['%d.%m.%Y'])
                if review_date:
                    if review_date > self.stored_last_date:
                        review_urls_xpath = "./div[@class='list-posts']/a/@href"
                        review_urls = (review_div.xpath(review_urls_xpath)).getall()
                        for review_url in review_urls:
                            yield Request(url=review_url, callback=self.parse_items)

        next_page_xpath = "//div[@class='alignleft']/a/@href"
        next_page = self.extract(response.xpath(next_page_xpath))

        review_date_xpath = "((//*[@id='content']/div[31]/text()))[1]"
        review_date = self.extract(response.xpath(review_date_xpath))
        oldest_review_date = dateparser.parse(review_date, date_formats=['%d.%m.%Y'])

        if next_page:
            if oldest_review_date > self.stored_last_date:
                yield response.follow(next_page, callback=self.parse)

    def parse_items(self, response):

        date = self.extract(response.xpath("//meta[@property='article:published_time']/@content"))
        date = str(date).split("T")[0]

        review_date = datetime.strptime(date, "%Y-%m-%d")
        if self.stored_last_date > review_date:
        	return

        product_xpaths = { "PicURL": "//meta[@property='og:image']/@content",
                           "OriginalCategoryName": "//div[@class='entry']/a[2]/text()"
                         }

        review_xpaths = { "TestSummary": "//meta[@property='og:description']/@content",
                          "TestTitle": "//meta[@property='og:title']/@content"
                        }

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        
        review['TestDateText'] = date_format(date, '%Y-%m-%d')

        try:
        	source_internal_id = str(self.extract(response.xpath("//*[@id='content']/div[6]/comment()[1]"))).split("-")[3].split(" ")[0]
         	review['source_internal_id'] = source_internal_id
        	product['source_internal_id'] = source_internal_id
        except:
        	internal_source_id = str(self.extract(response.xpath("//*[@id='content']/div[2]/comment()[4]"))).split("-")[3].split(" ")[0]
        	review['source_internal_id'] = internal_source_id
        	product['source_internal_id'] = internal_source_id
        
        review["DBaseCategoryName"] = "PRO"

        product_name = str(product["PicURL"].encode('utf-8')).split("/")[6].split(".")[0].replace("-", " ").replace("_", " ").strip(".jpg")
        review["ProductName"] = product_name
        product["ProductName"] = product_name

        author = self.extract(response.xpath("//div[@class='postdate']/text()"))
        review['Author'] = str(author).split("(")[1].rstrip(")")

        date = self.extract(response.xpath("//meta[@property='article:published_time']/@content"))
        date = str(date).split("T")[0]
        review['TestDateText'] = date_format(date, '%Y-%m-%d')

        yield product
        yield review 