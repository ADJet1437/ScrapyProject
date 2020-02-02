# -*- coding: utf8 -*-
from datetime import datetime
import re

from scrapy.http import Request
from scrapy.selector import Selector

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.spiders.base_spiders.bazaarvoice_spider import BVNoSeleniumSpider
from alascrapy.lib.generic import get_full_url, date_format
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import CategoryItem, ProductItem, ReviewItem, ProductIdItem
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from alascrapy.lib.selenium_browser import SeleniumBrowser


class Medion_nlSpider(AlaSpider):
    name = 'medion_nl'
    allowed_domains = ['medion.com', 'ekomi.de']
    start_urls = ['http://www.medion.com/nl/shop/']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        urls_xpath = "//div[contains(@class, 'navigation-main-sub-level')]//a[contains(@class, 'navigation-main-item')]/@href"
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
        
        urls_xpath = "//div[contains(@class, 'productTitleLinkTE')]/h2/a/@href"
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
            
            request = Request(single_url, callback=self.level_3)
            
             
            yield request
        url_xpath = "//div[contains(@class, 'pagination-bottom')]//li[last()]/a/@href"
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
            
            request = Request(single_url, callback=self.level_2)
            
            yield request
    
    def level_3(self, response):
                                     
        original_url = response.url
        
        category_leaf_xpath = "//div[@id='ariadne']//li[@class='active'][last()]/a/text()"
        category_path_xpath = "//div[@id='ariadne']//li[@class='active']/a/text()"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
                
                "source_internal_id": "//span[contains(@class, 'article-number')]/text()",
                
                
                "ProductName":"//div[@id='ariadne']//li[last()]/text()",
                
                
                
                "PicURL":"//img[@itemprop='image']/@src",
                
                
                "ProductManufacturer":"MEDION"
                
                            }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['TestUrl'] = original_url
        picurl = product.get("PicURL", "")
        if picurl and picurl[:2] == "//":
            product["PicURL"] = "https:" + product["PicURL"]
        manuf = product.get("ProductManufacturer", "")
        if manuf == "" and "MEDION"[:2] != "//":
            product["ProductManufacturer"] = "MEDION"
        try:
            product["OriginalCategoryName"] = category['category_path']
        except:
            pass

        matches = None
        if product["source_internal_id"]:
            matches = re.search("Art.Nr.[\s\S]* (\d+)", product["source_internal_id"], re.IGNORECASE)
        if matches:
            product["source_internal_id"] = matches.group(1)
                                    

        yield product

        url_xpath = "//iframe[@id='ekomi_Frame']/@src"
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
            
            request = Request(single_url, callback=self.level_4)
            
            request.meta["ProductName"] = product["ProductName"]
            
            request.meta["source_internal_id"] = product["source_internal_id"]
            
            yield request
    
    def level_4(self, response):
                                     
        original_url = response.url
        

        
        button_next_url = ""
        if "//div[@id='pager']//a[contains(text(), 'weiter')]/@href":
            button_next_url = self.extract(response.xpath("//div[@id='pager']//a[contains(text(), 'weiter')]/@href"))
        if button_next_url:
            button_next_url = get_full_url(original_url, button_next_url)
            request = Request(button_next_url, callback=self.level_4)
            
            request.meta["ProductName"] = response.meta["ProductName"]
            
            request.meta["source_internal_id"] = response.meta["source_internal_id"]
            
            yield request

        containers_xpath = "//div[@class='feedback']"
        containers = response.xpath(containers_xpath)
        for review_container in containers:
            review = ReviewItem()
            
            
            
            review['SourceTestRating'] = self.extract(review_container.xpath(".//div[@class='rating_user_inner']/@style"))
            
            
            review['TestDateText'] = self.extract(review_container.xpath(".//div[contains(@class, 'rating_user_date')]/text()"))
            
            
            
            
            review['TestSummary'] = self.extract(review_container.xpath(".//div[@class='rating_user_text']//text()"))
            
            
            
            
            
            
            review['TestUrl'] = original_url
            try:
                review['ProductName'] = product['ProductName']
                review['source_internal_id'] = product['source_internal_id']
            except:
                pass
        

           

            
            review["DBaseCategoryName"] = "USER"
            
                                    

            
            review["SourceTestScale"] = "100"
             
                                    

            
            if review["TestDateText"]:
                
                review["TestDateText"] = date_format(review["TestDateText"], "%d.%m.%Y om %H:%M", ["nl"])
            
                                    

            
            matches = None
            if review["SourceTestRating"]:
                matches = re.search("width:(.+)px", review["SourceTestRating"], re.IGNORECASE)
            if matches:
                review["SourceTestRating"] = matches.group(1)
            
                                    

        
            
                            
            if "ProductName" in ReviewItem.fields:
                review["ProductName"] = response.meta["ProductName"]
                            
            if "source_internal_id" in ReviewItem.fields:
                review["source_internal_id"] = response.meta["source_internal_id"]
                            
            yield review
            
        
