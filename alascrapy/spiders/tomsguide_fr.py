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


class Tomsguide_frSpider(AlaSpider):
    name = 'tomsguide_fr'
    allowed_domains = ['tomsguide.fr']
    start_urls = ['http://www.tomsguide.fr/articles/tests/']

    
    def parse(self, response):
                                     
        original_url = response.url
        product = response.meta.get("product", {})
        review = response.meta.get("review", {})
        url_xpath = "(//ul[@class='pager']//li)[last()]/a/@href"
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
            print single_url,'='*30
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
        urls_xpath = "//ul[@class='listing-items']/li/div/div[1]/a/@href"
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
        
        category_leaf_xpath = "(//ul[@class='breadcrumb']/li//text())[last()-1]"
        category_path_xpath = "//ul[@class='breadcrumb']/li//text()"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
                
                "source_internal_id": "//link[@rel='canonical']/@href",
                
                
                "ProductName":"//span[@class='sbs-header-title']//text()",
                
                
                "OriginalCategoryName":"//ul[@class='breadcrumb']/li//text()",
                
                
                
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
        if ocn == "" and "//ul[@class='breadcrumb']/li//text()"[:2] != "//":
            product["OriginalCategoryName"] = "//ul[@class='breadcrumb']/li//text()"
        review_xpaths = { 
                
                "source_internal_id": "//link[@rel='canonical']/@href",
                
                
                "ProductName":"//span[@class='sbs-header-title']//text()",
                
                
                "SourceTestRating":"//div[@class='p-u-1-3 inner10 review-bar-rating']//text()",
                
                
                "TestDateText":"//div[@class='author nolinks']//time[@itemprop='datePublished']//text()",
                
                
                "TestPros":"(//div[@class='sbs-advice-title'])[1]/following-sibling::ul/li//text()",
                
                
                "TestCons":"(//div[@class='sbs-advice-title'])[2]/following-sibling::ul/li//text()",
                
                
                
                "TestVerdict":"//span[@class='sbc-advice-text']//text()",
                
                
                "Author":"//div[@class='author nolinks']//span[@itemprop='author']//text()",
                
                
                "TestTitle":"//h1[@itemprop='headline']//text()",
                
                
                
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
            matches = re.search("(\d+)(?=\.html)", field_value, re.IGNORECASE)
        if matches:
            product["source_internal_id"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("source_internal_id", "")
        if field_value:
            matches = re.search("(\d+)(?=\.html)", field_value, re.IGNORECASE)
        if matches:
            review["source_internal_id"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("SourceTestRating", "")
        if field_value:
            matches = re.search("(\d+)(?=\/)", field_value, re.IGNORECASE)
        if matches:
            review["SourceTestRating"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("TestDateText", "")
        if field_value:
            matches = re.search("(.*)(?=\d{2}:)", field_value, re.IGNORECASE)
        if matches:
            review["TestDateText"] = matches.group(1)
                                    

        if review["TestDateText"]:
            
            review["TestDateText"] = review["TestDateText"].lower().replace('.'.lower(), "")
            
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(review["TestDateText"], "%d %B %Y", ["fr"])
                                    

        review["SourceTestScale"] = "10"
                                    

        review["DBaseCategoryName"] = "PRO"
                                    

        yield product


        
                            
        yield review
        
