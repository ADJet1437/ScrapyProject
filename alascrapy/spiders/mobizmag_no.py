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


class Mobizmag_noSpider(AlaSpider):
    name = 'mobizmag_no'
    allowed_domains = ['mobizmag.no']
    start_urls = ['http://www.mobizmag.no/kategori/tester/']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        urls_xpath = "//h2[@class='entry-title']/a/@href"
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
        url_xpath = "//div[contains(@class,'masonry-load-more')]/a/@data-link"
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
                
                
                
                "OriginalCategoryName":"'mobizmag.no'",
                
                
                "PicURL":"//div[contains(@class,'page-header-image-single')]/img/@src",
                
                
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
        if ocn == "" and "'mobizmag.no'"[:2] != "//":
            product["OriginalCategoryName"] = "'mobizmag.no'"
        review_xpaths = { 
                
                
                
                "SourceTestRating":"(//text()[contains(.,'Rating:')][last()])[position()=last()]",
                
                
                "TestDateText":"//span[@class='posted-on']//time[@itemprop='datePublished']/@datetime",
                
                
                "TestPros":"//p[strong[contains(text(),'Positivt') or contains(text(),'Pluss')]][(count(following-sibling::ul))>=1]/following::ul[1]//li//text() | //p[strong[contains(text(),'Positivt') or contains(text(),'Pluss')]][(count(following-sibling::ul))=0]/text()",
                
                
                "TestCons":"//p[strong[contains(text(),'Negativt') or contains(text(),'Minus')]][(count(following-sibling::ul))>=1]/following::ul[1]//li//text() | //p[strong[contains(text(),'Negativt') or contains(text(),'Minus')]][(count(following-sibling::ul))=0]/text()",
                
                
                "TestSummary":"(//h1[@class='entry-title']/following::h3[text()][1] | //h1[@class='entry-title']/following::p[text()][1] | //h1[@class='entry-title']/following::h2[text()][1] | //h1[@class='entry-title']/following::h4[.//text()][1])[1]//text()",
                
                
                "TestVerdict":"//*[starts-with(.//text(),'Konklusjon')][count(//*[starts-with(.//text(),'Konklusjon')][count(node())>1])=0][count(node())=1]/following::p[string-length(.//text())>2][1]//text() | //*[starts-with(.//text(),'Konklusjon')][count(node())>1]/text()",
                
                
                "Author":"//span[@class='author-name']//text()",
                
                
                "TestTitle":"//h1[@class='entry-title']//text()",
                
                
                
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

        matches = None
        field_value = review.get("SourceTestRating", "")
        if field_value:
            matches = re.search("((?<=Rating:).*(?=/))", field_value, re.IGNORECASE)
        if matches:
            review["SourceTestRating"] = matches.group(1)
                                    

        review["SourceTestScale"] = "6"
                                    
        if review and review['TestTitle']:
            title = review["TestTitle"].lower()
            if ":" in title:
                all_title_parts = title.split(":")
                for part in all_title_parts:
                    review["ProductName"] = part.replace("review", "") if 'review' in part else title.replace("review", "")
            else:
                review["ProductName"] = title.replace("review", "")
            
            review["ProductName"] = review["ProductName"].replace("TEST:".lower(), "")
            
            review["ProductName"] = review["ProductName"].strip("-: ")
            product["ProductName"] = review["ProductName"]

        matches = None
        field_value = review.get("TestDateText", "")
        if field_value:
            matches = re.search("(\d{4}-\d{2}-\d{2})", field_value, re.IGNORECASE)
        if matches:
            review["TestDateText"] = matches.group(1)
                                    

        yield product


        review["DBaseCategoryName"] = "PRO"
                                    

        
                            
        yield review
        
