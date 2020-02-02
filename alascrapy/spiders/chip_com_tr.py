# -*- coding: utf8 -*-
from datetime import datetime
import re

from scrapy.http import Request, HtmlResponse
from scrapy.selector import Selector

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.spiders.base_spiders.bazaarvoice_spider import BVNoSeleniumSpider
from alascrapy.lib.generic import get_full_url, date_format
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import CategoryItem, ProductItem, ReviewItem, ProductIdItem
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from alascrapy.lib.selenium_browser import SeleniumBrowser


class Chip_com_trSpider(AlaSpider):
    name = 'chip_com_tr'
    allowed_domains = ['chip.com.tr']
    start_urls = ['http://www.chip.com.tr/inceleme/']

    
    def parse(self, response):
                                     
        original_url = response.url
        product = response.meta.get("product", {})
        review = response.meta.get("review", {})
        
        url_xpath = "//li/a[@rel='next']/@href"
        single_url = self.extract(response.xpath(url_xpath))
        if single_url:
            matches = None
            if "":
                matches = re.search("", single_url, re.IGNORECASE)
                if matches:
                    single_url = matches.group(0)
                else:
                    return
            single_url = get_full_url(original_url, single_url)
            
            request = Request(single_url, callback=self.parse)
            try:
                request.meta["product"] = product
            except:
                pass
            try:
                request.meta["review"] = review
            except:
                pass
            yield request
        urls_xpath = "//div[@class='col-orta']//div[@class='col-clistinfo' or @class='akisBody']/a/@href"
        params_regex = {}
        urls = self.extract_list(response.xpath(urls_xpath))
        
        for single_url in urls:
            matches = None
            if "":
                matches = re.search("", single_url, re.IGNORECASE)
                if matches:
                    single_url = matches.group(0)
                else:
                    continue
            single_url = get_full_url(original_url, single_url)
            
            request = Request(single_url, callback=self.level_2)
            
             
            try:
                request.meta["product"] = product
            except:
                pass
            try:
                request.meta["review"] = review
            except:
                pass
            yield request
    
    def level_2(self, response):
                                     
        original_url = response.url
        product = response.meta.get("product", {})
        review = response.meta.get("review", {})
        
        category_leaf_xpath = "(//ul[@class='breadcrumb']/li//text())[last()-1]"
        category_path_xpath = "//ul[@class='breadcrumb']/li//text()"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
                "source_internal_id": "//div[@id='comments']/@data-id",
                "ProductName":"(//ul[@class='breadcrumb']/li//text())[last()]",
                "OriginalCategoryName":"//ul[@class='breadcrumb']/li//text()",
                "PicURL": "//*[@property='og:image']/@content"
                            }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['TestUrl'] = original_url
        picurl = product.get("PicURL", "")
        if picurl and picurl[:2] == "//":
            product["PicURL"] = "https:" + product["PicURL"]
        if picurl and picurl[:1] == "/":
            product["PicURL"] = get_full_url(original_url, picurl)
        manuf = product.get("ProductManufacturer", "")
        if manuf == "" and ""[:2] != "//":
            product["ProductManufacturer"] = ""
        try:
            product["OriginalCategoryName"] = category['category_path']
        except:
            pass
        ocn = product.get("OriginalCategoryName", "")
        if ocn == "" and "//ul[@class='breadcrumb']/li//text()"[:2] != "//":
            product["OriginalCategoryName"] = "//ul[@class='breadcrumb']/li//text()"
        review_xpaths = { 
                
                "source_internal_id": "//div[@id='comments']/@data-id",
                
                
                "ProductName":"(//ul[@class='breadcrumb']/li//text())[last()]",
                
                
                "SourceTestRating":"//span[@class='reviewNot']//text()",
                
                
                "TestDateText":"//time[@itemprop='datePublished']/@content",
                
                
                "TestPros":"//li[@class='arti']//text()",
                
                
                "TestCons":"//li[@class='eksi']//text()",
                
                
                "TestSummary":"//div[@class='summary']//text()",
                
                
                
                "Author":"(//div[@id='article-info']//span[@itemprop='author']//text())[2]",
                
                
                "TestTitle":"//h1[@itemprop='headline']//text()",
                
                
                
                            }
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        review['TestUrl'] = original_url
        try:
            review['ProductName'] = product['ProductName']
            review['source_internal_id'] = product['source_internal_id']
        except:
            pass
        awpic_link = review.get("AwardPic", "")
        if awpic_link and awpic_link[:2] == "//":
            review["AwardPic"] = "https:" + review["AwardPic"]
        if awpic_link and awpic_link[:1] == "/":
            review["AwardPic"] = get_full_url(original_url, awpic_link)

        matches = None
        field_value = review.get("TestDateText", "")
        if field_value:
            matches = re.search("([\d-]+)(?=\s)", field_value, re.IGNORECASE)
        if matches:
            review["TestDateText"] = matches.group(1)
                                    

        review["SourceTestScale"] = "100"
                                    

        yield product


        
                            
        yield review
        
