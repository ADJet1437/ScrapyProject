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


class Sotovik_ruSpider(AlaSpider):
    name = 'sotovik_ru'
    allowed_domains = ['sotovik.ru']
    start_urls = ['http://www.sotovik.ru/catalog/reviews/']

    
    def parse(self, response):
                                     
        original_url = response.url
        product = response.meta.get("product", {})
        review = response.meta.get("review", {})
        
        url_xpath = u"//ul[@class='pagination']/li[@class='active']/following-sibling::li[1]//a/@href"
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
        urls_xpath = u"//div[contains(@class,'list')]//h4/a/@href"
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
        
        category_leaf_xpath = u"//ol[@class='breadcrumb']/li[position()=last()-1]//text()"
        category_path_xpath = u"//ol[@class='breadcrumb']/li[position()<last()]//text()"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
                
                "source_internal_id": u"normalize-space(substring-after(substring-before(//*[contains(./text(),'newsID')],';'),'='))",
                
                
                "ProductName":u"//h1//text()",
                
                
                "OriginalCategoryName":u"//ol[@class='breadcrumb']/li[position()<last()]//text()",
                
                
                "PicURL":u"//div[@class='article__content']/descendant-or-self::img[1]/@src",
                
                
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
        if ocn == "" and u"//ol[@class='breadcrumb']/li[position()<last()]//text()"[:2] != "//":
            product["OriginalCategoryName"] = u"//ol[@class='breadcrumb']/li[position()<last()]//text()"
        review_xpaths = { 
                
                "source_internal_id": u"normalize-space(substring-after(substring-before(//*[contains(./text(),'newsID')],';'),'='))",
                
                
                "ProductName":u"//h1//text()",
                
                
                
                "TestDateText":u"substring-before(//div[contains(@class,'header')]//time/@datetime,'T')",
                
                
                
                
                "TestSummary":u"(//article/p[1]//text() | //meta[@name='description']/@content)[last()]",
                
                
                "TestVerdict":u"normalize-space(//h2[contains(.,'Выводы') or contains(.,'выводы') or contains(.,'Итоги')]/following-sibling::p[string-length(normalize-space())>1][1])",
                
                
                "Author":u"//div[@class='sub-header']//span[contains(.,'Автор') and normalize-space(substring-after(.,':'))]//text() | //div[@class='sub-header']//span[contains(.,'Автор') and not(normalize-space(substring-after(.,':')))]/preceding-sibling::span[1]//a//text()",
                
                
                "TestTitle":u"//h1//text()",
                
                
                
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
            matches = re.search("((?<=\:\s).*)", field_value, re.IGNORECASE)
        if matches:
            review["Author"] = matches.group(1)
                                    

        yield product


        
                            
        yield review
        
