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


class Consolemonster_enSpider(AlaSpider):
    name = 'consolemonster_en'
    allowed_domains = ['consolemonster.com']
    start_urls = ['http://www.consolemonster.com/category/reviews/']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        urls_xpath = "//div[contains(@class,'blog-two')]//a[img]/@href"
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
            
             
            yield request
        url_xpath = "//div[@class='pagination']/a[last()-1]/@href"
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
            
            yield request
    
    def level_2(self, response):
                                     
        original_url = response.url
        
        product_xpaths = { 
                
                
                "ProductName":"//meta[@property='og:title']/@content",
                
                
                "OriginalCategoryName":"game",
                
                
                "PicURL":"//meta[@property='og:image']/@content",
                
                
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
        if ocn == "" and "game"[:2] != "//":
            product["OriginalCategoryName"] = "game"

        matches = None
        field_value = product.get("ProductName", "")
        if field_value:
            matches = re.search("(.*)Review - Console Monster", field_value, re.IGNORECASE)
        if matches:
            product["ProductName"] = matches.group(1)
                                    
        review_xpaths = { 
                
                
                "ProductName":"//meta[@property='og:title']/@content",
                
                
                "SourceTestRating":"//div[@class='final-score']/text()",
                
                
                "TestDateText":"//meta[@property='article:published_time']/@content",
                
                
                "TestPros":"//div[@class='summary']/div[@class='pro']/text()",
                
                
                "TestCons":"//div[@class='summary']/div[@class='con']/text()",
                
                
                "TestSummary":"//div[@class='clearfix']/p[contains(.,'')][not(img)][1]//text()",
                
                
                "TestVerdict":"//div[@class='clearfix']/p[contains(.,'')][last()]//text()",
                
                
                "Author":"//a[@rel='author']/text()",
                
                
                "TestTitle":"//meta[@property='og:title']/@content",
                
                
                
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
        field_value = review.get("SourceTestRating", "")
        if field_value:
            matches = re.search("(.*) %", field_value, re.IGNORECASE)
        if matches:
            review["SourceTestRating"] = matches.group(1)
                                    

        review["DBaseCategoryName"] = "PRO"
                                    

        review["SourceTestScale"] = "100"
                                    

        if review["TestDateText"]:
            
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(review["TestDateText"], "%Y-%m-%dT%H:%M:%S%z", ["en"])
                                    

        yield product


        
                            
        yield review
        
