# -*- coding: utf8 -*-
from datetime import datetime
import dateparser
from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import date_format
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ReviewItem, ProductItem, ProductIdItem

class MaclifeDeSpider(AlaSpider):
    name = 'maclife_de'
    allowed_domains = ['maclife.de']
    start_urls = ['https://www.maclife.de/thema/tests']

    def __init__(self, *args, **kwargs):
        super(MaclifeDeSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):
        
        review_divs_xpath = "(//aside[@class='blk-wrapper'])[1]"
        review_divs = response.xpath(review_divs_xpath)
        for review_div in review_divs:
            date_xpath = ".//span[@class='date']/text()"
            dates = (review_div.xpath(date_xpath)).getall()
            for date in dates:
                review_date = dateparser.parse(date)
                if review_date > self.stored_last_date:
                    review_urls_xpath = ".//div[@class='share_wrapper']/@data-url"
                    review_urls = (review_div.xpath(review_urls_xpath)).getall()
                    for review in review_urls:
                        review_url = response.urljoin(review)
                        yield Request(url=review_url, callback=self.parse_items)

        last_page = 20
        for i in range(1, last_page+1):
            next_page_url = 'https://www.maclife.de/thema/tests?page='+str(i)
            if next_page_url:
                last_date = self.extract(response.xpath("((//aside[@class='blk-wrapper'])[1]//span[@class='date']/text())[last()]"))
                date_time = dateparser.parse(date)
                if date_time > self.stored_last_date:
                    yield Request(next_page_url, callback=self.parse)

    def parse_items(self, response):

        product_xpaths = { "PicURL": "//meta[@property='og:image']/@content",
                            "ProductManufacturer": "//table[@class='product_capsula']/tbody/tr[2]/td/text()"
                         }

        review_xpaths = { "TestSummary": "//meta[@property='og:description']/@content",
                          "TestTitle": "//meta[@property='og:title']/@content",
                          "Author": "//div[@class='meta desktop']/div/div/a[@rel='author']/text()",
                          "TestDateText": "substring-before(//meta[@property='article:published_time']/@content,'T')",
                          "TestVerdict": "//div[@style='font-weight:bold;']/p/text()",
                          "TestPros": "//td[@class='pro']/ul/li/text()",
                          "TestCons": "//td[@class='contra']/ul/li/text()",
                          "SourceTestRating": "//td[1]/div/meta[@itemprop='ratingValue']/@content"
                        }

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        productname = review['TestTitle'].replace("Test:", "").replace("im ", "").replace("Im ", "").split("|")[0]
        if ':' in productname:
            product_name = productname.split(": ")[1]
            review['ProductName'] = product_name
            product['ProductName'] = product_name
        else:
            review['ProductName'] = productname
            product['ProductName'] = productname

        url_xpath = '//meta[@property="og:url"]/@content'
        url = self.extract(response.xpath(url_xpath))

        # finding the source internal id in the url
        end_str = url.split('-')[-1]
        source_int_id = end_str.split('.')[0]

        product['source_internal_id'] = source_int_id

        review['DBaseCategoryName'] = 'PRO'
        review['source_internal_id'] = source_int_id

        if review['SourceTestRating']:
            review['SourceTestScale'] = '5'

        price = self.extract(response.xpath("//table[@class='product_capsula']/tbody/tr[3]/td/text()")).encode('utf-8')
        if price:
            product_id = ProductIdItem()
            product_id['ProductName'] = productname
            product_id['source_internal_id'] = source_int_id
            product_id['ID_kind'] = 'price'
            product_id['ID_value'] = str(price).split("€")[0].replace("ab ", "").replace("$", "")
            yield product_id

        yield product
        yield review