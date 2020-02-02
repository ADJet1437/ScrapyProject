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


class Digitalspy_comSpider(AlaSpider):
    name = 'digitalspy_com'
    allowed_domains = ['digitalspy.com']
    start_urls = ['http://www.digitalspy.com/tech/review/']

    
    def parse(self, response):
                                     
        original_url = response.url
        product = response.meta.get("product", {})
        review = response.meta.get("review", {})
        

        with SeleniumBrowser(self, response) as browser:
        
            wait_for = None
            wait_type, wait_for_xpath = "wait_none", ""
            if wait_for_xpath :
                wait_for = EC.wait_none((By.XPATH, wait_for_xpath))
            browser.get(response.url)
            selector = browser.scroll_until_the_end(2000, wait_for)
            response = selector.response
        urls_xpath = "//div[@class='landing-feed--special-content']/a/@href"
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
                
                "source_internal_id": "//link[@rel='canonical']/@href",
                
                
                "ProductName":"//div[@class='content-header--info']/h1/text()",
                
                
                
                "PicURL":"//div[@class='embedded-image--lead-inner']/img/@src",
                
                
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
        if ocn == "" and ""[:2] != "//":
            product["OriginalCategoryName"] = ""
        review_xpaths = { 
                
                "source_internal_id": "//link[@rel='canonical']/@href",
                
                
                "ProductName":"//div[@class='content-header--info']/h1/text()",
                
                
                "SourceTestRating":"count(//span[@class='star-rating icon icon-rating'])+count(//span[@class='star-rating icon icon-rating-half'])*0.5",
                
                
                "TestDateText":"//div[@class='social-byline--pub-info']//time[@itemprop='datePublished']/text()[normalize-space()]",
                
                
                "TestPros":"//p[contains(.,'The Good')]/following::ul[1]|//p[contains(.,'THE GOOD')]/following::ul[1]//text()",
                
                
                "TestCons":"//p[contains(.,'The Bad')]/following::ul[1]|//p[contains(.,'THE BAD')]/following::ul[1]//text()",
                
                
                "TestSummary":"//h2[@itemprop='alternativeHeadline']/p/text()",
                
                
                "TestVerdict":"//p[contains(.,'Verdict')]/following::p[normalize-space()][string-length(.)>2][1]|//h4[contains(.,'VERDICT')]/following::p[normalize-space()][string-length(.)>2][1]|//p[contains(.,'VERDICT')]/following::p[normalize-space()][string-length(.)>2][1]",
                
                
                "Author":"//div[@class='social-byline--pub-info']//span[@itemprop='name']/text()",
                
                
                "TestTitle":"//div[@class='content-header--info']/h1/text()",
                
                
                
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

        review["SourceTestScale"] = "5"
                                    

        matches = None
        field_value = product.get("source_internal_id", "")
        if field_value:
            matches = re.search("(?<=review\/a)(\d+)", field_value, re.IGNORECASE)
        if matches:
            product["source_internal_id"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("source_internal_id", "")
        if field_value:
            matches = re.search("(?<=review\/a)(\d+)", field_value, re.IGNORECASE)
        if matches:
            review["source_internal_id"] = matches.group(1)
                                    

        matches = None
        field_value = product.get("ProductName", "")
        if field_value:
            matches = re.search("([\w\-\s\.]+)(?=\sreview)", field_value, re.IGNORECASE)
        if matches:
            product["ProductName"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("ProductName", "")
        if field_value:
            matches = re.search("([\w\-\s\.]+)(?=\sreview)", field_value, re.IGNORECASE)
        if matches:
            review["ProductName"] = matches.group(1)
                                    

        if review["TestDateText"]:
            
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(review["TestDateText"], "%d %B %Y", ["en"])
                                    

        review["DBaseCategoryName"] = "PRO"
                                    

        yield product


        
                            
        yield review
        
