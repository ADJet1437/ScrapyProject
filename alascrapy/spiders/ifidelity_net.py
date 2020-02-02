# -*- coding: utf8 -*-
from datetime import datetime
import dateparser
from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import date_format, get_full_url
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ReviewItem, ProductItem, ProductIdItem

class Ifidelity_netSpider(AlaSpider):
    name = 'ifidelity_net'
    allowed_domains = ['i-fidelity.net']
    start_urls = ['http://www.i-fidelity.net/news/c/d/browse/1.html']

    def __init__(self, *args, **kwargs):
        super(Ifidelity_netSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):

        review_divs_xpath = "//div[@class='news-list-container']"
        review_divs = response.xpath(review_divs_xpath)

        for review_div in review_divs:
            date_xpath = ".//div[2]/p/text()"
            dates = (review_div.xpath(date_xpath)).getall()
            for date in dates:
                review_date = dateparser.parse(date)
                if review_date > self.stored_last_date:
                    review_urls_xpath = ".//div[1]/a/@href"
                    review_urls = (review_div.xpath(review_urls_xpath)).getall()
                    for review in review_urls:
                        review_url = get_full_url(response, review)
                        reviewurl = review_url.replace("news/c/d/browse/", "")
                        yield Request(url=reviewurl, callback=self.parse_items)

        last_page=10
        for i in range(2, last_page+1):
            next_page_url = 'http://www.i-fidelity.net/news/c/d/browse/'+str(i)+'.html'
            if next_page_url:
                review_date_xpath = "(//div[@class='news-list-container']//div[2]/p/text())[last()]"
                review_date = self.extract(response.xpath(review_date_xpath))
                oldest_review_date = dateparser.parse(review_date)
                if oldest_review_date > self.stored_last_date:
                    yield response.follow(next_page_url, callback=self.parse)

    def parse_items(self, response):

        product_xpaths = { "PicURL": "//meta[@property='og:image']/@content",
                            "ProductName": "//div[@class='news-single-item']/dl/dd[1]/text()"
                         }

        review_xpaths = { "TestSummary": "//div[@class='news-single-teaser']/h3/text()",
                          "Author": "//meta[@name='author']/@content",
                          "TestTitle": "//div[@class='news-single-item']/h2/text()",
                          "ProductName": "//div[@class='news-single-item']/dl/dd[1]/text()",
                          "TestVerdict": "(//div[@class='news-single-text']/p/text())[last()]"
                        }

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        source_internal_id = str(response.url).split("/")[6]
        review['source_internal_id'] = source_internal_id
        product['source_internal_id'] = source_internal_id

        if not review['ProductName']:
            review['ProductName'] = review['TestTitle']

        if not product['ProductName']:
            product['ProductName'] = review['TestTitle']

        review["DBaseCategoryName"] = "PRO"
        
        date = self.extract(response.xpath("//div[@class='news-single-timedata']/text()"))
        review['TestDateText'] = date_format(date, '%d.%m.%Y')

        yield product
        yield review

        price = self.extract(response.xpath("//div[@class='news-single-item']/dl/dd[2]/text()"))
        if price:
            pricevalue = str(price.encode('utf-8')).split(' ')[0]
            if pricevalue.isdigit():
                product_id = ProductIdItem()
                product_id['ID_kind'] = 'price'
                product_id['ID_value'] = pricevalue
                product_id['ProductName'] = product['ProductName']
                product_id['source_internal_id'] = product['source_internal_id']
                yield product_id