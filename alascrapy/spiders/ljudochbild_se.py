# -*- coding: utf8 -*-

from datetime import datetime
import dateparser
import re
from scrapy import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import date_format
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem, ProductIdItem


class Ljudochbild_seSpider(AlaSpider):
    name = 'ljudochbild_se'
    allowed_domains = ['ljudochbild.se']
    start_urls = ['https://www.ljudochbild.se/test/']

    def __init__(self, *args, **kwargs):
        super(Ljudochbild_seSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):

        review_divs_xpath = "//main/div[@class='col-md-8 mobilefilterx']//div[@class='pt-cv-ifield']"
        review_divs = response.xpath(review_divs_xpath)

        for review_div in review_divs:
            date_xpath = "./div/span[@class='entry-date']/time/@datetime"
            dates = (review_div.xpath(date_xpath)).getall()
            for date in dates:
                date = str(date).split("T")[0]
                review_date = datetime.strptime(date, '%Y-%m-%d')
                if review_date > self.stored_last_date:
                    review_urls_xpath = "./h4/a/@href"
                    review_urls = (review_div.xpath(review_urls_xpath)).getall()
                    r1 = filter(lambda k: 'horlurar' in k, review_urls)
                    r2 = filter(lambda k: 'tv' in k, review_urls)
                    r3 = filter(lambda k: 'mobil-surplatta' in k, review_urls)
                    r4 = filter(lambda k: 'prylar' in k, review_urls)
                    r5 = filter(lambda k: 'hogtalare' in k, review_urls)
                    review_url = r1 + r2 + r3 +r4 + r5
                    for review in review_url:
                        yield Request(url=review, callback=self.parse_items)

        last_page=309
        for i in range(2, last_page+1):
            next_page_url = 'https://www.ljudochbild.se/test/?_page='+str(i)
            if next_page_url:
                last_date = self.extract(response.xpath('(//span[@class="entry-date"]/time/@datetime)[last()]'))
                date = str(last_date).split("T")[0]
                date_time = datetime.strptime(date, '%Y-%m-%d')

                if date_time > self.stored_last_date:
                    yield Request(next_page_url, callback=self.parse)

    def parse_items(self, response):

        review_xpaths = {
            "TestTitle": "//meta[@property='og:title']/@content",
            "TestVerdict": "(//div[@class='heycontent']/p/text()[last()])[last()]",
            "TestPros": "//div[@class='col-md-12 hideonphone'][1]/span[2]/text()",
            "TestCons": "//div[@class='col-md-12 hideonphone'][2]/span[2]/text()",
            "TestSummary": "//meta[@name='description']/@content"
        }

        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        product = ProductItem()
        
        review['TestTitle'] = review['TestTitle'].replace(" | Ljud & Bild", "")
        sid = str(response.url).rstrip("/").rpartition("/")
        source_internal_id = str(sid[-1])
        review['source_internal_id'] = source_internal_id
        product['source_internal_id'] = source_internal_id

        product_name = review['TestTitle'].split("-")[0].replace(" | Ljud & Bild", "").replace("VI TESTAR: ", "").replace("TEST: ", "")
        product['ProductName'] = product_name
        review['ProductName'] = product_name

        author = self.extract(response.xpath("//div[@class='forfatter']/span/a[@class='fn email']/text()")).encode('utf-8')
        review['Author'] = author.replace("Av ", "")

        source_test_rating = self.extract(response.xpath(
            "//div[@class='ratetotal']/img/@src"))
        if source_test_rating:
            review['SourceTestRating'] = str(source_test_rating).split("/")[6].replace(".png", "")
            review['SourceTestScale'] = '6'

        product['TestUrl'] = response.url
        product['PicURL'] = self.extract(response.xpath('//meta[@property="og:image"]/@content'))
        review['DBaseCategoryName'] = 'PRO'

        date = self.extract(response.xpath("(//a[@class='fn email']//text())[last()]")).encode('utf-8')
        if date:
            date_time = date_format(date, '%d/%m/%Y')
            review['TestDateText'] = date_time
            
        yield review
        yield product

        price = self.extract(response.xpath("//div[@id='tab-1']/div[1]/span/text()"))
        if price:
            product_id = ProductIdItem()
            product_id['ID_kind'] = 'price'
            product_id['ID_value'] = str(price).lstrip('Pris:').replace('kr', '')
            product_id['ProductName'] = product_name
            product_id['source_internal_id'] = source_internal_id
            yield product_id        