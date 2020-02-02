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


class Aktivtraning_seSpider(AlaSpider):
    name = 'aktivtraning_se'
    allowed_domains = ['aktivtraning.se']
    start_urls = ['http://aktivtraning.se/prylar/cykelutrustning','http://aktivtraning.se/prylar/pulsklocka']

    
    def parse(self, response):
                                     
        original_url = response.url
        product = response.meta.get("product", {})
        review = response.meta.get("review", {})
        
        url_xpath = "//body/descendant-or-self::div[@class='mdPagination'][1]//a[@rel='next']/@href"
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
        urls_xpath = "//ul[@class='mdList']//h3/a/@href"
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
        
        category_leaf_xpath = "//meta[@name='bi-sub-category']/@content"
        category_path_xpath = "//meta[@name='bi-category' or @name='bi-sub-category']/@content"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
                
                "source_internal_id": "//meta[contains(@name,'articleid')]/@content",
                
                
                "ProductName":"substring-before(//title//text(),'|')",
                
                
                "OriginalCategoryName":"//meta[@name='bi-category' or @name='bi-sub-category']/@content",
                
                
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
        if ocn == "" and "//meta[@name='bi-category' or @name='bi-sub-category']/@content"[:2] != "//":
            product["OriginalCategoryName"] = "//meta[@name='bi-category' or @name='bi-sub-category']/@content"
        review_xpaths = { 
                
                "source_internal_id": "//meta[contains(@name,'articleid')]/@content",
                
                
                "ProductName":"substring-before(//title//text(),'|')",
                
                
                "SourceTestRating":"translate(//p[contains(translate(.,' ',''),'av6')]//text() | //img[contains(@alt,'stjerner')]/@alt,',','.')",
                
                
                "TestDateText":"substring-before(//meta[contains(@name,'publish')]/@content,'T')",
                
                
                "TestPros":"//p[.//text()[normalize-space()='Plus:' or concat(substring(normalize-space(),1,1),'o',substring(normalize-space(),3))='Fordelar:']]//text()[./preceding::*[normalize-space()][1][normalize-space()='Plus:' or concat(substring(normalize-space(),1,1),'o',substring(normalize-space(),3))='Fordelar:']] | //p[normalize-space()='Plus:' or concat(substring(normalize-space(),1,1),'o',substring(normalize-space(),3))='Fordelar:']/following-sibling::p[string-length(normalize-space())>1][1]//text()",
                
                
                "TestCons":"//p[.//text()[normalize-space()='Minus:' or normalize-space()='Nackdelar:']]//text()[./preceding::*[normalize-space()][1][normalize-space()='Minus:' or normalize-space()='Nackdelar:']] | //p[normalize-space()='Minus:' or normalize-space()='Nackdelar:']/following-sibling::p[string-length(normalize-space())>1][1]//text()",
                
                
                "TestSummary":"//p[@id='deck']//text()",
                
                
                "TestVerdict":"//p[normalize-space()='Slutsats:']/following::p[string-length(normalize-space())>1][1]//text() | //p[starts-with(.,'Slutsats:')]//text()[./preceding::text()[normalize-space()='Slutsats:']]",
                
                
                "Author":"//meta[@property='og:site_name']/@content",
                
                
                "TestTitle":"//h1//text()",
                
                
                
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

        id_value = self.extract(response.xpath("//p[contains(.,'Pris:')]//text()[./preceding::text()[normalize-space()][1][normalize-space()='Pris:']]"))
        if id_value:
            product_id = self.product_id(product)
            product_id['ID_kind'] = "Price"
            product_id['ID_value'] = id_value
            yield product_id
        

        matches = None
        field_value = review.get("SourceTestRating", "")
        if field_value:
            matches = re.search("(\d\.*\d*(?=.stj))", field_value, re.IGNORECASE)
        if matches:
            review["SourceTestRating"] = matches.group(1)
                                    

        review["DBaseCategoryName"] = "PRO"
                                    

        review["SourceTestScale"] = "6"
                                    

        yield product


        
                            
        yield review
        
