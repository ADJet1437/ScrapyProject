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


class Diisign_comSpider(AlaSpider):
    name = 'diisign_com'
    allowed_domains = ['diisign.com']
    start_urls = ['http://www.diisign.com/category/test/']

    
    def parse(self, response):
                                     
        original_url = response.url
        product = response.meta.get("product", {})
        review = response.meta.get("review", {})
        
        url_xpath = u"//div[contains(@class,'pagination')]//div[contains(@class,'left')]//a/@href"
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
        urls_xpath = u"//article//h2/a[contains(@href,'test')]/@href"
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
                
                "source_internal_id": u"substring-after(//article/@id,'post-')",
                
                
                "ProductName":u"//h1//text()",
                
                
                "OriginalCategoryName":u"//p[@class='post-meta']//a[contains(@rel,'category')]//text()",
                
                
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
        if ocn == "" and u"//p[@class='post-meta']//a[contains(@rel,'category')]//text()"[:2] != "//":
            product["OriginalCategoryName"] = u"//p[@class='post-meta']//a[contains(@rel,'category')]//text()"
        review_xpaths = { 
                
                "source_internal_id": u"substring-after(//article/@id,'post-')",
                
                
                "ProductName":u"//h1//text()",
                
                
                
                "TestDateText":u"normalize-space(//p[@class='post-meta'])",
                
                
                "TestPros":u"//p[contains(translate(.,' ',''),'Les+')]/text()[./preceding::text()[contains(translate(.,' ',''),'Les+')]]",
                
                
                "TestCons":u"//p[contains(translate(.,' ',''),'Les–')]/text()[./preceding::text()[contains(translate(.,' ',''),'Les–')]]",
                
                
                "TestSummary":u"//div[@class='entry-content']/p[string-length(normalize-space())>1 and ./text()[contains(translate(.,',?!','.'),'.')]][1]//text()[normalize-space() and (name(..)='p' or name(..)='a')][not(./preceding-sibling::br/preceding-sibling::text()[normalize-space()] or (../preceding-sibling::br/preceding-sibling::text()[normalize-space()] and name(..)='a'))]",
                
                
                "TestVerdict":u"//div[@class='entry-content']/p[./*[contains(.,'onclusion')]][last()]/text()[normalize-space() and ./preceding::text()[contains(.,'onclusion')]][1]",
                
                
                "Author":u"//p[@class='post-meta']//a[contains(@rel,'author')]//text()",
                
                
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
        field_value = review.get("TestDateText", "")
        if field_value:
            matches = re.search("(\d+\s\d+\s\d{4})", field_value, re.IGNORECASE)
        if matches:
            review["TestDateText"] = matches.group(1)
                                    

        if review["TestDateText"]:
            
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(review["TestDateText"], "%d %m %Y", ["fr"])
                                    

        yield product


        
                            
        yield review
        
