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


class Sony_nlSpider(AlaSpider):
    name = 'sony_nl'
    allowed_domains = ['sony.nl']
    start_urls = ['http://www.sony.nl/all-electronics']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        urls_xpath = "//li[@class='products-li']/a/@href"
        urls = self.extract_list(response.xpath(urls_xpath))
        
        for single_url in urls:
            matches = None
            if ".+/electronics/.+":
                matches = re.search(".+/electronics/.+", single_url, re.IGNORECASE)
                if matches:
                    single_url = matches.group(0)
                else:
                    continue
            single_url = get_full_url(original_url, single_url)
            
            request = Request(single_url, callback=self.level_2)
             
            yield request
    
    def level_2(self, response):
                                     
        original_url = response.url
        
        urls_xpath = "//button[@class='tab']/@data-tab-url"
        urls = self.extract_list(response.xpath(urls_xpath))
        
        urls.append(original_url)
        
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
    
    def level_3(self, response):
                                     
        original_url = response.url
        
        urls_xpath = "//div[contains(@class, 'products')]/a/@href"
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
            
            request = Request(single_url, callback=self.level_4)
             
            yield request
    
    def level_4(self, response):
                                     
        original_url = response.url
        
        product_xpaths = { 
                
                
                "ProductName":"//h1[@itemprop='name']/text()",
                
                
                "OriginalCategoryName":"//meta[contains(@name, 'category1')]/@content",
                
                
                "PicURL":"//meta[@property='og:image']/@content",
                
                
                "ProductManufacturer":"//meta[@property='og:site_name']/@content"
                
                            }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['TestUrl'] = original_url
        try:
            product["OriginalCategoryName"] = category['category_path']
        except:
            pass

        id_value = self.extract(response.xpath("//span[@itemprop='model']/text()"))
        if id_value:
            product_id = self.product_id(product)
            product_id['ID_kind'] = "sku"
            product_id['ID_value'] = id_value
            yield product_id
        

        yield product

        url_xpath = "//span[contains(@class, 'reviews-text')]/a[@class='primary-link ']/@href"
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
            
            request = Request(single_url, callback=self.level_5)
            
            yield request
    
    def level_5(self, response):
                                     
        original_url = response.url
        


        
        with SeleniumBrowser(self, response) as browser:
            browser.get(response.url)
        
            first_time = True
            while True:
                if not first_time:
                    try:
                        selector = browser.click_link("//button[contains(@class, 'loadmore')]", None)
                        response = selector.response
                    except:
                        break

                first_time = False
                containers_xpath = ".//div[@itemprop='review']"
                containers = response.xpath(containers_xpath)
                for review_container in containers:
                    review = ReviewItem()
                    
                    
                    review['ProductName'] = self.extract(review_container.xpath("//a[contains(@class, 'breadcrumb-link')]/@title"))
                    
                    
                    review['SourceTestRating'] = self.extract(review_container.xpath(".//meta[@itemprop='ratingValue']/@content"))
                    
                    
                    review['TestDateText'] = self.extract(review_container.xpath(".//span[contains(@class, 'review-date')]//text()"))
                    
                    
                    
                    
                    review['TestSummary'] = self.extract(review_container.xpath(".//p[@itemprop='description']/text()"))
                    
                    
                    
                    review['Author'] = self.extract(review_container.xpath(".//span[contains(@class, 'user-nickname')]/text()"))
                    
                    
                    review['TestTitle'] = self.extract(review_container.xpath(".//h4[@itemprop='name']/text()"))
                    
                    
                    
                    review['TestUrl'] = original_url
                    try:
                        review['ProductName'] = product['ProductName']
                        review['source_internal_id'] = product['source_internal_id']
                    except:
                        pass
           

                
                    review["DBaseCategoryName"] = "USER"
                 
                                    

                
                    review["SourceTestScale"] = "5"
                
                                    

                
                    if review["TestDateText"]:
                        
                        review["TestDateText"] = date_format(review["TestDateText"], "%d-%m-%Y", ["en"])
                
                                    

        
                
                            
                    yield review
                
        
