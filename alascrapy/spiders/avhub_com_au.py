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


class Avhub_com_auSpider(AlaSpider):
    name = 'avhub_com_au'
    allowed_domains = ['avhub.com.au']
    start_urls = ['http://www.avhub.com.au/product-reviews/']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        urls_xpath = "//div[@class='blog']//div[@class='contentintro']//a/@href"
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
        url_xpath = "//ul[@class='pagination']//img[@alt='next']/../@href"
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
        
        category_leaf_xpath = "'avhub.com.au'"
        category_path_xpath = "'avhub.com.au'"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
                
                
                "ProductName":"//div[@id='review-info']/strong[contains(text(),'Name')]/following::text()[1]",
                
                
                
                
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
        if ocn == "" and ""[:2] != "//":
            product["OriginalCategoryName"] = ""
        review_xpaths = { 
                
                
                "ProductName":"//div[@id='review-info']/strong[contains(text(),'Name')]/following::text()[1]",
                
                
                
                
                "TestPros":"//div[@id='maincontent']/p[position()>(count(//div[@id='maincontent']/p[strong[text()='PROS']]/preceding-sibling::p)+1) and position()<=count(//div[@id='maincontent']/p[strong[text()='CONS']]/preceding-sibling::p)]//text()",
                
                
                "TestCons":"//div[@id='maincontent']/p[position()>(count(//div[@id='maincontent']/p[strong[text()='CONS']]/preceding-sibling::p)+1) and position()<=count(//div[@id='maincontent']/p[strong[text()='CONTACT']]/preceding-sibling::p)]//text()",
                
                
                "TestSummary":"//meta[@property='og:description']/@content",
                
                
                "TestVerdict":"((//p[text()='Conclusion']|//strong[text()='Conclusion'])[1]/following::p[1]//text()|//strong[text()='CONCLUSION']/../text())[1]",
                
                
                "Author":"//strong[contains(text(),'By:')]/following::text()[1]",
                
                
                "TestTitle":"//div[@id='review-box']//h1[@class='title']//text()",
                
                
                
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

        yield product


        review["DBaseCategoryName"] = "PRO"
                                    

        
                            
        yield review
        
