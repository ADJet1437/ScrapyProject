# -*- coding: utf8 -*-
from datetime import datetime
import dateparser
from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import date_format, get_full_url
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ReviewItem, ProductItem, ProductIdItem

class Smartphone_uaSpider(AlaSpider):
    name = 'smartphone_ua'
    allowed_domains = ['smartphone.ua']
    start_urls = ['http://www.smartphone.ua/smartphone-tests.html']

    def __init__(self, *args, **kwargs):
        super(Smartphone_uaSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(2017, 1, 1)

    def parse(self, response):

        review_divs_xpath = "//td[@class='content_td']/table"
        review_divs = response.xpath(review_divs_xpath)

        for review_div in review_divs:
            date_xpath = "./tr/td[2]/span/text()"
            dates = (review_div.xpath(date_xpath)).getall()
            for date in dates:
                review_date = dateparser.parse(date, date_formats=['%d.%m.%Y'])
                if review_date > self.stored_last_date:
                    review_urls_xpath = "./tr/td[1]/a/@href"
                    review_urls = (review_div.xpath(review_urls_xpath)).getall()
                    for review_url in review_urls:
                        review_url = get_full_url(response, review_url)
                        yield Request(url=review_url, callback=self.parse_items)

        next_page_xpath = "(//td[@class='content_td']/div[1]/a/@href)[last()]"
        next_page = self.extract(response.xpath(next_page_xpath))
        next_page_url = get_full_url(response, next_page)

        review_date_xpath = "(//tr/td[2]/span/text())[last()]"
        review_date = self.extract(response.xpath(review_date_xpath))
        oldest_review_date = dateparser.parse(review_date, date_formats=['%d.%m.%Y'])

        if next_page:
            if oldest_review_date > self.stored_last_date:
                yield response.follow(next_page_url, callback=self.parse)

    def parse_items(self, response):

        product_xpaths = { "PicURL": "//div[@class='textalbum'][1]/span/img/@src",
                          "ProductName": "(//div[@id='ftext']/p/a/text())[1]",
                           "OriginalCategoryName": "//div[@id='breadcramps']/div[2]/a/span/text()"
                         }

        review_xpaths = { "TestSummary": "//meta[@name='description']/@content",
                          "Author": "(//div[@id='ftext']/p/strong/text())[last()]",
                          "TestTitle": "//td[@id='colCenter']/h1/text()",
                          "ProductName": "(//div[@id='ftext']/p/a/text())[1]",
                          "TestPros": "//table[@class='tester']/tbody/tr/td[1]/ul/li/text()",
                          "TestCons": "//table[@class='tester']/tbody/tr/td[2]/ul/li/text()"
                        }

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        source_internal_id = (str(response.url).rsplit("_", 1)[1]).split(".")[0]
        review['source_internal_id'] = source_internal_id
        product['source_internal_id'] = source_internal_id

        review["DBaseCategoryName"] = "PRO"

        date = self.extract(response.xpath("//div[@class='newsdate']/text()"))
        date = str(date).split(", ")[1]
        review['TestDateText'] = date_format(date, '%d.%m.%Y')

        if not review['ProductName']:
            product_name = review['TestTitle'].split(":")[0]
            review['ProductName'] = product_name
            product['ProductName'] = product_name

        yield product
        yield review

        price = self.extract(response.xpath("(//div[@id='ftext']/p/text())[last()]")).encode('utf-8')
        if "$" in price:
            product_id = ProductIdItem()
            product_id['ID_kind'] = 'price'
            product_id['ID_value'] = str(price).split("$")[1]
            product_id['ProductName'] = product['ProductName']
            product_id['source_internal_id'] = product['source_internal_id']
            yield product_id