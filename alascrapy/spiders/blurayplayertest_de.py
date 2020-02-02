# -*- coding: utf8 -*-
from datetime import datetime

from scrapy.http import Request
from alascrapy.lib.generic import date_format
import alascrapy.lib.dao.incremental_scraping as incremental_utils

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.items import ProductIdItem, ProductItem, ProductIdItem

class Blurayplayertest_deSpider(AlaSpider):
    name = 'blurayplayertest_de'
    allowed_domains = ['blurayplayertest.de']
    start_urls = ['https://www.blurayplayertest.de/']

    def __init__(self, *args, **kwargs):
        super(Blurayplayertest_deSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):

        for product_url in response.xpath(
                "//div[@class='info']/a[@class='right']/@href").extract():
            yield Request(url=product_url, callback=self.parse_items)

    def parse_items(self, response):

        review_date = self.extract(response.xpath("//div[@class='offers']/small/text()"))
        date = str(review_date).split(" ")[2]
        reviewdate = datetime.strptime(date, "%d.%m.%Y")
        if self.stored_last_date > reviewdate:
            return

        product_xpaths = { "PicURL": "//meta[@property='og:image']/@content",
                            "ProductManufacturer": "//tr[@class='marke-hersteller']/td/a/text()"
                         }

        review_xpaths = { "TestSummary": "//div[@id='review_body']/div[1]/p/text()",
                          "TestVerdict": "(//div[@id='review_body']/div/p/text())[last()]",  
                          "TestTitle": "(//title/text())[1]",
                          "Author": "//span/meta[@itemprop='author']/@content",
                          "TestPros": "//div[@class='list-advantages']/ul/li/div/text()",
                          "TestCons": "//div[@class='list-disadvantages']/ul/li/div/text()",
                          "SourceTestRating": "//span/meta[@itemprop='ratingValue']/@content"
                        }

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        productname = self.extract(response.xpath("//tr[@class='modell']/td/span/text()"))
        productmanu = product['ProductManufacturer']
        review['ProductName'] = productmanu + " " + productname
        product['ProductName'] = review['ProductName']

        source_internal_id = self.extract(response.xpath("//div/meta[@itemprop='productID']/@content"))
        review['source_internal_id'] = source_internal_id
        product['source_internal_id'] = source_internal_id

        if not product['PicURL']:
            product['PicURL'] = self.extract(response.xpath("(//div/a/img/@data-src)[1]"))

        if review['SourceTestRating']:
            review['SourceTestScale'] = "5"

        review["DBaseCategoryName"] = "PRO"

        review['TestDateText'] = date_format(date, '%d.%m.%Y')
        yield review
        yield product                

        price = self.extract(response.xpath("//div[@class='price']/text()")).encode('utf-8')
        if price:
            product_id = ProductIdItem()
            product_id['ID_kind'] = 'price'
            product_id['ID_value'] = str(price).split(' ')[0]
            product_id['ProductName'] = product['ProductName']
            product_id['source_internal_id'] = product['source_internal_id']
            yield product_id