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


class Fotosidan_seSpider(AlaSpider):
    name = 'fotosidan_se'
    allowed_domains = ['fotosidan.se']
    start_urls = ['http://www.fotosidan.se/articles.htm']

    
    def parse(self, response):
                                     
        original_url = response.url
        product = response.meta.get("product", {})
        review = response.meta.get("review", {})
        
        url_xpath = u"(//a[@class='pagectl pagectlnext'])[1]/@href"
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
        urls_xpath = u"//div[div[@class='documentdescription'][contains(text(),'Fotosidan testar')]]/div[@class='documentlisttitle']/a/@href"
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
        
        product_xpaths = { 
                
                
                "ProductName":u"//div[contains(@id,'content')]/h1/text()",
                
                
                
                "PicURL":u"//div[@id='supersuperingress']/div/img/@src",
                
                
                            }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['TestUrl'] = original_url
        picurl = product.get("PicURL", "")
        if picurl and picurl[:2] == "//":
            product["PicURL"] = "https:" + product["PicURL"]
        if picurl and picurl[:1] == "/":
            product["PicURL"] = get_full_url(original_url, picurl)
        manuf = product.get("ProductManufacturer", "")
        if manuf == "" and u""[:2] != "//":
            product["ProductManufacturer"] = u""
        try:
            product["OriginalCategoryName"] = category['category_path']
        except:
            pass
        ocn = product.get("OriginalCategoryName", "")
        if ocn == "" and u""[:2] != "//":
            product["OriginalCategoryName"] = u""
        review_xpaths = { 
                
                
                "ProductName":u"//div[contains(@id,'content')]/h1/text()",
                
                
                
                "TestDateText":u"//div[@class='document']//div[@class='docinfo']//br/following::text()[1][normalize-space()]",
                
                
                "TestPros":u"//h3[contains(.,'PLUS')]/following::p[1]//text()",
                
                
                "TestCons":u"//h3[contains(.,'MINUS')]/following::p[1]//text()",
                
                
                "TestSummary":u"//meta[@name='description']/@content",
                
                
                "TestVerdict":u"//h2[text()='Slutsats']/following::p[1]//text()",
                
                
                "Author":u"//div[@class='document']//div[@class='docinfo']//a[contains(@href,'/member')]/text()",
                
                
                "TestTitle":u"//div[contains(@id,'content')]/h1/text()",
                
                
                
                "AwardPic":u"(//div[@class='sidebarpart' and @id='sidebar-text']//p//text()[normalize-space()])[last()]/following::a[1]/img[last()-1]/@src"
                
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
            matches = re.search("(\d{4}-\d{2}-\d{2})", field_value, re.IGNORECASE)
        if matches:
            review["TestDateText"] = matches.group(1)
                                    

        review["DBaseCategoryName"] = "PRO"
                                    

        yield product


        
                            
        yield review
        
