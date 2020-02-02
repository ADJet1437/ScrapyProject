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


class Notebookinfo_deSpider(AlaSpider):
    name = 'notebookinfo_de'
    allowed_domains = ['notebookinfo.de']
    start_urls = ['http://www.notebookinfo.de/tests/']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        url_xpath = "//ul[contains(@class,'pagination')]/li[contains(@class,'next')]/a/@href"
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
        urls_xpath = "//article//h3/a/@href"
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
    
    def level_2(self, response):
                                     
        original_url = response.url
        
        category_leaf_xpath = "//ol[./@*[contains(.,'crumb')]]//li[last()-1]//span//text()"
        category_path_xpath = "//ol[./@*[contains(.,'crumb')]]//li[position()<last()]//span//text()"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
                
                "source_internal_id": "//input[@name='id']/@value",
                
                
                "ProductName":"//h1//text()",
                
                
                "OriginalCategoryName":"//ol[./@*[contains(.,'crumb')]]//li[position()<last()]//span//text()",
                
                
                "PicURL":"//meta[@property='og:image']/@content | //article[not(normalize-space(//meta[@property='og:image']/@content))]/descendant-or-self::img[1]/@src",
                
                
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
        if ocn == "" and "//ol[./@*[contains(.,'crumb')]]//li[position()<last()]//span//text()"[:2] != "//":
            product["OriginalCategoryName"] = "//ol[./@*[contains(.,'crumb')]]//li[position()<last()]//span//text()"
        review_xpaths = { 
                
                "source_internal_id": "//input[@name='id']/@value",
                
                
                "ProductName":"//h1//text()",
                
                
                "SourceTestRating":"string((5 - number(translate(//span[@itemprop='reviewRating']/meta[@itemprop='ratingValue']/@content,',','.'))) * 1.25)",
                
                
                "TestDateText":"substring-before(//time[@itemprop='datePublished']/@datetime,'T')",
                
                
                
                
                "TestSummary":"//p[@itemprop='description']//text() | //article[@itemprop='reviewBody' and not(normalize-space(//p[@itemprop='description']))]/p[string-length(normalize-space(./text()))>1][1]//text()",
                
                
                "TestVerdict":"//h2[contains(.,'Fazit') or @*=Fazit]/following-sibling::p[string-length(normalize-space())>1][1]//text()",
                
                
                "Author":"//span[@itemprop='author']//a//text()",
                
                
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
                                    

        review["SourceTestScale"] = "5"
                                    

        yield product


        
                            
        yield review
        
