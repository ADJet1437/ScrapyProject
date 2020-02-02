# -*- coding: utf8 -*-
import re

from scrapy.http import Request
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format
from alascrapy.items import CategoryItem, ReviewItem
from alascrapy.lib.selenium_browser import SeleniumBrowser


class BhphotovideoSpider(AlaSpider):
    name = 'bhphotovideo'
    allowed_domains = ['bhphotovideo.com']
    start_urls = ['http://www.bhphotovideo.com/']

    
    def parse(self, response):
                                     
        original_url = response.url
        urls_xpath = "//section[@class='main-nav']//li[contains(@id, 'cat')]/a/@href"
        urls = self.extract_list(response.xpath(urls_xpath))
        for single_url in urls:
            single_url = get_full_url(original_url, single_url)
            matches = None
            if "http://.+/N/\d+":
                matches = re.search("http://.+/N/\d+", single_url, re.IGNORECASE)
            if matches:
                single_url = matches.group(0)
            
            request = Request(single_url, callback=self.level_2)
             
            yield request
    
    def level_2(self, response):
                                     
        original_url = response.url
        urls_xpath = "//li[@class='clp-category']/a/@href"
        urls = self.extract_list(response.xpath(urls_xpath))
        for single_url in urls:
            single_url = get_full_url(original_url, single_url)
            matches = None
            if "":
                matches = re.search("", single_url, re.IGNORECASE)
            if matches:
                single_url = matches.group(0)
            
            request = Request(single_url, callback=self.level_3)
             
            yield request
    
    def level_3(self, response):
                                     
        original_url = response.url
        url_xpath = "//div[contains(@class, 'bottom')]//a[@data-selenium='pn-next']/@href"
        single_url = self.extract(response.xpath(url_xpath))
        if single_url:
            single_url = get_full_url(original_url, single_url)
            matches = None
            if "":
                matches = re.search("", single_url, re.IGNORECASE)
            if matches:
                single_url = matches.group(0)
            
            request = Request(single_url, callback=self.level_3)
             
            yield request
        urls_xpath = "//div[@data-selenium='itemInfo-zone']//a[@data-selenium='itemHeadingLink']/@href"
        urls = self.extract_list(response.xpath(urls_xpath))
        for single_url in urls:
            single_url = get_full_url(original_url, single_url)
            matches = None
            if "":
                matches = re.search("", single_url, re.IGNORECASE)
            if matches:
                single_url = matches.group(0)
            
            request = Request(single_url, callback=self.level_4)
             
            yield request
    
    def level_4(self, response):
                                     
        original_url = response.url
        category_leaf_xpath = "//ul[@id='breadcrumbs']//li[last()]//a/text()"
        category_path_xpath = "//ul[@id='breadcrumbs']//a/text()"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
                
                "source_internal_id": "//div[@class='pProductNameContainer']//meta[@itemprop='productID'][1]/@content",
                
                
                "ProductName":"//span[@itemprop='name']/text()",
                
                
                "OriginalCategoryName":"//ul[@id='breadcrumbs']//text()",
                
                
                "PicURL":"//img[@id='mainImage']/@src",
                
                
                "ProductManufacturer":"//div[@class='pProductNameContainer']//span[@itemprop='brand']/text()"
                
                            }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        try:
            product["OriginalCategoryName"] = category['category_path']
        except:
            pass

        matches = None
        if product["source_internal_id"]:
            matches = re.search("sku:(.+)", product["source_internal_id"], re.IGNORECASE)
        if matches:
            product["source_internal_id"] = matches.group(1)
                                    
        yield product

        product_id = self.product_id(product)
        product_id['ID_kind'] = "sku"
        product_id['ID_value'] = product["source_internal_id"]
        yield product_id
        

        with SeleniumBrowser(self, response) as browser:
        
            wait_for = None
            wait_type, wait_for_xpath = "presence_of_all_elements_located", "//div[@class='pr-review-wrap']"
            if wait_for_xpath :
                wait_for = EC.presence_of_all_elements_located((By.XPATH, wait_for_xpath))
            browser.get(response.url)
            selector = browser.click_link("//li[@id='navCustomerReviews']/a", wait_for)
            response = selector.response


        
            first_time = True
            while response.xpath("//div[@class='pr-pagination-bottom']//span[@class='pr-page-next']/a") or first_time:
                if not first_time:
                    selector = browser.click_link("//div[@class='pr-pagination-bottom']//span[@class='pr-page-next']/a", None)
                    response = selector.response

                first_time = False
                containers_xpath = "//div[@class='pr-review-wrap']"
                containers = response.xpath(containers_xpath)
                for review_container in containers:
                    review = ReviewItem()
                    
                    review['source_internal_id'] = self.extract(response.xpath("//div[@class='pProductNameContainer']//meta[@itemprop='productID'][1]/@content"))
                    
                    
                    review['ProductName'] = self.extract(review_container.xpath("//span[@itemprop='name']/text()"))
                    
                    
                    review['SourceTestRating'] = self.extract(review_container.xpath(".//div[contains(@class, 'pr-stars')]/@class"))
                    
                    
                    review['TestDateText'] = self.extract(review_container.xpath(".//div[contains(@class, 'pr-review-author-date')]/text()"))
                    
                    
                    
                    
                    review['TestSummary'] = self.extract(review_container.xpath(".//p[@class='pr-comments']/text()"))
                    
                    
                    
                    review['Author'] = self.extract(review_container.xpath(".//p[@class='pr-review-author-name']/span/text()"))
                    
                    
                    review['TestTitle'] = self.extract(review_container.xpath(".//p[@class='pr-review-rating-headline']//text()"))
                    
                    
                    
                    review['TestUrl'] = original_url
                    try:
                        review['source_internal_id'] = product['source_internal_id']
                        review['ProductName'] = product['ProductName']
                    except:
                        pass
           

                
                    review["DBaseCategoryName"] = "USER"
                 
                                     
                
                    review["SourceTestScale"] = "5"
                
                                    

                
                    if review["TestDateText"]:
                        
                        review["TestDateText"] = date_format(review["TestDateText"], "%d %B %Y", ["en"])
                
                                    

                
                    matches = None
                    if review["SourceTestRating"]:
                        matches = re.search(".+-stars-(\d)-.+", review["SourceTestRating"], re.IGNORECASE)
                    if matches:
                        review["SourceTestRating"] = matches.group(1)
                
                                    

                
                    matches = None
                    if review["source_internal_id"]:
                        matches = re.search("sku:(.+)", review["source_internal_id"], re.IGNORECASE)
                    if matches:
                        review["source_internal_id"] = matches.group(1)
                
                                    

                
                    yield review
                
        
