# -*- coding: utf8 -*-
import re

from scrapy.http import Request
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url
from alascrapy.items import CategoryItem, ReviewItem
from alascrapy.lib.selenium_browser import SeleniumBrowser


class Appliancesonline_com_auSpider(AlaSpider):
    name = 'appliancesonline_com_au'
    allowed_domains = ['appliancesonline.com.au']
    start_urls = ['https://www.appliancesonline.com.au/']

    
    def parse(self, response):

        original_url = response.url
        with SeleniumBrowser(self, response) as browser:
            selector = browser.get(response.url)
            
        urls_xpath = "//a[@class='sub-item-link']/@href"
        urls = self.extract_list(selector.xpath(urls_xpath))
        for single_url in urls:
            single_url = get_full_url(original_url, single_url)
            matches = None
            if "":
                matches = re.search("", single_url, re.IGNORECASE)
            if matches:
                single_url = matches.group(0)
            
            request = Request(single_url, callback=self.level_2)
             
            yield request
    
    def level_2(self, response):
                                     
        original_url = response.url
        urls_xpath = "//div[@class='catPageTiles']//a[@selenium][contains(@title, 'All')]/@href"
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
        url_xpath = "//div[@class='pages'][last()]//a[img[@title='Next Page']]/@href"
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
        urls_xpath = "//div[@class='product-title-block']/a/@href"
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
        category_leaf_xpath = "//ul[contains(@class, 'breadcrumbs')]//li[@itemprop][last()]//text()"
        category_path_xpath = "//ul[contains(@class, 'breadcrumbs')]//li[a]//text()"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
                
                "source_internal_id": "//script[contains(text(), 'ProductSKU')]/text()",
                
                
                "ProductName":"//li[@class='__item'][last()]//text()",
                
                
                "ProductManufacturer":"//script[contains(text(), 'ProductSKU')]/text()"
                
                            }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        try:
            product["OriginalCategoryName"] = category['category_path']
        except:
            pass

        matches = None
        if product["ProductManufacturer"]:
            matches = re.search("'brand': '(.+)',", product["ProductManufacturer"], re.IGNORECASE)
        if matches:
            product["ProductManufacturer"] = matches.group(1)

        matches = None
        if product["source_internal_id"]:
            matches = re.search("'ProductSKU': '(.+)',", product["source_internal_id"], re.IGNORECASE)
        if matches:
            product["source_internal_id"] = matches.group(1)


        product_id = self.product_id(product)
        product_id['ID_kind'] = "sku"
        product_id['ID_value'] = product["source_internal_id"]
        yield product_id


        with SeleniumBrowser(self, response) as browser:
        
            wait_for = None
            wait_type, wait_for_xpath = "presence_of_all_elements_located", "//li[contains(@class, 'review-item')]"
            if wait_for_xpath :
                wait_for = EC.presence_of_all_elements_located((By.XPATH, wait_for_xpath))
            browser.get(response.url)
            selector = browser.click_link("//ul[@class='tabs']//span[text()='Reviews']", wait_for)
            response = selector.response
            product['PicURL'] = get_full_url(original_url, self.extract(response.xpath("//img[contains(@class, 'media-gallery-main-image')]/@src")))
            yield product


            while True:
                try:
                    selector = browser.click_link("//button[contains(@class, 'load-more-button')]", None)
                    response = selector.response
                except:
                    break

            containers_xpath = "//li[contains(@class, 'review-item')]"
            containers = response.xpath(containers_xpath)
            for review_container in containers:
                review = ReviewItem()
                
                review['source_internal_id'] = self.extract(response.xpath("//script[contains(text(), 'ProductSKU')]/text()"))
                
                
                review['ProductName'] = self.extract(review_container.xpath("//section[@class='product-section']//span[@itemprop='name']/text()"))
                
                
                review['SourceTestRating'] = self.extract(review_container.xpath(".//span[@itemprop='ratingValue']/text()"))
                
                
                review['TestDateText'] = self.extract(review_container.xpath(".//span[contains(@class, 'author-post-time')]/text()"))
                
                
                
                
                review['TestSummary'] = self.extract(review_container.xpath(".//p[contains(@class, 'review-text')]/text()"))
                
                
                
                review['Author'] = self.extract(review_container.xpath(".//span[contains(@class, 'author-name')]/text()"))
                
                
                review['TestTitle'] = self.extract(review_container.xpath(".//h4[contains(@class, 'review-title')]/a/text()"))
                
                
                
                review['TestUrl'] = original_url
                try:
                    review['ProductName'] = product['ProductName']
                    review['source_internal_id'] = product['source_internal_id']
                except:
                    pass
       

                review["DBaseCategoryName"] = "USER"

                review["SourceTestScale"] = "5"
            
                        
                yield review
                
        
