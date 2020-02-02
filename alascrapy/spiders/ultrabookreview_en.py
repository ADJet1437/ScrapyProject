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


class Ultrabookreview_enSpider(AlaSpider):
    name = 'ultrabookreview_en'
    allowed_domains = ['ultrabookreview.com']
    start_urls = ['http://www.ultrabookreview.com/reviews/']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        urls_xpath = "//ul[@class='archive-list']//a[img]/@href"
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
        urls_xpath = "//div[@class='pagination']/a/@href"
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
            
            request = Request(single_url, callback=self.parse)
            
             
            yield request
    
    def level_2(self, response):
                                     
        original_url = response.url
        
        product_xpaths = { 
                
                
                "ProductName":"//h1[contains(@class,'headline')]/text()",
                
                
                "OriginalCategoryName":"UltraBook",
                
                
                "PicURL":"//meta[@property='og:image'][2]/@content",
                
                
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
        if ocn == "" and "UltraBook"[:2] != "//":
            product["OriginalCategoryName"] = "UltraBook"
        review_xpaths = { 
                
                
                "ProductName":"//h1[contains(@class,'headline')]/text()",
                
                
                "SourceTestRating":"//span[@class='rating']/text()",
                
                
                "TestDateText":"(//span[@class='updated']/abbr/@title | //span[@class='updated']/text())[1]",
                
                
                "TestPros":"//p[contains(text(),'GOOD')]/following-sibling::p/text()",
                
                
                "TestCons":"//p[contains(text(),'BAD')]/following-sibling::p/text()",
                
                
                "TestSummary":"(//span[@class='description']/span/text() | //div[@id='content-area']/p[1]/text())[1] | //h2[text()='Summary']/following-sibling::p[1]/text()",
                
                
                "TestVerdict":"(//h2[contains(text(),'Wrap') or contains(text(),'thoughts')]/following-sibling::p[1]/text()[1] | //h2[@id='a9']/following-sibling::p[1]/text())[1]",
                
                
                "Author":"(//span[@class='reviewer']//a/text() | //span[contains(@class,'author')]//a/text())[1]",
                
                
                "TestTitle":"//h1[contains(@class,'headline')]/text() ",
                
                
                
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
            matches = re.search("(.*)review.*", field_value, re.IGNORECASE)
        if matches:
            product["ProductName"] = matches.group(1)
                                    

        if review["TestDateText"]:
            
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(review["TestDateText"], "%b %d, %Y", ["en"])
                                    

        yield product


        
                            
        yield review
        
