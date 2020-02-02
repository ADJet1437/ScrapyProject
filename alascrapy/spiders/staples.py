# -*- coding: utf8 -*-
import re

from scrapy.http import Request
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format
from alascrapy.items import CategoryItem, ReviewItem
from alascrapy.lib.selenium_browser import SeleniumBrowser


class StaplesSpider(AlaSpider):
    name = 'staples'
    allowed_domains = ['staples.com']
    start_urls = ['http://www.staples.com/office/supplies/home']

    
    def parse(self, response):
                                     
        original_url = response.url
        urls_xpath = "//span[@class='scTrack scNavLink']/@data-href"
        urls = self.extract_list(response.xpath(urls_xpath))
        for single_url in urls:
            matches = None
            if "/.+/cat_.+":
                matches = re.search("/.+/cat_.+", single_url, re.IGNORECASE)
            if matches:
                single_url = matches.group(0)
            single_url = get_full_url(original_url, single_url)
            
            request = Request(single_url, callback=self.level_2)
             
            yield request
    
    def level_2(self, response):
                                     
        original_url = response.url
        urls_xpath = "//div[@class='cat_gallery']//a/@href"
        urls = self.extract_list(response.xpath(urls_xpath))
        for single_url in urls:
            matches = None
            if "/.+/cat_.+":
                matches = re.search("/.+/cat_.+", single_url, re.IGNORECASE)
            if matches:
                single_url = matches.group(0)
            single_url = get_full_url(original_url, single_url)
            
            request = Request(single_url, callback=self.level_3)
             
            yield request
    
    def level_3(self, response):
                                     
        original_url = response.url
        urls_xpath = "//div[@class='cat_gallery']//a/@href"
        urls = self.extract_list(response.xpath(urls_xpath))
        for single_url in urls:
            matches = None
            if "/.+/cat_.+":
                matches = re.search("/.+/cat_.+", single_url, re.IGNORECASE)
            if matches:
                single_url = matches.group(0)
            single_url = get_full_url(original_url, single_url)
            
            request = Request(single_url, callback=self.level_4)
             
            yield request
    
    def level_4(self, response):
                                     
        original_url = response.url

        with SeleniumBrowser(self, response) as browser:
        
            wait_for = None
            wait_type, wait_for_xpath = "wait_none", ""
            if wait_for_xpath :
                wait_for = EC.wait_none((By.XPATH, wait_for_xpath))
            browser.get(response.url)
            while True:
                try:
                    selector = browser.click_link("//button[@id='load-more-results']", wait_for)
                    response = selector.response
                except:
                    break
        urls_xpath = "//div[@class='product-info']/a/@href"
        urls = self.extract_list(response.xpath(urls_xpath))
        for single_url in urls:
            matches = None
            if "":
                matches = re.search("", single_url, re.IGNORECASE)
            if matches:
                single_url = matches.group(0)
            single_url = get_full_url(original_url, single_url)
            
            request = Request(single_url, callback=self.level_5)
             
            yield request
    
    def level_5(self, response):
                                     
        original_url = response.url
        category_leaf_xpath = "//li[@typeof='v:Breadcrumb'][last()]/a//text()"
        category_path_xpath = "//li[@typeof='v:Breadcrumb']/a//text()"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
                
                "source_internal_id": "//span[@ng-bind='product.metadata.partnumber']/text()",
                
                
                "ProductName":"//div[@class='stp--grid']//*[@ng-bind-html='product.metadata.name']/text()",
                
                
                
                "PicURL":"//div[@id='STP--Product-Image']//img/@src",
                
                
                            }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        try:
            product["OriginalCategoryName"] = category['category_path']
        except:
            pass

        id_value = self.extract(response.xpath("//span[@ng-bind='product.metadata.partnumber']/text()"))
        if id_value:
            product_id = self.product_id(product)
            product_id['ID_kind'] = "sku"
            product_id['ID_value'] = id_value
            yield product_id
        

        yield product



        
        with SeleniumBrowser(self, response) as browser:
            browser.get(response.url)
        
            first_time = True
            while response.xpath("//span[contains(@class, 'yotpo_next')]") or first_time:
                if not first_time:
                    selector = browser.click_link("//span[contains(@class, 'yotpo_next')]", None)
                    response = selector.response

                first_time = False
                containers_xpath = "//div[@data-review-id]"
                containers = response.xpath(containers_xpath)
                for review_container in containers:
                    review = ReviewItem()
                    
                    review['source_internal_id'] = self.extract(response.xpath("//span[@ng-bind='product.metadata.partnumber']/text()"))
                    
                    
                    review['ProductName'] = self.extract(review_container.xpath("//div[@class='stp--grid']//*[@ng-bind-html='product.metadata.name']/text()"))
                    
                    
                    review['SourceTestRating'] = self.extract(review_container.xpath("count(.//span[contains(@class, 'yotpo-icon-star')])"))
                    
                    
                    review['TestDateText'] = self.extract(review_container.xpath(".//div[contains(@class, 'yotpo-header-element')]//label[contains(@class, 'yotpo-review-date')]/text()"))
                    
                    
                    
                    
                    review['TestSummary'] = self.extract(review_container.xpath(".//div[@class='content-review']/text()"))
                    
                    
                    
                    review['Author'] = self.extract(review_container.xpath(".//div[contains(@class, 'yotpo-header-element')]//label[contains(@class, 'yotpo-user-name')]/text()"))
                    
                    
                    review['TestTitle'] = self.extract(review_container.xpath(".//div[contains(@class, 'content-title')]/text()"))
                    
                    
                    
                    review['TestUrl'] = original_url
                    try:
                        review['ProductName'] = product['ProductName']
                        review['source_internal_id'] = product['source_internal_id']
                    except:
                        pass
           

                
                    review["DBaseCategoryName"] = "USER"
                 
                                     
                
                    if review["TestDateText"]:
                        
                        review["TestDateText"] = date_format(review["TestDateText"], "%m/%d/%y", ["en"])
                
                                    

                
                    review["SourceTestScale"] = "5"
                
                                    

        
                
                            
                    yield review
                
        
