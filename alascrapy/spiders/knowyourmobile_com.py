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


class Knowyourmobile_comSpider(AlaSpider):
    name = 'knowyourmobile_com'
    allowed_domains = ['knowyourmobile.com']
    start_urls = ['http://www.knowyourmobile.com/reviews']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        urls_xpath = "//div[@id='content']//div[@class='view-content']//h2/span/a/@href"
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
        url_xpath = "//ul[@class='pager']/li[contains(@class,'pager-next')]/a/@href"
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
        
        category_leaf_xpath = "//div[@id='breadcrumbs-inner']/a[last()]//text()"
        category_path_xpath = "//div[@id='breadcrumbs-inner']/a//text()"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
                
                "source_internal_id": "//link[@rel='canonical']/@href",
                
                
                
                "OriginalCategoryName":"//div[@id='breadcrumbs-inner']/a//text()",
                
                
                "PicURL":"//span[@class='date-display-single']/following::img[1]/@src",
                
                
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
        if ocn == "" and "//div[@id='breadcrumbs-inner']/a//text()"[:2] != "//":
            product["OriginalCategoryName"] = "//div[@id='breadcrumbs-inner']/a//text()"
        review_xpaths = { 
                
                "source_internal_id": "//link[@rel='canonical']/@href",
                
                
                
                "SourceTestRating":"//div[@class='group_details']//div[contains(@class,'star-first')]/span[@class='on']//text()",
                
                
                "TestDateText":"//span[@class='date-display-single']/@content",
                
                
                "TestPros":"//div[@class='field-label'][starts-with(.//text(),'Pros')]/following::div[contains(@class,'field-item')][1]//text()",
                
                
                "TestCons":"//div[@class='field-label'][starts-with(.//text(),'Cons')]/following::div[contains(@class,'field-item')][1]//text()",
                
                
                "TestSummary":"//div[contains(@class, 'premium')]/p[1]/text()",
                
                
                "TestVerdict":"//div[@class='field-label'][starts-with(.//text(),'Verdict')]/following::div[contains(@class,'field-item')][1]//text()",
                
                
                "Author":"//span[contains(@class,'field-name-field-author')]//a//text()",
                
                
                "TestTitle":"//h1[@class='title']//text()",
                
                
                
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
        field_value = product.get("source_internal_id", "")
        if field_value:
            matches = re.search("((?<=/)\d{4,10}(?=/))", field_value, re.IGNORECASE)
        if matches:
            product["source_internal_id"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("source_internal_id", "")
        if field_value:
            matches = re.search("((?<=/)\d{4,10}(?=/))", field_value, re.IGNORECASE)
        if matches:
            review["source_internal_id"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("TestDateText", "")
        if field_value:
            matches = re.search("(\d{4}-\d{2}-\d{2})", field_value, re.IGNORECASE)
        if matches:
            review["TestDateText"] = matches.group(1)
                                    

        review["SourceTestScale"] = "5"
                                    
        if review and review['TestTitle']:
            title = review["TestTitle"].lower()
            if ":" in title:
                all_title_parts = title.split(":")
                for part in all_title_parts:
                    review["ProductName"] = part.replace("review", "") if 'review' in part else title.replace("review", "")
            else:
                review["ProductName"] = title.replace("review", "")
            
            review["ProductName"] = review["ProductName"].strip("-: ")
            product["ProductName"] = review["ProductName"]

        yield product


        review["DBaseCategoryName"] = "PRO"
                                    

        
                            
        yield review
        
