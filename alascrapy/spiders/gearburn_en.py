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


class Gearburn_enSpider(AlaSpider):
    name = 'gearburn_en'
    allowed_domains = ['gearburn.com']
    start_urls = ['http://gearburn.com/category/reviews/']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        urls_xpath = "//ul[@class='archive-list']//h2/a/@href"
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
        url_xpath = "//a[contains(text(),'Next')]/@href"
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
                
                
                "ProductName":"//div[contains(@class,'headline')]/h1/text()",
                
                
                "OriginalCategoryName":"//div[@id='crumbs']/a/text()",
                
                
                "PicURL":"//meta[@property='og:image'][1]/@content",
                
                
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
        if ocn == "" and "//div[@id='crumbs']/a/text()"[:2] != "//":
            product["OriginalCategoryName"] = "//div[@id='crumbs']/a/text()"
        review_xpaths = { 
                
                
                "ProductName":"//div[contains(@class,'headline')]/h1/text()",
                
                
                "SourceTestRating":" (//p[contains(text(), '/10')]/text() | //p/strong[contains(text(), '/10')]/text() | //p[strong[contains(text(),'Score')]]/text()[last()])[last()]",
                
                
                "TestDateText":"//meta[@property='article:published_time']/@content",
                
                
                "TestPros":"//*[contains(text(),'Positives')]/following-sibling::*[1]/*/text() | //*[*[contains(text(),'Positives')]]/following-sibling::*[1]/*/text()",
                
                
                "TestCons":"//*[contains(text(),'Negatives')]/following-sibling::*[1]/*/text() | //*[*[contains(text(),'Negatives')]]/following-sibling::*[1]/*/text()",
                
                
                "TestSummary":"//meta[@property='og:description']/@content",
                
                
                "TestVerdict":"//*[*[contains(text(),'Verdict') or contains(text(),'Nutshell')]]/text() | //p[contains(text(),'Verdict')]/text() | //*[*[contains(text(),'Verdict')]]/following-sibling::*[1]/text()",
                
                
                "Author":"//span[@class='post-byline']/a[@rel='author']/text()",
                
                
                "TestTitle":"//div[@class='story-headline']/h1/text()",
                
                
                
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
        field_value = review.get("SourceTestRating", "")
        if field_value:
            matches = re.search(":*\s*(\d.*\d*)/10.*", field_value, re.IGNORECASE)
        if matches:
            review["SourceTestRating"] = matches.group(1)
                                    

        review["DBaseCategoryName"] = "PRO"
                                    

        review["SourceTestScale"] = "10"
                                    

        if review["TestDateText"]:
            
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(review["TestDateText"], "%Y-%m-%dT%I:%M:%S%z", ["en"])
                                    

        yield product


        
                            
        yield review
        
