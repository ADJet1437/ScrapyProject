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


class Mobilegeeks_deSpider(AlaSpider):
    name = 'mobilegeeks_de'
    allowed_domains = ['mobilegeeks.de']
    start_urls = ['https://www.mobilegeeks.de/test/']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        urls_xpath = "//div[@class='article-info']//h2/a/@href"
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
        url_xpath = "//div[@class='wp-pagenavi']//a[@class='nextpostslink']/@href"
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
            
            yield request
    
    def level_2(self, response):
                                     
        original_url = response.url
        
        category_leaf_xpath = "//div[@class='breadcrumbs']//div[last()]//a//text()"
        category_path_xpath = "//div[@class='breadcrumbs']//a//text()"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
                
                
                "ProductName":"translate(//link[@rel='canonical']/@href,'-',' ')",
                
                
                "OriginalCategoryName":"//div[@class='breadcrumbs']//a//text()",
                
                
                "PicURL":"//div[@class='billboard-image']//img/@src | //div[contains(@class,'main-top')]//span[@class='author'][count(//div[@class='billboard-image']//img)=0]/following::img[1]/@src",
                
                
                "ProductManufacturer":"//div/div[@class='category-top-list'][position()=2]//div[@style='text']//text()"
                
                            }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['TestUrl'] = original_url
        picurl = product.get("PicURL", "")
        if picurl and picurl[:2] == "//":
            product["PicURL"] = "https:" + product["PicURL"]
        if picurl and picurl[:1] == "/":
            product["PicURL"] = get_full_url(original_url, picurl)
        manuf = product.get("ProductManufacturer", "")
        if manuf == "" and "//div/div[@class='category-top-list'][position()=2]//div[@style='text']//text()"[:2] != "//":
            product["ProductManufacturer"] = "//div/div[@class='category-top-list'][position()=2]//div[@style='text']//text()"
        try:
            product["OriginalCategoryName"] = category['category_path']
        except:
            pass
        ocn = product.get("OriginalCategoryName", "")
        if ocn == "" and "//div[@class='breadcrumbs']//a//text()"[:2] != "//":
            product["OriginalCategoryName"] = "//div[@class='breadcrumbs']//a//text()"
        review_xpaths = { 
                
                
                "ProductName":"translate(//link[@rel='canonical']/@href,'-',' ')",
                
                
                "SourceTestRating":"//div[@class='meter-circle']//div[contains(@class,'editor_rating')]//text()",
                
                
                "TestDateText":"substring(//div[contains(@class,'main-top')]//span[@class='date']//text(),5)",
                
                
                "TestPros":"//div[contains(@class,'section-subtitle')][contains(text(),'Pro')]/following::*[name()='ul' or name()='ol'][1]//text()",
                
                
                "TestCons":"//div[contains(@class,'section-subtitle')][contains(text(),'Kontra')]/following::*[name()='ul' or name()='ol'][1]//text()",
                
                
                "TestSummary":"//div[contains(@class,'main-top')]//div[contains(@class,'billboard-subtitle')]//text() | //div[contains(@class,'main-top')]//span[@class='author'][count(//div[contains(@class,'main-top')]//div[contains(@class,'billboard-subtitle')])=0]/following::p[string-length(.//text())>2][1]//text()",
                
                
                "TestVerdict":"//h2[contains(.//text(),'Fazit')]/following-sibling::p[string-length(.//text())>2][1]//text()",
                
                
                "Author":"//div[contains(@class,'main-top')]//span[@class='author']//a//text()",
                
                
                "TestTitle":"//h1[contains(@class,'main-title')]//text()",
                
                
                
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
        field_value = product.get("ProductName", "")
        if field_value:
            matches = re.search("((?<=test/).*(?=/))", field_value, re.IGNORECASE)
        if matches:
            product["ProductName"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("ProductName", "")
        if field_value:
            matches = re.search("((?<=test/).*(?=/))", field_value, re.IGNORECASE)
        if matches:
            review["ProductName"] = matches.group(1)
                                    

        review["SourceTestScale"] = "10"
                                    

        if review["TestDateText"]:
            
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(review["TestDateText"], "%d. %B %Y", ["de"])
                                    

        yield product


        review["DBaseCategoryName"] = "PRO"
                                    

        
                            
        yield review
        
