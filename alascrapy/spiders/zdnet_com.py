# -*- coding: utf8 -*-
from datetime import datetime

from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ReviewItem, ProductItem

class ZDNETSpider(AlaSpider):
    name = 'zdnet_com'
    allowed_domains = ['zdnet.com']
    start_urls = ['http://www.zdnet.com/reviews/#reviews']

    def __init__(self, *args, **kwargs):
        super(ZDNETSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):

        print self.stored_last_date
        review_divs_xpath = "//div[@id='d031c816-ecc4-4983-91c5-4e07caf8d9db-river']/div"
        review_divs = response.xpath(review_divs_xpath)

        for review_div in review_divs:
            date_xpath = "./article/div/div[2]/p[2]/span/@data-date"
            dates = (review_div.xpath(date_xpath)).getall()
            for date in dates:
                review_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                if review_date > self.stored_last_date:
                    review_urls_xpath = ".//article/div/div[2]/h3/a/@href"
                    review_urls = (review_div.xpath(review_urls_xpath)).getall()
                    for review_url in review_urls:
                        review_url = get_full_url(response, review_url)
                        yield Request(url=review_url, callback=self.parse_items)

        last_page=30
        for i in range(2, last_page+1):
            next_page_url = 'http://www.zdnet.com/reviews/'+str(i)
            if next_page_url:
                yield Request(next_page_url, callback=self.parse)

    def parse_items(self, response):

        product_xpaths = { "PicURL": "//meta[@property='og:image']/@content",
                           "OriginalCategoryName": "(//p[@class='meta']/a)[last()]/text()"
                         }

        review_xpaths = { "TestSummary": "//meta[@name='description']/@content",
                          "TestTitle": "//meta[@property='og:title']/@content",
                          "TestPros": "//ul[@class='pros']/li/text()",
                          "TestCons": "//ul[@class='cons']/li/text()"
                        }

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        source_internal_id = str(response.url).split("/")[4].rstrip("/")
        review['source_internal_id'] = source_internal_id
        product['source_internal_id'] = source_internal_id

        review['Author'] = self.extract(response.xpath("//div[@class='byline']/p[@class='meta']/a[1]/text()"))
        if not review['Author']:
            review['Author'] = str(self.extract(response.xpath("(//div[@class='credit']/p)[2]/text()"))).split(":")[1]

        review["DBaseCategoryName"] = "PRO"

        source_test_rating = self.extract(response.xpath("//li[@class='editors']//*[@itemprop='ratingValue']/text()"))
        if source_test_rating:
            review['SourceTestRating'] = source_test_rating
            review['SourceTestScale'] = '10'

        if "review" in review["TestTitle"]:
            product_name = review["TestTitle"].split("review")[0]
        elif ":" in review["TestTitle"]:
            product_name = review["TestTitle"].split(":")[0]
        else:
            product_name = (response.url).split("/")[4].replace("-", " ").rstrip("/")

        review['ProductName'] = product_name
        product['ProductName'] = product_name

        date = self.extract(response.xpath("//time/@datetime"))
        review['TestDateText'] = date_format(date, '%Y-%m-%d')

        yield product
        yield review
