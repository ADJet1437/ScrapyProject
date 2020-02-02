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


class Pinoytechblog_comSpider(AlaSpider):
    name = 'pinoytechblog_com'
    allowed_domains = ['pinoytechblog.com']
    start_urls = ['http://www.pinoytechblog.com/archives/category/reviews']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        urls_xpath = "//div[@class='awr']/h2[@class='entry-title']/a/@href"
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
        url_xpath = "//div[contains(@class,'pgn')]/a[contains(@class,'next')]/@href"
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
        
        category_leaf_xpath = "//div[contains(@class,'meta')]/descendant::div[contains(@class,'cat_b')][last()-1]//text()"
        category_path_xpath = "//div[contains(@class,'meta')]/descendant::div[contains(@class,'cat_b')]//text()"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
                
                
                "ProductName":"//div[@class='wrp']/h1[contains(@class,'title')]//text()",
                
                
                "OriginalCategoryName":"//div[contains(@class,'meta')]/descendant::div[contains(@class,'cat_b')]//text()",
                
                
                "PicURL":"//p[img][1]/img/@src|//p[a/img][1]/a/img/@src|//div[img][@style][1]/img/@src",
                
                
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
        ocn = product["OriginalCategoryName"]
        if ocn == "" and "//div[contains(@class,'meta')]/descendant::div[contains(@class,'cat_b')]//text()"[:2] != "//":
            product["OriginalCategoryName"] = "//div[contains(@class,'meta')]/descendant::div[contains(@class,'cat_b')]//text()"
        review_xpaths = { 
                
                
                "ProductName":"//div[@class='wrp']/h1[contains(@class,'title')]//text()",
                
                
                
                "TestDateText":"//div[contains(@class,'cat_b')]/../span/text()[last()]",
                
                
                "TestPros":"//p/strong[text()='Pros']/../text()",
                
                
                "TestCons":"//p/strong[text()='Cons']/../text()",
                
                
                "TestSummary":"//article/div[@class='awr']/p[not(*) or @style][1]//text()",
                
                
                "TestVerdict":"//p/strong[contains(text(),'Verdict') or contains(text(),'Conclusion')]/../following::p[text()][1]//text()",
                
                
                "Author":"//div[contains(@class,'cat_b')]/../span/a//text()",
                
                
                "TestTitle":"//div[@class='wrp']/h1[contains(@class,'title')]//text()",
                
                
                
                            }
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        review['TestUrl'] = original_url
        try:
            review['ProductName'] = product['ProductName']
            review['source_internal_id'] = product['source_internal_id']
        except:
            pass

        if review["TestDateText"]:
            
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(review["TestDateText"], "/ %B %d, %Y", ["en"])
                                    

        yield product


        review["DBaseCategoryName"] = "PRO"
                                    

        
                            
        yield review
        
