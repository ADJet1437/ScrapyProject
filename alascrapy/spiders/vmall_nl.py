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


class Vmall_nlSpider(AlaSpider):
    name = 'vmall_nl'
    allowed_domains = ['vmall.eu']
    start_urls = ['https://www.vmall.eu/nl/']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        urls_xpath = "//a[@class='nav__primary-link']/@href"
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
        
        urls_xpath = "//a[@class='listing__item-link']/@href"
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
            
            
            matches = None
            text_1 = ""
            extract_text = self.extract(response.xpath('//h1[@class="title-h1"]/text()'))
            if extract_text:
                if "OriginalCategoryName" in params_regex:
                    matches = re.search(params_regex.get("OriginalCategoryName", ""), extract_text, re.IGNORECASE)
                    if matches:
                        text_1 = matches.group(1)
                else:
                    text_1 = extract_text
            request.meta["OriginalCategoryName"] = text_1
             
            yield request
    
    def level_3(self, response):
                                     
        original_url = response.url
        
        product_xpaths = { 
                
                "source_internal_id": "//div[@class='product__head']/@data-initial-sku",
                
                
                "ProductName":"//div[@class='product__core']//span[@class='js-product-title']/text()",
                
                
                
                "PicURL":"//div[@class='product__gallery']//li[contains(@class, 'product__gallery-item')][1]/a/@href",
                
                
                "ProductManufacturer":"HUAWEI"
                
                            }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['TestUrl'] = original_url
        picurl = product.get("PicURL", "")
        if picurl and picurl[:2] == "//":
            product["PicURL"] = "https:" + product["PicURL"]
        manuf = product.get("ProductManufacturer", "")
        if manuf == "" and "HUAWEI"[:2] != "//":
            product["ProductManufacturer"] = "HUAWEI"
        try:
            product["OriginalCategoryName"] = category['category_path']
        except:
            pass

        product_id = self.product_id(product)
        product_id['ID_kind'] = "sku"
        product_id['ID_value'] = product["source_internal_id"]
        yield product_id
        

        yield product


        with SeleniumBrowser(self, response) as browser:
        
            wait_for = None
            wait_type, wait_for_xpath = "wait_none", ""
            if wait_for_xpath :
                wait_for = EC.wait_none((By.XPATH, wait_for_xpath))
            browser.get(response.url)
            if response.xpath("//li[@data-tab='reviews']"):
                selector = browser.click_link("//li[@data-tab='reviews']", wait_for)
                response = selector.response

        
            button_next_url = ""
            if "":
                button_next_url = self.extract(response.xpath(""))
            if button_next_url:
                button_next_url = get_full_url(original_url, button_next_url)
                request = Request(button_next_url, callback=self.level_3)
                
                yield request

            containers_xpath = "//ul[contains(@class, 'product__review')]"
            containers = response.xpath(containers_xpath)
            for review_container in containers:
                review = ReviewItem()
                
                review['source_internal_id'] = self.extract(response.xpath("//div[@class='product__head']/@data-initial-sku"))
                
                
                review['ProductName'] = self.extract(review_container.xpath("//div[@class='product__core']//span[@class='js-product-title']/text()"))
                
                
                review['SourceTestRating'] = self.extract(review_container.xpath(".//div[contains(@class, 'review-avg-stars')]/@class"))
                
                
                review['TestDateText'] = self.extract(review_container.xpath(".//span[contains(@class, 'review-published')]/text()"))
                
                
                
                
                review['TestSummary'] = self.extract(review_container.xpath(".//li[contains(@class, 'review-body')]//text()"))
                
                
                
                review['Author'] = self.extract(review_container.xpath(".//span[contains(@class, 'review-author')]/text()"))
                
                
                review['TestTitle'] = self.extract(review_container.xpath(".//li[contains(@class, 'review-title')]/text()"))
                
                
                
                review['TestUrl'] = original_url
                try:
                    review['ProductName'] = product['ProductName']
                    review['source_internal_id'] = product['source_internal_id']
                except:
                    pass
        

           

            
                review["DBaseCategoryName"] = "USER"
            
                                    

            
                review["SourceTestScale"] = "100"
             
                                    

            
                matches = None
                if review["SourceTestRating"]:
                    matches = re.search(".+--pc(.+)", review["SourceTestRating"], re.IGNORECASE)
                if matches:
                    review["SourceTestRating"] = matches.group(1)
            
                                    

            
                if review["TestDateText"]:
                    
                    review["TestDateText"] = date_format(review["TestDateText"], "%d-%m-%Y", ["en"])
            
                                    

        
            
                            
                yield review
            
        
