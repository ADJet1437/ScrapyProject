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


class Techtree_enSpider(AlaSpider):
    name = 'techtree_en'
    allowed_domains = ['techtree.com']
    start_urls = ['http://www.techtree.com/content/reviews']

    
    def parse(self, response):
                                     
        original_url = response.url
        

        with SeleniumBrowser(self, response) as browser:
        
            wait_for = None
            wait_type, wait_for_xpath = "wait_none", ""
            if wait_for_xpath :
                wait_for = EC.wait_none((By.XPATH, wait_for_xpath))
            browser.get(response.url)
            while True:
                try:
                    urls_xpath = "//ul[@class='review-listing']//h3/a/@href"
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
                    selector = browser.click_link("//ul[contains(@class,'pager')]//a[contains(text(),'next')]", wait_for)
                    response = selector.response
                except:
                    break

    
    def level_2(self, response):
                                     
        original_url = response.url
        
        product_xpaths = { 
                
                
                "ProductName":"//meta[@property='og:title']/@content",
                
                
                "OriginalCategoryName":"techtree.com",
                
                
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
        if ocn == "" and "techtree.com"[:2] != "//":
            product["OriginalCategoryName"] = "techtree.com"
        review_xpaths = { 
                
                
                "ProductName":"//meta[@property='og:title']/@content",
                
                
                "SourceTestRating":"//span[@class='rate-star']/span[@itemprop='rating']/text()",
                
                
                "TestDateText":"//div[@class='art-txt']//time/text()",
                
                
                "TestPros":"//div[@class='pros-cont']/text()",
                
                
                "TestCons":"//div[@class='cons-cont']/text()",
                
                
                "TestSummary":"//*[@class='small-title']/text()",
                
                
                
                "Author":"//span[@itemprop='reviewer']/a/text()",
                
                
                "TestTitle":"//meta[@property='og:title']/@content",
                
                
                
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
                                    

        if review["TestDateText"]:
            
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(review["TestDateText"], "%d %b %Y", ["en"])
                                    

        yield product


        
                            
        yield review
        
