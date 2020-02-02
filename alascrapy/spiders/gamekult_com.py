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


class Gamekult_comSpider(AlaSpider):
    name = 'gamekult_com'
    allowed_domains = ['gamekult.com']
    start_urls = ['http://www.gamekult.com/jeux/test-jeux-video.html']

    
    def parse(self, response):
                                     
        original_url = response.url
        product = response.meta.get("product", {})
        review = response.meta.get("review", {})
        
        url_xpath = "//div[@class='pagination pagination-centered']/ul/li[contains(.,'»')]/a/@href".decode('utf-8')
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
        urls_xpath = "//section[@id='review-list']/article//p[@class='title']/a/@href"
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
                
                "source_internal_id": "//meta[@property='og:url']/@content",
                
                
                "ProductName":"(//article[@id='story-page']//p[@class='titleh1']//span/text())[1]",
                
                
                
                
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
                
                "source_internal_id": "//meta[@property='og:url']/@content",
                
                
                "ProductName":"(//article[@id='story-page']//p[@class='titleh1']//span/text())[1]",
                
                
                "SourceTestRating":"(//meta[@itemprop='value']/@content)[1]",
                
                
                "TestDateText":"(//time[@itemprop='dtreviewed']/@datetime)[1]",
                
                
                "TestPros":"(//div[@class='story-plus']/ul)[1]/li/text()[normalize-space()]",
                
                
                "TestCons":"(//div[@class='story-moins']/ul)[1]/li/text()[normalize-space()]",
                
                
                "TestSummary":"//div[@class='summary']/p//text()[normalize-space()]",
                
                
                "TestVerdict":"//div[@class='story-conclusion']/p//text()[normalize-space()]",
                
                
                "Author":"(//span[@itemprop='reviewer']//text())[1]",
                
                
                "TestTitle":"(//article[@id='story-page']//p[@class='titleh1']//span/text())[1]",
                
                
                
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
        field_value = product.get("source_internal_id", "")
        if field_value:
            matches = re.search("(\d+)(?=t\.html)", field_value, re.IGNORECASE)
        if matches:
            product["source_internal_id"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("source_internal_id", "")
        if field_value:
            matches = re.search("(\d+)(?=t\.html)", field_value, re.IGNORECASE)
        if matches:
            review["source_internal_id"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("TestDateTest", "")
        if field_value:
            matches = re.search("(\d{4}-\d{2}-\d{2})", field_value, re.IGNORECASE)
        if matches:
            review["TestDateTest"] = matches.group(1)
                                    

        review["SourceTestScale"] = "10"
                                    

        review["DBaseCategoryName"] = "PRO"
                                    

        yield product


        
                            
        yield review
        
