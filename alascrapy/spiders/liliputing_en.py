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


class Liliputing_enSpider(AlaSpider):
    name = 'liliputing_en'
    allowed_domains = ['liliputing.com']
    start_urls = ['http://liliputing.com/category/reviews']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        urls_xpath = "//h2[@itemprop='headline']/a/@href"
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
                
                
                "ProductName":"//h1[@itemprop='headline']/text()",
                
                
                "OriginalCategoryName":"liliputing.com",
                
                
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
        ocn = product["OriginalCategoryName"]
        if ocn == "" and "liliputing.com"[:2] != "//":
            product["OriginalCategoryName"] = "liliputing.com"
        review_xpaths = { 
                
                
                "ProductName":"//h1[@itemprop='headline']/text()",
                
                
                
                "TestDateText":"//time[1]/text()",
                
                
                
                
                "TestSummary":"//div[@itemprop='text']/p[1]/text()",
                
                
                "TestVerdict":"(//h3[contains(text(),'Verdict')]/following-sibling::p[1]//text() | //div[@itemprop='text']/p[text()][last()]//text())[1]",
                
                
                "Author":"//a[@rel='author']/span[@itemprop='name']/text()",
                
                
                "TestTitle":"//h1[@itemprop='headline']/text()",
                
                
                
                            }
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        review['TestUrl'] = original_url
        try:
            review['ProductName'] = product['ProductName']
            review['source_internal_id'] = product['source_internal_id']
        except:
            pass

        review["DBaseCategoryName"] = "PRO"
                                    

        if review["TestDateText"]:
            
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(review["TestDateText"], "%m/%d/%Y", ["en"])
                                    

        yield product


        
                            
        yield review
        
