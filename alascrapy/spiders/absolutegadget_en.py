# -*- coding: utf8 -*-
from datetime import datetime
import re

from scrapy.http import Request, HtmlResponse
from scrapy.selector import Selector

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import CategoryItem, ProductItem, ReviewItem, ProductIdItem
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from alascrapy.lib.selenium_browser import SeleniumBrowser


class Absolutegadget_enSpider(AlaSpider):
    name = 'absolutegadget_en'
    allowed_domains = ['absolutegadget.com']
    start_urls = ['http://www.absolutegadget.com/category/s4-reviews']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        urls_xpath = "//div[contains(@class,'main-content')]//a[img]/@href"
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
        url_xpath = "//div[contains(@class,'padding')]/a[last()]/@href"
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
        
        category_leaf_xpath = "//div[@class='entry-crumbs']/span[last()-1]//text()"
        category_path_xpath = "//div[@class='entry-crumbs']/span//text()"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
                
                
                "ProductName":"//h1[@class='entry-title']/text()",
                
                
                
                "PicURL":"//meta[@property='og:image'][1]/@content",
                
                
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
        if ocn == "" and ""[:2] != "//":
            product["OriginalCategoryName"] = ""

        matches = None
        field_value = product.get("ProductName", "")
        if field_value:
            matches = re.search("(.*)review", field_value, re.IGNORECASE)
        if matches:
            product["ProductName"] = matches.group(1)
                                    
        review_xpaths = { 
                
                
                "ProductName":"//h1[@class='entry-title']/text()",
                
                
                "SourceTestRating":"//div[contains(@class,'final-score')]/text()",
                
                
                "TestDateText":"//meta[@property='article:published_time']/@content",
                
                
                
                
                "TestSummary":"(//td[@class='td-review-summary']/div/text() | //div[contains(@class,'content')]/p[text()][1]/text())[last()]",
                
                
                "TestVerdict":"//*[contains(.,'Conclusion') or contains(.,'Verdict')]/following-sibling::p[text()][1]/text()",
                
                
                "Author":"//meta[@name='author']/@content",
                
                
                "TestTitle":"//h1[@class='entry-title']/text()",
                
                
                
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

        review["DBaseCategoryName"] = "PRO"
                                    

        review["SourceTestScale"] = "5"
                                    

        if review["TestDateText"]:
            
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(review["TestDateText"], "%Y-%m-%dT%H:%M:%S%z", ["en"])
                                    

        yield product


        
                            
        yield review
        
