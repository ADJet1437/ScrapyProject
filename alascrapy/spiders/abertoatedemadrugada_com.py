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


class Abertoatedemadrugada_comSpider(AlaSpider):
    name = 'abertoatedemadrugada_com'
    allowed_domains = ['abertoatedemadrugada.com']
    start_urls = ['http://abertoatedemadrugada.com/search/label/An%C3%A1lises']

    
    def parse(self, response):
                                     
        original_url = response.url
        product = response.meta.get("product", {})
        review = response.meta.get("review", {})
        
        url_xpath = u"//div[@class='blog-pager']//a[contains(@class,'older')]/@href"
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
        urls_xpath = u"//div[contains(@class,'blog-posts')]//h3/a/@href"
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
                
                
                "ProductName":u"//meta[@property='og:title'][1]/@content",
                
                
                "OriginalCategoryName":u"//span[@class='post-labels']//a//text()",
                
                
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
        if ocn == "" and u"//span[@class='post-labels']//a//text()"[:2] != "//":
            product["OriginalCategoryName"] = u"//span[@class='post-labels']//a//text()"
        review_xpaths = { 
                
                
                "ProductName":u"//meta[@property='og:title'][1]/@content",
                
                
                "SourceTestRating":u"substring-before(substring-after(//div[contains(@class,'entry-content')]//div[.//img[contains(./@src,'_badge')]]//img/@src,'_badge'),'.')",
                
                
                "TestDateText":u"substring-before(//*[@class='published']/@title,'T')",
                
                
                "TestPros":u"//ul[./preceding-sibling::*[normalize-space()][1][normalize-space()='Prós' or normalize-space()='Prós:' or normalize-space()='Pros' or normalize-space()='Pros:']]/li//text()",
                
                
                "TestCons":u"//ul[./preceding-sibling::*[normalize-space()][1][normalize-space()='Contras' or normalize-space()='Contras:' or normalize-space()='Contra' or normalize-space()='Contra:']]/li//text()",
                
                
                "TestSummary":u"//meta[@property='og:description']/@content",
                
                
                "TestVerdict":u"//div[contains(@class,'entry-content')]/*[name()='h3' or name()='b'][contains(.,'final') or contains(.,'Final') or contains(.,'finais') or contains(.,'Finais')]/following-sibling::text()[string-length(normalize-space())>1 and not(./preceding-sibling::br[1]/preceding-sibling::text()[string-length(normalize-space())>1]/preceding-sibling::*[name()='h3' or name()='b'][contains(.,'final') or contains(.,'Final') or contains(.,'finais') or contains(.,'Finais')])]",
                
                
                "Author":u"//span[contains(@class,'post-author')]//span//text()",
                
                
                "TestTitle":u"//meta[@property='og:title'][1]/@content",
                
                
                "award":u"//div[contains(@class,'entry-content')]//div[.//img[contains(./@src,'_badge')]]/following-sibling::*[string-length(normalize-space())>1][1]//text()",
                
                
                "AwardPic":u"//div[contains(@class,'entry-content')]//div[.//img[contains(./@src,'_badge')]]//img[contains(./@src,'_badge')]/@src"
                
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
                                    

        yield product


        
                            
        yield review
        
