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


class Gsmonline_plSpider(AlaSpider):
    name = 'gsmonline_pl'
    allowed_domains = ['gsmonline.pl']
    start_urls = ['http://gsmonline.pl/testy?page=1']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        url_xpath = "concat('/testy',//div[@class='pagination']/a[last()]/@href)"
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
        urls_xpath = "//div[@class='column_left_wide']//ul[contains(@id,'article_list')]/li//h4/a/@href"
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
    
    def level_2(self, response):
                                     
        original_url = response.url
        
        product_xpaths = { 
                
                "source_internal_id": "//*[@*='comment_commentable_id']/@value",
                
                
                "ProductName":"//meta[@property='og:title']/@content",
                
                
                "OriginalCategoryName":"//meta[@property='og:type']/@content",
                
                
                "PicURL":"(//table[1]//td[//img][1]//a[@class='fancybox']/img/@src | //meta[@property='og:image']/@content)[last()]",
                
                
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
        if ocn == "" and "//meta[@property='og:type']/@content"[:2] != "//":
            product["OriginalCategoryName"] = "//meta[@property='og:type']/@content"
        review_xpaths = { 
                
                "source_internal_id": "//*[@*='comment_commentable_id']/@value",
                
                
                "ProductName":"//meta[@property='og:title']/@content",
                
                
                
                "TestDateText":"substring-before(normalize-space(//span[@class='article_date']//text()),' ')",
                
                
                "TestPros":"//*[starts-with(normalize-space(),'Zalety') or .//text()[starts-with(normalize-space(),'Zalety')]]/following::*[string-length(normalize-space())>1][1][name()='ul']/li//text() | //*[starts-with(normalize-space(),'Zalety')]/following::*[string-length(normalize-space())>1][1][name()='p' and starts-with(normalize-space(),'+')]//text()",
                
                
                "TestCons":"//*[starts-with(normalize-space(),'Wady') or .//text()[starts-with(normalize-space(),'Wady')]]/following::*[string-length(normalize-space())>1][1][name()='ul']/li//text() | //*[starts-with(normalize-space(),'Wady')]/following::*[string-length(normalize-space())>1][1][name()='p' and starts-with(normalize-space(),'-')]//text()",
                
                
                "TestSummary":"//meta[@property='og:description']/@content",
                
                
                "TestVerdict":"//*[contains(.,'Podsumowanie')]/following-sibling::p[string-length(normalize-space())>1][1]//text()",
                
                
                "Author":"//span[contains(.,'autor:')]//a//text()",
                
                
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

        review["DBaseCategoryName"] = "PRO"
                                    

        yield product


        
                            
        yield review
        
