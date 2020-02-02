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


class Koffiecenter_nlSpider(AlaSpider):
    name = 'koffiecenter_nl'
    allowed_domains = ['koffiecenter.nl']
    start_urls = ['http://www.koffiecenter.nl/']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        urls_xpath = "//li[position()>1 and position()<last()]//a[contains(@class,'nav-action')]/@href"
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
        
        urls_xpath = "//li[contains(@class,'product-list')]//h2/a/@href"
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
        url_xpath = "//div[@class='paging-footer']//div[@class='paging-navigation']/a[contains(@class,'next')]/@href"
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
        
        urls_xpath = "//div[contains(@class,'title-links')]//span[contains(@class,'reviews')]/a/@href"
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
            
            request = Request(single_url, callback=self.level_4)
            
             
            yield request
    
    def level_4(self, response):
                                     
        original_url = response.url
        
        category_leaf_xpath = "//ol[@class='breadcrumbs']//ol/li[last()]//a//span//text()"
        category_path_xpath = "//ol[@class='breadcrumbs']//span//text()"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
                
                "source_internal_id": "//div[@class='overviewHeaderTitle']//h1/a/@href",
                
                
                "ProductName":"//div[@class='overviewHeaderTitle']//h1/a//text()",
                
                
                "OriginalCategoryName":"//ol[@class='breadcrumbs']//span//text()",
                
                
                "PicURL":"//div[@class='headerContent']//img/@src",
                
                
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
        if ocn == "" and "//ol[@class='breadcrumbs']//span//text()"[:2] != "//":
            product["OriginalCategoryName"] = "//ol[@class='breadcrumbs']//span//text()"

        matches = None
        field_value = product.get("source_internal_id", "")
        if field_value:
            matches = re.search("((?<=/)\d+(?=/))", field_value, re.IGNORECASE)
        if matches:
            product["source_internal_id"] = matches.group(1)
                                    

        yield product


        
        button_next_url = ""
        if "//div[contains(@class,'paging-footer')]//a[contains(@class,'next')]/@href":
            button_next_url = self.extract(response.xpath("//div[contains(@class,'paging-footer')]//a[contains(@class,'next')]/@href"))
        if button_next_url:
            button_next_url = get_full_url(original_url, button_next_url)
            request = Request(button_next_url, callback=self.level_4)
            
            yield request

        containers_xpath = "//ul[@class='reviewList']/li[@class='review']"
        containers = response.xpath(containers_xpath)
        for review_container in containers:
            review = ReviewItem()
            
            review['source_internal_id'] = self.extract(response.xpath("//div[@class='overviewHeaderTitle']//h1/a/@href"))
            
            
            review['ProductName'] = self.extract(review_container.xpath("//div[@class='overviewHeaderTitle']//h1/a//text()"))
            
            
            review['SourceTestRating'] = self.extract(review_container.xpath(".//div[@class='reviewAverageRating']//meter/@value"))
            
            
            review['TestDateText'] = self.extract(review_container.xpath(".//span[@class='writeDate']//time//text()"))
            
            
            review['TestPros'] = self.extract(review_container.xpath(".//div[@class='pros']//ul/li//text()"))
            
            
            review['TestCons'] = self.extract(review_container.xpath(".//div[@class='cons']//ul/li//text()"))
            
            
            review['TestSummary'] = self.extract(review_container.xpath(".//div[contains(@class,'reviewText')]//p[count(br)=0]/text() | .//div[contains(@class,'reviewText')]//br[position()=1]/preceding-sibling::text()[1]"))
            
            
            
            review['Author'] = self.extract(review_container.xpath(".//div[@class='reviewWriter']/strong//text()"))
            
            
            review['TestTitle'] = self.extract(review_container.xpath(".//div[@class='reviewContent']/h3/a//text()"))
            
            
            
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
            field_value = review.get("source_internal_id", "")
            if field_value:
                matches = re.search("((?<=/)\d+(?=/))", field_value, re.IGNORECASE)
            if matches:
                review["source_internal_id"] = matches.group(1)
            
                                    

            
            review["SourceTestScale"] = "5"
             
                                    

            
            if review["TestDateText"]:
                
                review["TestDateText"] = date_format(review["TestDateText"], "%d %B %Y", ["nl"])
            
                                    

            
            review["DBaseCategoryName"] = "USER"
            
                                    

        
            
                            
            yield review
            
        
