# -*- coding: utf8 -*-
from datetime import datetime
import dateparser  
import re

from scrapy.http import Request, HtmlResponse
from scrapy.selector import Selector

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import CategoryItem, ProductItem, ReviewItem, ProductIdItem


class Digit_inSpider(AlaSpider):
    name = 'digit_in'
    allowed_domains = ['digit.in']
    start_urls = ['http://www.digit.in/review/']

    def __init__(self, *args, **kwargs):
        super(Digit_inSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

    def parse(self, response):

        r1_xpath = "//div[@class='staticDropdown']//div[@class='clearfix']/a/@href"
        r2_xpath = "//div[@class='staticDropdown']//div//div[@class='product-desc']/a/@href"
        r1_urls = (response.xpath(r1_xpath)).getall()
        r2_urls = (response.xpath(r2_xpath)).getall()
        product_urls = r1_urls + r2_urls
        for product_url in product_urls:
            yield Request(url=product_url, callback=self.level_2)
    
    def level_2(self, response):

        category_path_xpath = "//nav/ol[@class='breadcrumb']/li[@class='breadcrumb-item']/a/text()"
        url_xpath = "//li[@class='breadcrumb-item'][3]/a/@href"
        category = CategoryItem()
        category['category_url'] = self.extract(response.xpath(url_xpath))
        category['category_leaf'] = self.extract(response.xpath(category_path_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
                "OriginalCategoryName":"//li[@class='breadcrumb-item'][3]/a/text()",
                "PicURL":"//div[@class='col-sm-12']/div[@class='smal-article']/img/@data-src"
                            }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)

        if not product['PicURL']:
            picurl = "/html/body/div[@class='block']/a/img/@data-src"
            product['PicURL'] = self.extract(response.xpath(picurl))
        
        review_xpaths = {               
                "ProductName":"//div[@class='ProductName']/h4/text()",
                "SourceTestRating":"//div[@class='Review-reting']/div[@class='Numeric-Number']/text()",                               
                "TestPros":"//div[@class='pros-Cons']/ul[1]/li/text()",                
                "TestCons":"//div[@class='pros-Cons']/ul[2]/li/text()",
                "TestSummary":"//meta[@name='description']/@content",
                "TestVerdict":"//div[@class='col-md-7']/p[2]/text()",
                "Author":"//div[@class='launch']/b/a[@class='datahreflink']/text()",
                "TestTitle":"//div[@class='wrap-lang']/h1/text()",
                            }
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        
        source_internal_id = str(self.extract(response.xpath('//link[@rel="amphtml"]/@href'))).split('/')[6]

        product['source_internal_id'] = source_internal_id
        review['source_internal_id'] = product['source_internal_id']
        product['ProductName'] = review['ProductName']

        if review['SourceTestRating']:
            review["SourceTestScale"] = "100"

        if not review['Author']:
            author = "//div[@class='Text-sponsered']/a/text()"
            review['Author'] = self.extract(response.xpath(author))
                
        date_xpath = "(//div[@class='launch']/text())[last()]"
        r_date = self.extract(response.xpath(date_xpath))
        if r_date:
            date = r_date.split(' ')[2]
            review["TestDateText"] = date_format(date, "%b %d %Y", ["en"])
        if not r_date:
            date_xpath = "//div[@class='Text-sponsered']/text()"
            r_date = self.extract(response.xpath(date_xpath))
            date = r_date.lstrip('|  ')
            review["TestDateText"] = date_format(date, "%d %b %Y", ["en"])

        review["DBaseCategoryName"] = "PRO"

        yield product               
        yield review

        price = self.extract(response.xpath("//div[@class='Price-Wrap']/table/tbody/tr[1]/td[3]/strong/text()"))
        if price:
            product_id = ProductIdItem()
            product_id['ID_kind'] = 'price'
            product_id['ID_value'] = price
            product_id['ProductName'] = review['ProductName']
            product_id['source_internal_id'] = review['source_internal_id']
            yield product_id    