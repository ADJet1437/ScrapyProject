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


class Gottabemobile_comSpider(AlaSpider):
    name = 'gottabemobile_com'
    allowed_domains = ['gottabemobile.com']
    start_urls = ['http://www.gottabemobile.com/reviews/']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        url_xpath = "//ul[starts-with(@class,'page')]/li/a[starts-with(@class,'next')]/@href"
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
        urls_xpath = "//article//h2/a/@href"
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
                
                "source_internal_id": "substring-after(//article/@id,'-')",
                
                
                
                
                "PicURL":"//head/meta[contains(@name,'image')][1]/@content",
                
                
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
        review_xpaths = { 
                
                "source_internal_id": "substring-after(//article/@id,'-')",
                
                
                
                "SourceTestRating":"//span[contains(@class,'rating') and contains(@class,'result')]//text()",
                
                
                "TestDateText":"//span/time/@datetime",
                
                
                "TestPros":"//h3[contains(translate(.,' ',''),'WhatWeLike')]/following::ul[1]/li/text() | //p[contains(translate(.//text(),' ',''),'Whatwelike')]/text()",
                
                
                "TestCons":"//h3[contains(translate(.,' ',''),'WhatWeDo')]/following::ul[1]/li/text() | //p[contains(translate(.//text(),' ',''),'Whatwedo')]/text()",
                
                
                "TestSummary":"//article/descendant-or-self::*[(name()='section' and starts-with(@class,'cb-entry-content') and ./p) or (name()='div' and contains(@class,'summary'))][1]/p[string-length(normalize-space())>1][1]//text()",
                
                
                "TestVerdict":"//article/descendant-or-self::*[(name()='section' and starts-with(@class,'cb-entry') and ./p) or @itemprop='reviewBody'][last()]/p[string-length(normalize-space())>1 and (not(./preceding::h2) or ./preceding::*[string-length(normalize-space())>1][1][name()='h2']) and not(contains(.,'check') and contains(.,'later')) and not(contains(@onclick,'Amazon') and contains(@onclick,'$')) and not(./em)][last()]//text()",
                
                
                "Author":"//span[@class='cb-author']/a//text()",
                
                
                "TestTitle":"//title//text()",
                
                
                
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
                                    

        review["SourceTestScale"] = "5"
                                    

        yield product


        
                            
        yield review
        
