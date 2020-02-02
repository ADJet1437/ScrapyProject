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


class Cyberphoto_seSpider(AlaSpider):
    name = 'cyberphoto_se'
    allowed_domains = ['cyberphoto.se']
    start_urls = ['https://www.cyberphoto.se/bloggen']

    
    def parse(self, response):
                                     
        original_url = response.url
        product = response.meta.get("product", {})
        review = response.meta.get("review", {})
        
        url_xpath = "//span[contains(.,'ta sida')]/../@href"
        single_url = self.extract(response.xpath(url_xpath))
        single_url='/bloggen'+single_url
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
        urls_xpath = "//div[@class='blogg_big_container'][contains(.,'Test')]//a[contains(@href,'article')]/@href"
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
        
        category_leaf_xpath = "(//div[@id='breadcrumb_area']/a/text())[last()]"
        category_path_xpath = "//div[@id='breadcrumb_area']/a/text()"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
                
                
                "ProductName":"(//div[@id='breadcrumb_area']/following-sibling::h1)[1]/text()",
                
                
                "OriginalCategoryName":"//div[@id='breadcrumb_area']/a/text()",
                
                
                "PicURL":"(//div[@class='picture_container']/img/@src)[1]",
                
                
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
        if ocn == "" and "//div[@id='breadcrumb_area']/a/text()"[:2] != "//":
            product["OriginalCategoryName"] = "//div[@id='breadcrumb_area']/a/text()"
        review_xpaths = { 
                "ProductName":"(//div[@id='breadcrumb_area']/following-sibling::h1)[1]/text()",
                "TestDateText":"//p[contains(.,'Testad') and contains(.,'av')]/text()",
                "TestPros":"//*[contains(text(),'Plus') or contains(text(),'Mycket')]/../text()[normalize-space()]",
                "TestCons":"//*[contains(text(),'Minus') or contains(text(),'Mindre')]/../text()[normalize-space()]",
                "TestTitle":"(//div[@id='breadcrumb_area']/following-sibling::h1)[1]/text()",               
        }
        summary = self.extract_xpath(response, "//div[@class='tabcontent']//p[text()][1]/text()")
        verdict = self.extract_all_xpath(response, 
            "//*[contains(text(),'Slutsats') or contains(text(),'Sammanfattning')]/../text()[normalize-space()]",
            separator="\n")
        match1 = re.search('Slutsats\n+([^\n]+)', verdict)
        match2 = re.search('Sammanfattning\n+([^\n]+)', verdict)
        if match1:
            verdict = match1.group(1)
        elif match2:
            verdict = match2.group(1)
        

        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        review['TestUrl'] = original_url
        review['TestSummary'] = summary
        review['TestVerdict'] = verdict

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
            matches = re.search("(\d{4}-\d{2}-\d{2})", field_value, re.IGNORECASE)
        if matches:
            review["TestDateText"] = matches.group(1)
                                    

        review["DBaseCategoryName"] = "PRO"
                                    

        yield product


        
                            
        yield review
        
