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


class Darkzero_co_ukSpider(AlaSpider):
    name = 'darkzero_co_uk'
    allowed_domains = ['darkzero.co.uk']
    start_urls = ['http://darkzero.co.uk/game-reviews/']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        urls_xpath = "//div[@class='header']/a/@href"
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
        url_xpath = "//ul[@class='pager']/li[@class='next']/a/@href"
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
                
                
                "ProductName":"//h1[@class='title']/text()",
                
                
                "OriginalCategoryName":"//p[starts-with(text(),'Genre:')]/span//text()",
                
                
                "PicURL":"//div[@class='header']/img/@src",
                
                
                "ProductManufacturer":"//p[starts-with(text(),'Publisher:')]/span//text()"
                
                            }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['TestUrl'] = original_url
        picurl = product.get("PicURL", "")
        if picurl and picurl[:2] == "//":
            product["PicURL"] = "https:" + product["PicURL"]
        if picurl and picurl[:1] == "/":
            product["PicURL"] = get_full_url(original_url, picurl)
        manuf = product.get("ProductManufacturer", "")
        if manuf == "" and "//p[starts-with(text(),'Publisher:')]/span//text()"[:2] != "//":
            product["ProductManufacturer"] = "//p[starts-with(text(),'Publisher:')]/span//text()"
        try:
            product["OriginalCategoryName"] = category['category_path']
        except:
            pass
        ocn = product.get("OriginalCategoryName", "")
        if ocn == "" and "//p[starts-with(text(),'Genre:')]/span//text()"[:2] != "//":
            product["OriginalCategoryName"] = "//p[starts-with(text(),'Genre:')]/span//text()"
        review_xpaths = { 
                
                
                "ProductName":"//h1[@class='title']/text()",
                
                
                "SourceTestRating":"//img[contains(@src,'scores')]/@src",
                
                
                "TestDateText":"//time[@datetime]//text()",
                
                
                
                
                "TestSummary":"//div[@itemprop='reviewBody']/p[string-length(.//text())>2][1]//text()",
                
                
                "TestVerdict":"//div[@itemprop='reviewBody']/p[string-length(.//text())>2][last()]//text()",
                
                
                "Author":"//a[@rel='author']//text()",
                
                
                "TestTitle":"//h1[@class='title']//text()",
                
                
                
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

        if review["TestDateText"]:
            
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(review["TestDateText"], "%B %d %Y", ["en"])
                                    

        matches = None
        field_value = review.get("SourceTestRating", "")
        if field_value:
            matches = re.search("((?<=scores/).*(?=.png))", field_value, re.IGNORECASE)
        if matches:
            review["SourceTestRating"] = matches.group(1)
                                    

        review["SourceTestScale"] = "10"
                                    

        yield product


        review["DBaseCategoryName"] = "PRO"
                                    

        
                            
        yield review
        
