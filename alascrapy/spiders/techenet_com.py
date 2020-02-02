# -*- coding: utf8 -*-
from datetime import datetime
import re

from scrapy.http import Request, HtmlResponse
from scrapy.selector import Selector

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import date_format
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import CategoryItem, ProductItem, ReviewItem, ProductIdItem


class Techenet_comSpider(AlaSpider):
    name = 'techenet_com'
    allowed_domains = ['techenet.com']
    start_urls = ['http://www.techenet.com/category/analise/']

    def __init__(self, *args, **kwargs):
            super(Techenet_comSpider, self).__init__(self, *args, **kwargs)
            self.stored_last_date = incremental_utils.get_latest_pro_review_date(self.mysql_manager, self.spider_conf["source_id"])
            if not self.stored_last_date:
                self.stored_last_date = datetime(2018, 1, 1)

    def parse(self, response):

        review_divs_xpath = "//div[@class='archive-container clearfix']"
        review_divs = response.xpath(review_divs_xpath)

        for review_div in review_divs:
            date_xpath = ".//span[@class='meta-date']/time[@class='published']/@datetime"
            dates = (review_div.xpath(date_xpath)).getall()
            for date in dates:
                date = str(date).split("T")[0]
                review_date = datetime.strptime(date, '%Y-%m-%d')
                if review_date > self.stored_last_date:

                    review_urls_xpath = ".//header[@class='post-entry-header']/h2[@class='entry-title']//@href"
                    review_urls = (review_div.xpath(review_urls_xpath)).getall()
                    for review_url in review_urls:
                        yield Request(url=review_url, callback=self.parse_items)

        last_page = 5
        for i in range(2, last_page+1):
            next_page_url = 'http://www.techenet.com/category/analise/page/'+str(i)
            if next_page_url:
                last_date = self.extract(response.xpath('(//span[@class="meta-date"]/time[@class="published"]/@datetime)[last()]'))
                date = str(last_date).split("T")[0]
                date_time = datetime.strptime(date, '%Y-%m-%d')
                if date_time > self.stored_last_date:
                    yield Request(next_page_url, callback=self.parse)


    def parse_items(self, response):

        product_xpaths = { "PicURL": "//meta[@property='og:image'][1]/@content"
                         }

        review_xpaths = { "TestTitle": "//meta[@property='og:title'][1]/@content",
                          "TestSummary": "//meta[@property='og:description'][1]/@content",
                          "Author": "//a[@class='meta-author url']/span/span/text()",
                          "TestVerdict": "//span[@class='review_body_content'][3]/text()"
                        }

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        source_internal_id = str(self.extract(response.xpath("//link[@rel='canonical']/@href"))).split("/")[5].replace("/", "")
        review['source_internal_id'] = source_internal_id
        product['source_internal_id'] = source_internal_id

        review["DBaseCategoryName"] = "PRO"

        rating_xpath = "//span[@class='rating_summary_value']/text()"
        rating = self.extract(response.xpath(rating_xpath))
        if rating:
            review['SourceTestRating'] = rating
            review['SourceTestScale'] = '10'

        product_name = source_internal_id.replace("-", " ").replace("analise", "").replace("review", "")
        review['ProductName'] = product_name
        product['ProductName'] = product_name
        
        date = self.extract(response.xpath("//meta[@property='article:published_time'][1]/@content"))
        date = str(date).split("T")[0]
        review['TestDateText'] = date_format(date, '%Y-%m-%d')

        yield product
        yield review
