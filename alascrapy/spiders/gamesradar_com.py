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


class Gamesradar_comSpider(AlaSpider):
    name = 'gamesradar_com'
    allowed_domains = ['gamesradar.com']
    start_urls = ['http://www.gamesradar.com/all-platforms/reviews/']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        url_xpath = "//div[@class='pagination-top']//span[contains(@class,'next')]/a/@href"
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
        urls_xpath = "//div[starts-with(@class,'listingResult')]/a[not(contains(@class,'category'))]/@href"
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
        
        product_xpaths = { 
                
                
                "ProductName":"//*[@itemprop='itemReviewed']//text()",
                
                
                "OriginalCategoryName":"string(normalize-space(concat(//td[text()='Platform']/following-sibling::td[not(//p/em[contains(.,'review')])],' ','Games',substring-before(substring-after(//p/em[contains(.,'review')],'reviewed'),'.'))))",
                
                
                "PicURL":"//meta[@property='og:image']/@content",
                
                
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
        if ocn == "" and "string(normalize-space(concat(//td[text()='Platform']/following-sibling::td[not(//p/em[contains(.,'review')])],' ','Games',substring-before(substring-after(//p/em[contains(.,'review')],'reviewed'),'.'))))"[:2] != "//":
            product["OriginalCategoryName"] = "string(normalize-space(concat(//td[text()='Platform']/following-sibling::td[not(//p/em[contains(.,'review')])],' ','Games',substring-before(substring-after(//p/em[contains(.,'review')],'reviewed'),'.'))))"
        review_xpaths = { 
                
                
                "ProductName":"//*[@itemprop='itemReviewed']//text()",
                
                
                "SourceTestRating":"//meta[@itemprop='ratingValue']/@content",
                
                
                "TestDateText":"//time[@itemprop='datePublished']/@datetime",
                
                
                "TestPros":"//*[normalize-space()='Pros']/following-sibling::*/descendant-or-self::*[normalize-space()]//text()",
                
                
                "TestCons":"//*[normalize-space()='Cons']/following-sibling::*/descendant-or-self::*[normalize-space()]//text()",
                
                
                "TestSummary":"//meta[@name='description']/@content",
                
                
                "TestVerdict":"//p[contains(@class,'verdict')]//text()",
                
                
                "Author":"//a[@itemprop='author']//text()",
                
                
                "TestTitle":"//h1[starts-with(@class,'review-title')]//text()",
                
                
                
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
        if review and review['TestTitle']:
            title = review["TestTitle"].lower()
            if ":" in title:
                all_title_parts = title.split(":")
                for part in all_title_parts:
                    review["ProductName"] = part.replace("review", "") if 'review' in part else title.replace("review", "")
            else:
                review["ProductName"] = title.replace("review", "")
            
            review["ProductName"] = review["ProductName"].strip("-: ")
            product["ProductName"] = review["ProductName"]

        review["DBaseCategoryName"] = "PRO"
                                    

        review["SourceTestScale"] = "5"
                                    

        matches = None
        field_value = review.get("TestDateText", "")
        if field_value:
            matches = re.search("(\d.*(?=T))", field_value, re.IGNORECASE)
        if matches:
            review["TestDateText"] = matches.group(1)
                                    

        yield product


        
                            
        yield review
        
