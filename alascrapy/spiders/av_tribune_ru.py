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


class Av_tribune_ruSpider(AlaSpider):
    name = 'av_tribune_ru'
    allowed_domains = ['av-tribune.ru']
    start_urls = ['http://www.av-tribune.ru/test-equipment.html']

    
    def parse(self, response):
                                     
        original_url = response.url
        product = response.meta.get("product", {})
        review = response.meta.get("review", {})
        
        url_xpath = u"//div[@class='pagination']//li[@class='pagination-next']/a/@href"
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
        urls_xpath = u"//div[@class='page-header']/h2/a/@href"
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
        
        category_leaf_xpath = u"//ul[@class='breadcrumb']/li[.//a][last()]//a//text()"
        category_path_xpath = u"//ul[@class='breadcrumb']/li[.//a]//a//text()"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
                
                "source_internal_id": u"//base/@href",
                
                
                "ProductName":u"//title//text()",
                
                
                "OriginalCategoryName":u"//ul[@class='breadcrumb']/li[.//a]//a//text()",
                
                
                "PicURL":u"//div[@itemprop='articleBody']/descendant-or-self::img[1]/@src",
                
                
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
        if ocn == "" and u"//ul[@class='breadcrumb']/li[.//a]//a//text()"[:2] != "//":
            product["OriginalCategoryName"] = u"//ul[@class='breadcrumb']/li[.//a]//a//text()"
        review_xpaths = { 
                
                "source_internal_id": u"//base/@href",
                
                
                "ProductName":u"//title//text()",
                
                
                
                "TestDateText":u"substring-before(//time[@itemprop='datePublished']/@datetime,'T')",
                
                
                
                
                "TestSummary":u"//div[@itemprop='articleBody']/descendant-or-self::p[string-length(normalize-space())>1 and (normalize-space(.//strong/../text()) or normalize-space(.//strong/../*[not(name()='strong')]) or not(.//strong)) and (contains(.,'.') or contains(.,'?') or contains(.,'!'))][./preceding-sibling::p[string-length(normalize-space())>1][1][starts-with(normalize-space(),'Вступление')] or not(../p[starts-with(normalize-space(),'Вступление')])][1]//text() | //div[@itemprop='articleBody']/div[string-length(normalize-space())>1 and (normalize-space(.//strong/../text()) or normalize-space(.//strong/../*[not(name()='strong')]) or not(.//strong)) and (contains(.,'.') or contains(.,'?') or contains(.,'!'))][./preceding-sibling::div[string-length(normalize-space())>1][1][starts-with(normalize-space(),'Вступление')] or not(../div[starts-with(normalize-space(),'Вступление')])][1]//text()",
                
                
                "TestVerdict":u"normalize-space(//div[@itemprop='articleBody']/descendant-or-self::p[starts-with(translate(.,' ',''),'Подводимитог')]/following-sibling::p[string-length(normalize-space())>1][1])",
                
                
                "Author":u"//div[@itemprop='articleBody']/descendant-or-self::p[starts-with(normalize-space(),'Автор')]//text() | //base[not(//div[@itemprop='articleBody']/descendant-or-self::p[starts-with(normalize-space(),'Автор')])]/@href",
                
                
                "TestTitle":u"//title//text()",
                
                
                
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
        field_value = product.get("source_internal_id", "")
        if field_value:
            matches = re.search("((?<=\/)\d+(?=\-))", field_value, re.IGNORECASE)
        if matches:
            product["source_internal_id"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("source_internal_id", "")
        if field_value:
            matches = re.search("((?<=\/)\d+(?=\-))", field_value, re.IGNORECASE)
        if matches:
            review["source_internal_id"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("Author", "")
        if field_value:
            matches = re.search("((?<=\:\s).*(?=\.))", field_value, re.IGNORECASE)
        if matches:
            review["Author"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("Author", "")
        if field_value:
            matches = re.search("((?<=\:\s).*)", field_value, re.IGNORECASE)
        if matches:
            review["Author"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("Author", "")
        if field_value:
            matches = re.search("((?<=www\.)(\w|\.|\-)*(?=\/))", field_value, re.IGNORECASE)
        if matches:
            review["Author"] = matches.group(1)
                                    

        yield product


        
                            
        yield review
        
