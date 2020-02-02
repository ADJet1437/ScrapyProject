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


class Datormagazin_seSpider(AlaSpider):
    name = 'datormagazin_se'
    allowed_domains = ['datormagazin.se']
    start_urls = ['http://www.datormagazin.se/?s=test']

    
    def parse(self, response):
                                     
        original_url = response.url
        product = response.meta.get("product", {})
        review = response.meta.get("review", {})
        
        url_xpath = "//div[@class='nav-links']/*[contains(@class,'next')]/@href"
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
        urls_xpath = "//main//h3/a/@href"
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
                
                "source_internal_id": "substring-after(//link[@rel='shortlink']/@href,'p=')",
                
                
                "ProductName":"//h1//text()",
                
                
                "OriginalCategoryName":"//div[@class='tags-links']//a//text()",
                
                
                "PicURL":"//main/descendant-or-self::img[1]/@src",
                
                
                "ProductManufacturer":"//p//text()[./preceding::text()[normalize-space()][1][normalize-space()='Tillverkare:']]"
                
                            }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['TestUrl'] = original_url
        picurl = product.get("PicURL", "")
        if picurl and picurl[:2] == "//":
            product["PicURL"] = "https:" + product["PicURL"]
        if picurl and picurl[:1] == "/":
            product["PicURL"] = get_full_url(original_url, picurl)
        manuf = product.get("ProductManufacturer", "")
        if manuf == "" and "//p//text()[./preceding::text()[normalize-space()][1][normalize-space()='Tillverkare:']]"[:2] != "//":
            product["ProductManufacturer"] = "//p//text()[./preceding::text()[normalize-space()][1][normalize-space()='Tillverkare:']]"
        try:
            product["OriginalCategoryName"] = category['category_path']
        except:
            pass
        ocn = product.get("OriginalCategoryName", "")
        if ocn == "" and "//div[@class='tags-links']//a//text()"[:2] != "//":
            product["OriginalCategoryName"] = "//div[@class='tags-links']//a//text()"
        review_xpaths = { 
                
                "source_internal_id": "substring-after(//link[@rel='shortlink']/@href,'p=')",
                
                
                "ProductName":"//h1//text()",
                
                
                "SourceTestRating":"//div[contains(@class,'entry-content')]/descendant-or-self::div[@*='reviewRating'][1]/span[@*='ratingValue']//text()",
                
                
                "TestDateText":"//meta[@property='datePublished']/@content",
                
                
                "TestPros":"//main/descendant-or-self::div[@class='rwp-pros'][1]//text()",
                
                
                "TestCons":"//main/descendant-or-self::div[@class='rwp-cons'][1]//text()",
                
                
                "TestSummary":"//div[contains(@class,'entry-content')]/p[string-length(normalize-space())>1][1]//text()[normalize-space()] | //div[contains(@class,'entry-content') and not(./p[string-length(normalize-space())>1])]/descendant-or-self::div[contains(@class,'textwidget')][1]//text()[normalize-space()]",
                
                
                "TestVerdict":"//main/descendant-or-self::div[@class='rwp-summary'][1]//text()",
                
                
                "Author":"//div[contains(@class,'entry-content')]/p[starts-with(.,'Av') and ./strong and not(./text())][last()]//text() | //span[@class='byline' and not(//div[contains(@class,'entry-content')]/p[starts-with(.,'Av') and ./strong])]//span[contains(@class,'author')]//text()",
                
                
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
                                    

        review["SourceTestScale"] = "6"
                                    

        matches = None
        field_value = product.get("ProductManufacturer", "")
        if field_value:
            matches = re.search("(\w+(?=\,\s[^\s]+\.))", field_value, re.IGNORECASE)
        if matches:
            product["ProductManufacturer"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("Author", "")
        if field_value:
            matches = re.search("((?<=Av\s)\w.*\w)", field_value, re.IGNORECASE)
        if matches:
            review["Author"] = matches.group(1)
                                    

        yield product


        
                            
        yield review
        
