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


class Exler_ruSpider(AlaSpider):
    name = 'exler_ru'
    allowed_domains = ['exler.ru']
    start_urls = ['https://www.exler.ru/expromt/byyears/']

    
    def parse(self, response):
                                     
        original_url = response.url
        product = response.meta.get("product", {})
        review = response.meta.get("review", {})
        
        urls_xpath = u"//td[@id='TopicRightText']//td/a/@href"
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
        
        urls_xpath = u"//table[./preceding-sibling::*[normalize-space()='Обзоры']]//tr//a/@href"
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
            
            request = Request(single_url, callback=self.level_3)
            
             
            try:
                request.meta["product"] = product
            except:
                pass
            try:
                request.meta["review"] = review
            except:
                pass
            yield request
    
    def level_3(self, response):
                                     
        original_url = response.url
        product = response.meta.get("product", {})
        review = response.meta.get("review", {})
        
        product_xpaths = { 
                
                
                "ProductName":u"//title//text()",
                
                
                "OriginalCategoryName":u"//div[@class='Topic']//text()",
                
                
                "PicURL":u"//div[@id='article']/descendant-or-self::img[1]/@src",
                
                
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
        if ocn == "" and u"//div[@class='Topic']//text()"[:2] != "//":
            product["OriginalCategoryName"] = u"//div[@class='Topic']//text()"
        review_xpaths = { 
                
                
                "ProductName":u"//title//text()",
                
                
                
                "TestDateText":u"//p[starts-with(.,'Дата')]//text()",
                
                
                "TestPros":u"//ul[./preceding-sibling::*[string-length(normalize-space())>1][1][normalize-space()='Плюсы:' or normalize-space()='Плюсы' or normalize-space()='Достоинства' or normalize-space()='Достоинства:']]/li//text()[normalize-space()]",
                
                
                "TestCons":u"//ul[./preceding-sibling::*[string-length(normalize-space())>1][1][normalize-space()='Минусы:' or normalize-space()='Минусы' or normalize-space()='Недостатки:' or normalize-space()='Недостатки']]/li//text()[normalize-space()]",
                
                
                "TestSummary":u"normalize-space(//div[@id='article']/p[@align='justify' or @align='JUSTIFY' and string-length(normalize-space())>1][1])",
                
                
                "TestVerdict":u"normalize-space(//div[@id='article']/descendant-or-self::p[contains(.,'выводы')]/following-sibling::p[string-length(normalize-space())>1][1])",
                
                
                "Author":u"//div[@class='FooterExler']//a//text()",
                
                
                "TestTitle":u"//title//text()",
                
                
                
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
                                    

        matches = None
        field_value = review.get("TestDateText", "")
        if field_value:
            matches = re.search("(\d{2}\.\d{2}\.\d{4})", field_value, re.IGNORECASE)
        if matches:
            review["TestDateText"] = matches.group(1)
                                    

        if review["TestDateText"]:
            
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(review["TestDateText"], "%d.%m.%Y", ["ru"])
                                    

        yield product


        
                            
        yield review
        
