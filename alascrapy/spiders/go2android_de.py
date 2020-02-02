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


class Go2android_deSpider(AlaSpider):
    name = 'go2android_de'
    allowed_domains = ['go2android.de']
    start_urls = ['http://www.go2android.de/test/']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        url_xpath = "//div[@class='navigation']/a[contains(@class,'next')]/@href"
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
        urls_xpath = "//div[starts-with(@id,'recent-post')]/div[starts-with(@id,'post')]//h2/a/@href"
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
                
                "source_internal_id": "substring-before(substring-after(//body/@class,'postid-'),' ')",
                
                
                "ProductName":"//h1//text()",
                
                
                "OriginalCategoryName":"//ul[./preceding-sibling::a[1][normalize-space(./text())='Tests']]//li[contains(//div[starts-with(@id,'post-')]/@class,substring-before(substring-after(./a/@href,'/test/'),'/'))]/a[contains(@href,'test')]/text() | //li/a[normalize-space(./text())='Tests']/text()",
                
                
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
        if ocn == "" and "//ul[./preceding-sibling::a[1][normalize-space(./text())='Tests']]//li[contains(//div[starts-with(@id,'post-')]/@class,substring-before(substring-after(./a/@href,'/test/'),'/'))]/a[contains(@href,'test')]/text() | //li/a[normalize-space(./text())='Tests']/text()"[:2] != "//":
            product["OriginalCategoryName"] = "//ul[./preceding-sibling::a[1][normalize-space(./text())='Tests']]//li[contains(//div[starts-with(@id,'post-')]/@class,substring-before(substring-after(./a/@href,'/test/'),'/'))]/a[contains(@href,'test')]/text() | //li/a[normalize-space(./text())='Tests']/text()"
        review_xpaths = { 
                
                "source_internal_id": "substring-before(substring-after(//body/@class,'postid-'),' ')",
                
                
                "ProductName":"//h1//text()",
                
                
                "SourceTestRating":"substring-before(substring-after(//table[contains(.,'Wertung')]/following::img[1]/@src,'rating_'),'.jpg')",
                
                
                "TestDateText":"substring-before(//meta[contains(@property,'published_time')]/@content,'T')",
                
                
                "TestPros":"//div[@class='entry']/descendant-or-self::*[normalize-space()='Positiv'][1]/following::ul[1]/li//text()",
                
                
                "TestCons":"//div[@class='entry']/descendant-or-self::*[normalize-space()='Negativ'][1]/following::ul[1]/li//text()",
                
                
                "TestSummary":"//div[@class='entry']/p[string-length(normalize-space())>1][1]//text()",
                
                
                "TestVerdict":"//*[(name()='h2' or name()='h3') and contains(.,'Fazit')]/following::p[string-length(normalize-space(./text()))>1][1]//text()[1]",
                
                
                "Author":"//div[@class='meta-author']/a/text()",
                
                
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

        review["DBaseCategoryName"] = "PRO"
                                    

        review["SourceTestScale"] = "5"
                                    

        matches = None
        field_value = product.get("ProductName", "")
        if field_value:
            matches = re.search("((?<=\[Test\]).*)", field_value, re.IGNORECASE)
        if matches:
            product["ProductName"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("ProductName", "")
        if field_value:
            matches = re.search("((?<=\[Test\]).*)", field_value, re.IGNORECASE)
        if matches:
            review["ProductName"] = matches.group(1)
                                    

        yield product


        
                            
        yield review
        
