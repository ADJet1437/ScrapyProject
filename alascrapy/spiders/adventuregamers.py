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


class AdventuregamersSpider(AlaSpider):
    name = 'adventuregamers'
    allowed_domains = ['adventuregamers.com']
    start_urls = ['http://www.adventuregamers.com/articles/reviews']

    
    def parse(self, response):
                                     
        original_url = response.url
        product = response.meta.get("product", {})
        review = response.meta.get("review", {})
        
        url_xpath = "//div[@class='pagination_big']//a[contains(.,'Last')]/preceding-sibling::a[1]/@href"
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
        urls_xpath = "//div[@class='article_right']//a/@href"
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
                
                "source_internal_id": "//div[@id='middle']/img/@src",
                
                
                "ProductName":"(//div[@class='cleft_inn']//h2[@class='page_title']//text())[1]",
                
                
                
                "PicURL":"//div[@class='item']//div[@class='game_left_short']//a//img/@src",
                
                
                "ProductManufacturer":"//div[@class='game_right_short']//p[contains(.,'Developer')]/a/text()"
                
                            }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['TestUrl'] = original_url
        picurl = product.get("PicURL", "")
        if picurl and picurl[:2] == "//":
            product["PicURL"] = "https:" + product["PicURL"]
        if picurl and picurl[:1] == "/":
            product["PicURL"] = get_full_url(original_url, picurl)
        manuf = product.get("ProductManufacturer", "")
        if manuf == "" and "//div[@class='game_right_short']//p[contains(.,'Developer')]/a/text()"[:2] != "//":
            product["ProductManufacturer"] = "//div[@class='game_right_short']//p[contains(.,'Developer')]/a/text()"
        try:
            product["OriginalCategoryName"] = category['category_path']
        except:
            pass
        ocn = product.get("OriginalCategoryName", "")
        if ocn == "" and ""[:2] != "//":
            product["OriginalCategoryName"] = ""
        review_xpaths = { 
                
                "source_internal_id": "//div[@id='middle']/img/@src",
                
                
                "ProductName":"(//div[@class='cleft_inn']//h2[@class='page_title']//text())[1]",
                
                
                "SourceTestRating":"//div[@class='review_box padding']/div/a/span/strong/text()",
                
                
                "TestDateText":"normalize-space(//div[@class='cleft_inn']//div[@class='pageheader_byline']/text()[last()])",
                
                
                "TestPros":"(//div[@class='padding']//div[contains(.,'The Good')]//text())[last()]",
                
                
                "TestCons":"(//div[@class='padding']//div[contains(.,'The Bad')]//text())[last()]",
                
                
                
                "TestVerdict":"//div[@class='review_box padding']/p//text()|(//div[@class='review_box padding']//text()[normalize-space()][string-length(.)>6])[last()]",
                
                "TestSummary":"//div[@class='bodytext']/p[1]//text()[normalize-space()]",

                "Author":"//div[@class='cleft_inn']//div[@class='pageheader_byline']//a/text()",
                
                
                "TestTitle":"(//div[@class='cleft_inn']//h2[@class='page_title']//text())[1]",
                
                
                
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
            matches = re.search("(?<=&i=)(\d+)", field_value, re.IGNORECASE)
        if matches:
            product["source_internal_id"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("source_internal_id", "")
        if field_value:
            matches = re.search("(?<=&i=)(\d+)", field_value, re.IGNORECASE)
        if matches:
            review["source_internal_id"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("TestDateText", "")
        if field_value:
            matches = re.search("(\w.*)", field_value, re.IGNORECASE)
        if matches:
            review["TestDateText"] = matches.group(1)
                                    

        if review["TestDateText"]:
            
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(review["TestDateText"], "%B %d, %Y", ["en"])
                                    

        matches = None
        field_value = review.get("SourceTestRating", "")
        if field_value:
            matches = re.search("(\w.*)(?=\sstar)", field_value, re.IGNORECASE)
        if matches:
            review["SourceTestRating"] = matches.group(1)
                                    

        review["SourceTestScale"] = "5"
                                    

        review["DBaseCategoryName"] = "PRO"
                                    

        yield product


        
                            
        yield review
        
