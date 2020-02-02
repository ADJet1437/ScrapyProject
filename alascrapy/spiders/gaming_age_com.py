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


scores = {"A+":"13", "A":"12", "A-":"11", "B+":"10", "B":"9", "B-":"8", "C+":"7", "C":"6", "C-":"5", "D+":"4", "D":"3", "D-":"2", "F":"1"}


class Gaming_age_comSpider(AlaSpider):
    name = 'gaming_age_com'
    allowed_domains = ['gaming-age.com']
    start_urls = ['http://www.gaming-age.com/reviews/']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        urls_xpath = "//div[@class='entries-wrapper']//div[contains(@class,'clearfix')]//h2/a/@href"
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
        url_xpath = "//div[contains(@class,'post-nav')]/p[@class='previous']/a/@href"
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
                
                
                
                "OriginalCategoryName":"game",
                
                
                "PicURL":"(//div[contains(@class,'entry-content')]/p[*/img or img][1] | //div[contains(@class,'entry-content')]//a[*/img or img][1])[1]//img/@src",
                
                
                "ProductManufacturer":"//span[@class='amazon-manufacturer']/text()"
                
                            }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['TestUrl'] = original_url
        picurl = product.get("PicURL", "")
        if picurl and picurl[:2] == "//":
            product["PicURL"] = "https:" + product["PicURL"]
        if picurl and picurl[:1] == "/":
            product["PicURL"] = get_full_url(original_url, picurl)
        manuf = product.get("ProductManufacturer", "")
        if manuf == "" and "//span[@class='amazon-manufacturer']/text()"[:2] != "//":
            product["ProductManufacturer"] = "//span[@class='amazon-manufacturer']/text()"
        try:
            product["OriginalCategoryName"] = category['category_path']
        except:
            pass
        ocn = product.get("OriginalCategoryName", "")
        if ocn == "" and "game"[:2] != "//":
            product["OriginalCategoryName"] = "game"
        review_xpaths = { 
                
                
                
                "SourceTestRating":"//div[@class='review_grade']/*//text()",
                
                
                "TestDateText":"//p[contains(@class,'post-date-inline')]/abbr[@class='published']//text()",
                
                
                
                
                "TestSummary":"//div[contains(@class,'entry-content')]/p[string-length(text())>5][1]//text()",
                
                
                
                "Author":"//p[contains(@class,'post-author')]/span[contains(@class,'nickname')]//text()",
                
                
                "TestTitle":"//h1[contains(@class,'entry-title')]//text()",
                
                
                
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
        if review and review['TestTitle']:
            title = review["TestTitle"].lower()
            if ":" in title:
                all_title_parts = title.split(":")
                for part in all_title_parts:
                    review["ProductName"] = part.replace("review", "") if 'review' in part else title.replace("review", "")
            else:
                review["ProductName"] = title.replace("review", "")
            
            review["ProductName"] = review["ProductName"].replace("review".lower(), "")
            
            review["ProductName"] = review["ProductName"].strip("-: ")
            product["ProductName"] = review["ProductName"]

        review["SourceTestScale"] = "13"
                                    

        if review["TestDateText"]:
            
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(review["TestDateText"], "%B %d, %Y", ["en"])
                                    

        yield product


        review["DBaseCategoryName"] = "PRO"
                                    

        review["SourceTestRating"] = scores.get(review["SourceTestRating"], "")
                            
        yield review
        
