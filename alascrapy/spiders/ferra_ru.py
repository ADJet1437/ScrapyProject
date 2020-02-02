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


class Ferra_ruSpider(AlaSpider):
    name = 'ferra_ru'
    allowed_domains = ['ferra.ru']
    start_urls = ['http://www.ferra.ru/ru/all/review/']

    
    def parse(self, response):
                                     
        original_url = response.url
        product = response.meta.get("product", {})
        review = response.meta.get("review", {})
        
        url_xpath = "//span[@class='bpr_next']/a/@href"
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
        urls_xpath = "//div[@class='doclist_rating']/parent::div/parent::a/@href"
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
        
        category_leaf_xpath = "(//ul[@class='b-way']/li[2]//text())[last()-1]"
        category_path_xpath = "//ul[@class='b-way']/li[2]//text()"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
                
                
                "ProductName":"//div[@class='post']/h1//text()",
                
                
                "OriginalCategoryName":"//ul[@class='b-way']/li[2]//text()",
                
                
                
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
        if ocn == "" and "//ul[@class='b-way']/li[2]//text()"[:2] != "//":
            product["OriginalCategoryName"] = "//ul[@class='b-way']/li[2]//text()"
        review_xpaths = { 
                
                
                "ProductName":"//div[@class='post']/h1//text()",
                
                
                "SourceTestRating":"//div[@class='ratinglabel']//text()",
                
                
                "TestDateText":"//span[@class='date']/time[@itemprop='dtreviewed']/@datetime",
                
                
                "TestPros":"(//td[@valign='top']/ul)[1]//text()[normalize-space()]|//td[@valign='top'][last()]/following::td[1]//li//text()",
                
                
                "TestCons":"(//td[@valign='top']/ul)[2]//text()[normalize-space()]|//td[@valign='top'][last()]/following::td[2]//li//text()",
                
                
                "TestSummary":"//div[@itemprop='summary']//text()[normalize-space()]",
                
                
                
                "Author":"//div[@class='post']//span[@itemprop='reviewer']//text()",
                
                
                "TestTitle":"//div[@class='post']/h1//text()",
                
                
                "award":"(//img[contains(@src,'580x3000')])[last()]/@alt",
                
                
                "AwardPic":"(//img[contains(@src,'580x3000')])[last()]/@src"
                
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
            matches = re.search("([\d\.\s]+)(?=из)".decode('utf-8'), field_value, re.IGNORECASE)
        if matches:
            review["SourceTestRating"] = matches.group(1)
                                    

        review["SourceTestScale"] = "10"
                                    

        review["DBaseCategoryName"] = "PRO"
                                    

        yield product


        
                            
        yield review
        
