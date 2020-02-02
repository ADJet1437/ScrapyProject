# -*- coding: utf8 -*-

from datetime import datetime
import re
from scrapy import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import date_format, get_full_url
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem

class Digitalphoto_deSpider(AlaSpider):
    name = 'digitalphoto_de'
    allowed_domains = ['digitalphoto.de']
    start_urls = ['https://www.digitalphoto.de/thema/tests']

    def __init__(self, *args, **kwargs):
        super(Digitalphoto_deSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):

        review_divs_xpath = "//div[@class='col-12 col-sm-6 col-md-4']"
        review_divs = response.xpath(review_divs_xpath)

        for review_div in review_divs:
            date_xpath = ".//div[@class='submitted']/span/@content"
            dates = (review_div.xpath(date_xpath)).getall()
            for date in dates:
                date = str(date).split("T")[0]
                review_date = datetime.strptime(date, '%Y-%m-%d')
                if review_date > self.stored_last_date:
                    review_urls_xpath = ".//h2[@class='title']/a/@href"
                    review_urls = (review_div.xpath(review_urls_xpath)).getall()
                    for review_url in review_urls:
                        review = get_full_url(response, review_url)
                        reviewurl = review.replace("/thema/ ", "")
                        yield Request(url=reviewurl, callback=self.parse_items)

        last_page=10
        for i in range(1, last_page+1):
            next_page_url = 'https://www.digitalphoto.de/thema/tests?page='+str(i)
            if next_page_url:
                last_date = self.extract(response.xpath("(//div[@class='col-12 col-sm-6 col-md-4']//div[@class='submitted']/span/@content)[last()]"))
                date = str(last_date).split("T")[0]
                date_time = datetime.strptime(date, '%Y-%m-%d')
                
                if date_time > self.stored_last_date:
                    yield Request(next_page_url, callback=self.parse)

    def parse_items(self, response):

        product_xpaths = { "PicURL": "//meta[@property='og:image']/@content",
                            "OriginalCategoryName": "//ul[@class='tags']/li/a/text()"
                         }

        review_xpaths = { "TestSummary": "//meta[@property='og:description']/@content",
                          "TestVerdict": "(//div[@class='article-content']/p/em/strong/text())[last()]",  
                          "TestTitle": "//meta[@property='og:title']/@content",
                          "Author": "//div[@class='author-wrapper']/div[@class='submitted']/a/text()"
                        }

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        
        internal_source_id = (str(response.url).rsplit("-", 1)[1]).split(".")[0]
        review['source_internal_id'] = internal_source_id
        product['source_internal_id'] = internal_source_id

        product_name = str(review['TestTitle'].encode('utf-8')).split("|")[0]
        product['ProductName'] = product_name
        review['ProductName'] = product_name

        product['OriginalCategoryName'] = str(product['OriginalCategoryName'].encode('utf-8')).replace(" ", " | ").replace(' ', '').replace('#', '')

        review['DBaseCategoryName'] = 'PRO'

        date = self.extract(response.xpath("//div[@class='col-12 col-lg-8']/span/@content"))
        if date:
            date_str = str(date).split("T")[0]
            review['TestDateText'] = date_str
            
        yield review
        yield product