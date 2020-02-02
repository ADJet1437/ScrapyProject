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


class Therunningpitt_comSpider(AlaSpider):
    name = 'therunningpitt_com'
    allowed_domains = ['therunningpitt.com']
    start_urls = ['http://therunningpitt.com/category/recensioni']

    
    def parse(self, response):
                                     
        original_url = response.url
        product = response.meta.get("product", {})
        review = response.meta.get("review", {})
        
        url_xpath = u"//div[@class='pagination']//a[contains(.,'Next')]/@href"
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
        urls_xpath = u"//h3/a/@href"
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
                
                "source_internal_id": u"substring-after(//link[@rel='shortlink']/@href,'p=')",
                
                
                "ProductName":u"//div[@class='inner_wrapper']/descendant-or-self::*[contains(name(),'h')][1]//text()[normalize-space()]",
                
                
                "OriginalCategoryName":u"//meta[@property='article:section']/@content",
                
                
                "PicURL":u"//meta[@property='og:image']/@content",
                
                
                            }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['TestUrl'] = original_url
        picurl = product.get("PicURL", "")
        if picurl and picurl[:2] == "//":
            product["PicURL"] = "https:" + product["PicURL"]
        if picurl and picurl[:1] == "/":
            product["PicURL"] = get_full_url(original_url, picurl)
        manuf = product.get("ProductManufacturer", "")
        if manuf == "" and u""[:2] != "//":
            product["ProductManufacturer"] = u""
        try:
            product["OriginalCategoryName"] = category['category_path']
        except:
            pass
        ocn = product.get("OriginalCategoryName", "")
        if ocn == "" and u"//meta[@property='article:section']/@content"[:2] != "//":
            product["OriginalCategoryName"] = u"//meta[@property='article:section']/@content"
        review_xpaths = { 
                
                "source_internal_id": u"substring-after(//link[@rel='shortlink']/@href,'p=')",
                
                
                "ProductName":u"//div[@class='inner_wrapper']/descendant-or-self::*[contains(name(),'h')][1]//text()[normalize-space()]",
                
                
                
                "TestDateText":u"substring-before(//meta[@property='article:published_time']/@content,'T')",
                
                
                
                
                "TestSummary":u"//meta[@property='og:description']/@content",
                
                
                "TestVerdict":u"//div[@class='post_inner_wrapper']/descendant-or-self::p[.//strong[contains(.,'onclusi')]][1]/text()",
                
                
                "Author":u"//div[@class='post_detail']//text()[./preceding-sibling::*[contains(@src,'author')]]",
                
                
                "TestTitle":u"//div[@class='inner_wrapper']/descendant-or-self::*[contains(name(),'h')][1]//text()[normalize-space()]",
                
                
                
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
                                    

        matches = None
        field_value = review.get("Author", "")
        if field_value:
            matches = re.search("((?<=Scritto\sda).*)", field_value, re.IGNORECASE)
        if matches:
            review["Author"] = matches.group(1)
                                    

        yield product


        
                            
        yield review
        
