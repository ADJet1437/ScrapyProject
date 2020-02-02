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


class Avforums_enSpider(AlaSpider):
    name = 'avforums_en'
    allowed_domains = ['avforums.com']
    start_urls = ['https://www.avforums.com/reviews']

    
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
                    selector = browser.click_link("//li[@class='navigation']//a[*[contains(text(),'More')]]", wait_for)
                    response = selector.response
                except:
                    break
        urls_xpath = "//div[@class='jscroll-inner']//a[img]/@href"
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
        
        category_leaf_xpath = "//span[last()-1]/a/span[@itemprop='title']/text()"
        category_path_xpath = "//div[@class='breadBoxTop']//fieldset//span[@class='crust']/a/span/text()"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
                
                
                "ProductName":"//h1/text()",
                
                
                
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
        if ocn == "" and ""[:2] != "//":
            product["OriginalCategoryName"] = ""

        matches = None
        field_value = product.get("ProductName", "")
        if field_value:
            matches = re.search("(.*)Review", field_value, re.IGNORECASE)
        if matches:
            product["ProductName"] = matches.group(1)
                                    
        review_xpaths = { 
                
                
                "ProductName":"//h1/text()",
                
                
                "SourceTestRating":"//span[@class='score']/text()",
                
                
                "TestDateText":"//span/span[@class='DateTime']/text() | //span[@class='reviewDate']/*/@data-datestring",
                
                
                "TestPros":"//p[contains(text(),'Pros') or contains(text(),'Good')]/following-sibling::ul[1]/li/span/text()",
                
                
                "TestCons":"//p[contains(text(),'Cons') or contains(text(),'Bad')]/following-sibling::ul[1]/li/span/text()",
                
                
                "TestSummary":"//meta[@property='og:description']/@content",
                
                
                "TestVerdict":"//div[h2[contains(text(),'Conclusion')]]//div[contains(@class,'blockLayer')]/text() | //div[h2[contains(text(),'Verdict')]]//div[contains(@class,'blockLayer')]//text()",
                
                
                "Author":"//span[@class='reviewer']/text()",
                
                
                "TestTitle":"//h1/text()",
                
                
                
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
                                    

        review["SourceTestScale"] = "10"
                                    

        if review["TestDateText"]:
            
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(review["TestDateText"], "%b %d, %Y", ["en"])
                                    

        yield product


        
                            
        yield review
        
