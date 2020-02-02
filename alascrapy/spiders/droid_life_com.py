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


class Droid_life_comSpider(AlaSpider):
    name = 'droid_life_com'
    allowed_domains = ['droid-life.com']
    start_urls = ['http://www.droid-life.com/category/reviews/']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        url_xpath = "//div[@class='nav-previous']/a/@href"
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
        urls_xpath = "//article//h1/a/@href"
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
                
                "source_internal_id": "substring-after(//link[@rel='shortlink']/@href,'?p=')",
                
                
                
                "OriginalCategoryName":"//span[@class='cat-links']/a[not(contains(.,'News') or contains(.,'Featured'))]/text()",
                
                
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
        if ocn == "" and "//span[@class='cat-links']/a[not(contains(.,'News') or contains(.,'Featured'))]/text()"[:2] != "//":
            product["OriginalCategoryName"] = "//span[@class='cat-links']/a[not(contains(.,'News') or contains(.,'Featured'))]/text()"
        review_xpaths = { 
                
                "source_internal_id": "substring-after(//link[@rel='shortlink']/@href,'?p=')",
                
                
                
                
                "TestDateText":"substring-before(//time/@datetime,'T')",
                
                
                "TestPros":"//p[(./strong or ./b) and not(./text()) and ./preceding::*[name()='h3' or name()='h4'][contains(translate(.,' ',''),'TheGood') or contains(translate(.,' ',''),'WhatILike')] and (./following::*[name()='h3' or name()='h4'][contains(.,'in-the-Middle') or contains(translate(normalize-space(),' ',''),'intheMiddle')] or ./following::*[name()='h3' or name()='h4'][contains(.,'Not-so-Good') or contains(translate(.,' ',''),'NotSoGood') or contains(translate(.,' ',''),'WhatIDon')]) and not(.//*[contains(.,'in-the-Middle') or contains(translate(normalize-space(),' ',''),'intheMiddle')])]//text() | //ul/li/strong[./preceding::*[contains(translate(.,' ',''),'TheGood')] and ./following::*[contains(.,'Not-so-Good') or contains(translate(.,' ',''),'NotSoGood')]]/text() | //h4[./preceding::h3[contains(translate(.,' ',''),'TheGood')] and (./following::h3[contains(.,'in-the-Middle')] or ./following::h3[contains(translate(.,' ',''),'intheMiddle')] or ./following::h3[(contains(.,'Not-so-Good') or contains(translate(.,' ',''),'NotSoGood')) and not(.//*[contains(.,'in-the-Middle') or contains(translate(normalize-space(),' ',''),'intheMiddle')])])]//text()",
                
                
                "TestCons":"//p[(./strong or ./b) and not(./text()) and ./preceding::*[name()='h3' or name()='h4'][1][contains(.,'Not-so-Good') or contains(translate(.,' ',''),'NotSoGood') or contains(translate(.,' ',''),'WhatIDon')]]//text() | //ul/li/strong[./preceding::*[contains(.,'Not-so-Good') or contains(translate(.,' ',''),'NotSoGood')] and not(./preceding::*[contains(translate(.,' ',''),'OtherNotes')])]/text() | //h3[contains(.,'Not-so-Good') or contains(translate(.,' ',''),'NotSoGood')]/following::h4[not(preceding::h3[contains(translate(.,' ',''),'OtherNotes')])]/text()",
                
                
                "TestSummary":"//div[@class='entry-content']//*[name()='h4' or name()='h3' or name()='h2'][1]/preceding::p[not((contains(.,'our') or contains(.,'my')) and contains(.,'review.')) and string-length(normalize-space())>1][last()]//text() | //div[@class='entry-content' and not(./descendant::*[name()='h2' or name()='h3' or name()='h4'])]/descendant::p[string-length(normalize-space())>1][1]//text()",
                
                
                "TestVerdict":"//*[contains(translate(.,' ',''),'Verdict') or contains(translate(.,' ',''),'FinalThoughts') or contains(translate(.,' ',''),'Finalthoughts') or contains(translate(.,' ',''),'Shouldyoubuy')]/following-sibling::p[1]//text()",
                
                
                "Author":"//span[starts-with(@class,'author')]//text()",
                
                
                "TestTitle":"//header/h1[@class='entry-title']//text()",
                
                
                
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
            
            review["ProductName"] = review["ProductName"].strip("-: ")
            product["ProductName"] = review["ProductName"]

        review["DBaseCategoryName"] = "PRO"
                                    

        yield product


        
                            
        yield review
        
