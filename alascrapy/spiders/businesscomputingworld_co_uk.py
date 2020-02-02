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


class Businesscomputingworld_co_ukSpider(AlaSpider):
    name = 'businesscomputingworld_co_uk'
    allowed_domains = ['businesscomputingworld.co.uk']
    start_urls = ['http://www.businesscomputingworld.co.uk/category/reviews/']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        urls_xpath = "//div[contains(@class,'masonry-grid-latest')]//div[@class='inner']/div[@class='post-categories']/following-sibling::a[1]/@href"
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
        url_xpath = "//nav[@id='post-nav']//*[contains(text(),'Older')]/../@href"
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
                
                
                
                "OriginalCategoryName":"'businesscomputingworld.co.uk'",
                
                
                "PicURL":"(//div[@class='entry-content']/p[img or */img][1]//img/@src | //div[@class='entry-content']//li[img or */img][1]//img/@src)[1]",
                
                
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
        if ocn == "" and "'businesscomputingworld.co.uk'"[:2] != "//":
            product["OriginalCategoryName"] = "'businesscomputingworld.co.uk'"
        review_xpaths = { 
                
                
                
                "SourceTestRating":"//div[@class='review-rating']/img/@src",
                
                
                "TestDateText":"//span[@class='entry-date']//text()",
                
                
                
                
                "TestSummary":"(//h2[contains(text(),'Summary') or *[contains(text(),'Summary')]]/following::p[string-length(text())>5][1] | //div[@class='entry-content']/p[.//text()][1])[(position()>count(//h2[contains(text(),'Summary') or *[contains(text(),'Summary')]]/following::p[string-length(text())>5][1]) and count(//h2[contains(text(),'Summary') or *[contains(text(),'Summary')]])>0) or (count(//h2[contains(text(),'Summary') or *[contains(text(),'Summary')]])=0)]//text() | //div[@class='entry-content']//h3/text()",
                
                
                
                "Author":"//span[contains(@class,'author')]/a//text()",
                
                
                "TestTitle":"//div[@class='page-heading']//h1//text()",
                
                
                
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
            
            review["ProductName"] = review["ProductName"].replace("REVIEW:".lower(), "")
            
            review["ProductName"] = review["ProductName"].strip("-: ")
            product["ProductName"] = review["ProductName"]

        if review["TestDateText"]:
            
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(review["TestDateText"], "%d/%B/%Y", ["en"])
                                    

        matches = None
        field_value = review.get("SourceTestRating", "")
        if field_value:
            matches = re.search("((?<=rating-).+(?=.png))", field_value, re.IGNORECASE)
        if matches:
            review["SourceTestRating"] = matches.group(1)
                                    

        review["SourceTestScale"] = "5"
                                    

        yield product


        review["DBaseCategoryName"] = "PRO"
                                    

        
                            
        yield review
        
