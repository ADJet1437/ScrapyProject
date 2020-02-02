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


class Homecinemamagazine_nlSpider(AlaSpider):
    name = 'homecinemamagazine_nl'
    allowed_domains = ['homecinemamagazine.nl']
    start_urls = ['https://www.homecinemamagazine.nl/category/reviews/']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        urls_xpath = "//div[contains(@class,'content-area')]//h2/a/@href"
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
        url_xpath = "//a[@class='nextpostslink']/@href"
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
        
        category_leaf_xpath = "//div[@class='breadcrumbs']//span[contains(@class,'last')]//text()"
        category_path_xpath = "//div[@class='breadcrumbs']//span//text()"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
                
                
                
                "OriginalCategoryName":"//div[@class='breadcrumbs']//span//text()",
                
                
                "PicURL":"//div[@id='thumbnail']//img/attribute::*[name()='src' or name()='srcset']",
                
                
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
        if ocn == "" and "//div[@class='breadcrumbs']//span//text()"[:2] != "//":
            product["OriginalCategoryName"] = "//div[@class='breadcrumbs']//span//text()"
        review_xpaths = { 
                
                
                
                "SourceTestRating":"(//span[@class='rating']/span[@class='value']//text()|//div[@class='content']//img[contains(@title,'Star')]/@title)[1]",
                
                
                "TestDateText":"//span[@class='meta-date']/text()",
                
                
                "TestPros":"(//div[@class='rating-positive']//li//text()|//p/strong[contains(text(),'Pluspunten')]/../text())[1]",
                
                
                "TestCons":"(//div[@class='rating-negative']//li//text()|//p/strong[contains(text(),'Minpunten')]/../text())[1]",
                
                
                "TestSummary":"//div[@class='content']/p[text()][string-length(text())>5][1]//text()",
                
                
                "TestVerdict":"(//h2|//h3)[contains(text(),'conclusie') or contains(text(),'Conclusie')][1]/following::p[text()][1]//text()",
                
                
                "Author":"//span[@class='meta-author']/a//text()",
                
                
                "TestTitle":"//div[contains(@class,'content-area')]/h1//text()",
                
                
                
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
            
            review["ProductName"] = review["ProductName"].replace("Review:".lower(), "")
            
            review["ProductName"] = review["ProductName"].strip("-: ")
            product["ProductName"] = review["ProductName"]

        review["SourceTestScale"] = "10"
                                    

        if review["TestDateText"]:
            
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(review["TestDateText"], "%d %B %Y", ["nl"])
                                    

        matches = None
        field_value = review.get("SourceTestRating", "")
        if field_value:
            matches = re.search("(\d|\d.\d)", field_value, re.IGNORECASE)
        if matches:
            review["SourceTestRating"] = matches.group(1)
                                    

        matches = None
        field_value = product.get("PicURL", "")
        if field_value:
            matches = re.search("(http[^ ]+\.jpg(?! 2x))", field_value, re.IGNORECASE)
        if matches:
            product["PicURL"] = matches.group(1)
                                    

        yield product


        review["DBaseCategoryName"] = "PRO"
                                    

        
                            
        yield review
        
