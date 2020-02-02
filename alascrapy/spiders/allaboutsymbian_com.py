# -*- coding: utf8 -*-
from datetime import datetime
import dateparser
from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import date_format, get_full_url
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ReviewItem, ProductItem

class Allaboutsymbian_comSpider(AlaSpider):
    name = 'allaboutsymbian_com'
    allowed_domains = ['allaboutsymbian.com']
    start_urls = ['http://www.allaboutsymbian.com/reviews/']

    def __init__(self, *args, **kwargs):
        super(Allaboutsymbian_comSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):
        
        review_divs_xpath = "//section[@class='maincolumn5']"
        review_divs = response.xpath(review_divs_xpath)
        for review_div in review_divs:
            date_xpath = ".//p[@class='cdetails']/time/@datetime"
            dates = (review_div.xpath(date_xpath)).getall()
            for date in dates:
                date = str(date).split("T")[0]
                review_date = datetime.strptime(date, '%Y-%m-%d')
                if review_date > self.stored_last_date:
                    review_urls_xpath = ".//article[@class='citem clearfix']/h2/a/@href"
                    review_urls = (review_div.xpath(review_urls_xpath)).getall()
                    for review_url in review_urls:
                        yield Request(url=review_url, callback=self.parse_items)

        last_page = 20
        for i in range(2, last_page+1):
            next_page_url = 'http://www.allaboutsymbian.com/reviews/?page='+str(i)
        if next_page_url:
            last_date = self.extract(response.xpath('(//p[@class="cdetails"]/time/@datetime)[last()]'))
            date = str(last_date).split("T")[0]
            date_time = datetime.strptime(date, '%Y-%m-%d')
            if date_time > self.stored_last_date:
                yield Request(next_page, callback=self.parse)

    def parse_items(self, response):

        product_xpaths = { "PicURL": "//meta[@property='og:image']/@content",
                            "ProductName": "//meta[@property='og:title']/@content",
                           "OriginalCategoryName": "//aside[@class='btop']/p[2]/a/text()"
                         }

        review_xpaths = { "TestSummary": "//meta[@property='og:description']/@content",
                          "TestTitle": "/html/head/title/text()",
                          "ProductName": "//meta[@property='og:title']/@content",
                          "Author": "//span[@itemprop='author']/a/text()"
                        }

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        source_internal_id = str(self.extract(response.xpath('//meta[@property="og:url"]/@content'))).split("/")[5].split("_")[0]
        review['source_internal_id'] = source_internal_id
        product['source_internal_id'] = source_internal_id

        sourcetestrating = self.extract(response.xpath("//span[@class='reviewscore']/text()"))
        if sourcetestrating:
            review['SourceTestRating'] = str(sourcetestrating).strip("%")
            review['SourceTestScale'] = "100"

        review["DBaseCategoryName"] = "PRO"

        review_date = self.extract(response.xpath("//time[@itemprop='datePublished']/@datetime"))
        date = str(review_date).split("T")[0]
        review['TestDateText'] = date_format(date, '%Y-%m-%d')

        yield product
        yield review
