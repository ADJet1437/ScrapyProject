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


class Nl_beatsbydre_comSpider(AlaSpider):
    name = 'nl_beatsbydre_com'
    allowed_domains = ['beatsbydre.com']
    start_urls = ['http://nl.beatsbydre.com/']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        with SeleniumBrowser(self, response) as browser:
            browser.get(response.url)
            original_request = response.request
            response = Selector(text=browser.browser.page_source).response
            response = HtmlResponse(original_url).replace(body=response.body)
            response.request = original_request
        
        urls_xpath = "//div[contains(@class, 'swiper-container')]//div[1]/a/@href"
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
        
        product_xpaths = { 
                
                "source_internal_id": "//link[@rel='canonical']/@href",
                
                
                "ProductName":"//h1/img/@alt",
                
                
                "OriginalCategoryName":"Headphone",
                
                
                "PicURL":"//meta[@property='og:image'][1]/@content",
                
                
                "ProductManufacturer":"apple"
                
                            }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['TestUrl'] = original_url
        picurl = product.get("PicURL", "")
        if picurl and picurl[:2] == "//":
            product["PicURL"] = "https:" + product["PicURL"]
        if picurl and picurl[:1] == "/":
            product["PicURL"] = get_full_url(original_url, picurl)
        manuf = product.get("ProductManufacturer", "")
        if manuf == "" and "apple"[:2] != "//":
            product["ProductManufacturer"] = "apple"
        try:
            product["OriginalCategoryName"] = category['category_path']
        except:
            pass
        ocn = product["OriginalCategoryName"]
        if ocn == "" and "Headphone"[:2] != "//":
            product["OriginalCategoryName"] = "Headphone"

        matches = None
        if product["source_internal_id"]:
            matches = re.search("http://nl.beatsbydre.com/nl.*/(.+).html", product["source_internal_id"], re.IGNORECASE)
        if matches:
            product["source_internal_id"] = matches.group(1)
                                    

        yield product


        
        button_next_url = ""
        if "//span[contains(@class, 'BVRRNextPage')]/a/@href":
            button_next_url = self.extract(response.xpath("//span[contains(@class, 'BVRRNextPage')]/a/@href"))
        if button_next_url:
            button_next_url = get_full_url(original_url, button_next_url)
            request = Request(button_next_url, callback=self.level_2)
            
            yield request

        containers_xpath = "//div[@itemprop='review']"
        containers = response.xpath(containers_xpath)
        for review_container in containers:
            review = ReviewItem()
            
            review['source_internal_id'] = self.extract(response.xpath("//link[@rel='canonical']/@href"))
            
            
            review['ProductName'] = self.extract(review_container.xpath("//h1/img/@alt"))
            
            
            review['SourceTestRating'] = self.extract(review_container.xpath(".//span[@itemprop='ratingValue']//text()"))
            
            
            review['TestDateText'] = self.extract(review_container.xpath(".//meta[@itemprop='datePublished']/@content"))
            
            
            
            
            review['TestSummary'] = self.extract(review_container.xpath(".//span[@itemprop='description']//text()"))
            
            
            
            review['Author'] = self.extract(review_container.xpath(".//span[@itemprop='author']//text()"))
            
            
            review['TestTitle'] = self.extract(review_container.xpath(".//span[@itemprop='name']//text()"))
            
            
            
            review['TestUrl'] = original_url
            try:
                review['ProductName'] = product['ProductName']
                review['source_internal_id'] = product['source_internal_id']
            except:
                pass
        

           

            
            review["DBaseCategoryName"] = "USER"
            
                                    

            
            review["SourceTestScale"] = "5"
             
                                    

        
            
                            
            yield review
            
        
