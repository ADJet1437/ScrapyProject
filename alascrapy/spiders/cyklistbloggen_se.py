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


class Cyklistbloggen_seSpider(AlaSpider):
    name = 'cyklistbloggen_se'
    allowed_domains = ['cyklistbloggen.se']
    start_urls = ['http://www.cyklistbloggen.se/category/recension/','http://www.cyklistbloggen.se/category/test-2/']

    
    def parse(self, response):
                                     
        original_url = response.url
        product = response.meta.get("product", {})
        review = response.meta.get("review", {})
        
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
            try:
                request.meta["product"] = product
            except:
                pass
            try:
                request.meta["review"] = review
            except:
                pass
            yield request
        urls_xpath = "//h2/a/@href"
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
                
                
                "OriginalCategoryName":"//p//a[./preceding-sibling::text()[contains(.,'Kategorier:')]][contains(@href,'tag') or contains(@href,'category')]//text()",
                
                
                "PicURL":"//head/meta[@property='og:image'][1]/@content",
                
                
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
        if ocn == "" and "//p//a[./preceding-sibling::text()[contains(.,'Kategorier:')]][contains(@href,'tag') or contains(@href,'category')]//text()"[:2] != "//":
            product["OriginalCategoryName"] = "//p//a[./preceding-sibling::text()[contains(.,'Kategorier:')]][contains(@href,'tag') or contains(@href,'category')]//text()"
        review_xpaths = { 
                
                "source_internal_id": "substring-after(//link[@rel='shortlink']/@href,'p=')",
                
                
                "ProductName":"//h1//text()",
                
                
                
                "TestDateText":"substring-before(//head/meta[@property='article:published_time'][1]/@content,'T')",
                
                
                
                
                "TestSummary":"normalize-space(//div[contains(@class,'entry-content')]/descendant-or-self::p[string-length(normalize-space())>1][1])",
                
                
                
                "Author":"//div[@class='author-description']//a//text()",
                
                
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
                                    

        yield product


        
                            
        yield review
        
