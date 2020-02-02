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


class Cheatcc_enSpider(AlaSpider):
    name = 'cheatcc_en'
    allowed_domains = ['cheatcc.com']
    start_urls = ['http://www.cheatcc.com/']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        urls_xpath = "//div[contains(@class,'secondary')]//li/a[not(contains(@href,'#'))]/@href"
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
        
        urls_xpath = "//span[@id='cheatcc_reviews']//a/@href"
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
    
    def level_3(self, response):
                                     
        original_url = response.url
        
        product_xpaths = { 
                
                
                "ProductName":"//div[@id='container']/div[@id='mainContent']/div[@class='title']/text()",
                
                
                "OriginalCategoryName":"//div[@class='subtitle']//text()",
                
                
                "PicURL":"//p[img][1]/img/@src",
                
                
                "ProductManufacturer":"//tr/td[contains(text(),'Pub')]/text()"
                
                            }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['TestUrl'] = original_url
        picurl = product.get("PicURL", "")
        if picurl and picurl[:2] == "//":
            product["PicURL"] = "https:" + product["PicURL"]
        if picurl and picurl[:1] == "/":
            product["PicURL"] = get_full_url(original_url, picurl)
        manuf = product.get("ProductManufacturer", "")
        if manuf == "" and "//tr/td[contains(text(),'Pub')]/text()"[:2] != "//":
            product["ProductManufacturer"] = "//tr/td[contains(text(),'Pub')]/text()"
        try:
            product["OriginalCategoryName"] = category['category_path']
        except:
            pass
        ocn = product["OriginalCategoryName"]
        if ocn == "" and "game"[:2] != "//":
            product["OriginalCategoryName"] = "game"

        matches = None
        if product["ProductManufacturer"]:
            matches = re.search("Pub:(.*)", product["ProductManufacturer"], re.IGNORECASE)
        if matches:
            product["ProductManufacturer"] = matches.group(1)
                                    

        matches = None
        if product["ProductName"]:
            matches = re.search("(.*)Review", product["ProductName"], re.IGNORECASE)
        if matches:
            product["ProductName"] = matches.group(1)
                                    
        review_xpaths = { 
                
                
                "ProductName":"//div[@id='container']/div[@id='mainContent']/div[@class='title']/text()",
                
                "SourceTestRating":"//div[contains(@class,'bottom')]/div[contains(@class,'number')]/div/text()",
                
                
                "TestSummary":"//span[@class='editorial-p-title']/text()",
                
                "Author":"//td/font//text()",
                
                
                "TestTitle":"//div[@id='container']/div[@id='mainContent']/div[@class='title']/text()",
                
                "TestPros":"//div[@align='justify']//text()",
                
                            }
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        review['TestUrl'] = original_url
        try:
            review['ProductName'] = product['ProductName']
            review['source_internal_id'] = product['source_internal_id']
        except:
            pass

        review["DBaseCategoryName"] = "PRO"
                                    

        review["SourceTestScale"] = "5"
                                    
        in_another_page_xpath = "//div[@class='editorial-menu']//li[last()]/a/@href"
        pros_xpath = "//div[@align='justify']//text()"
        cons_xpath = ""
        rating_xpath = "//div[contains(@class,'bottom')]/div[contains(@class,'number')]/div/text()"
        award_xpath = ""
        award_pic_xpath = ""
        
        test_verdict_xpath_1 = '//div[@class="content"]/p[last()]/text()'
        
        review["TestVerdict"] = None
        in_another_page_url = None
        if in_another_page_xpath:
            in_another_page_url = self.extract(response.xpath(in_another_page_xpath))
        if in_another_page_url:
            link_replace_part = original_url.split('/')[-1]
            in_another_page_url = original_url.replace(link_replace_part, in_another_page_url)
            request = Request(in_another_page_url, callback=self.parse_fields_page)
            request.meta['review'] = review
            
            request.meta['test_verdict_xpath_1'] = test_verdict_xpath_1
            
            request.meta['pros_xpath'] = pros_xpath
            request.meta['cons_xpath'] = cons_xpath
            request.meta['rating_xpath'] = rating_xpath
            request.meta['award_xpath'] = award_xpath
            request.meta['award_pic_xpath'] = award_pic_xpath
            yield request
        else:
            
            if not review["TestVerdict"]:
                review["TestVerdict"] = self.extract(response.xpath(test_verdict_xpath_1))
            
            yield review

        yield product

    
    def parse_fields_page(self, response):
        review = response.meta['review']
        
        test_verdict_xpath_1 = response.meta['test_verdict_xpath_1']
        
        
        if not review["TestVerdict"]:
            review["TestVerdict"] = self.extract(response.xpath(test_verdict_xpath_1))
        
        pros_xpath = response.meta['pros_xpath']
        cons_xpath = response.meta['cons_xpath']
        rating_xpath = response.meta['rating_xpath']
        award_xpath = response.meta['award_xpath']
        award_pic_xpath = response.meta['award_pic_xpath']
        if pros_xpath:
            review["TestPros"] = self.extract_all(response.xpath(pros_xpath), ' ; ')
        if cons_xpath:
            review["TestCons"] = self.extract_all(response.xpath(cons_xpath), ' ; ')
        if rating_xpath:
            review['SourceTestRating'] = self.extract(response.xpath(rating_xpath), '%')
        if award_xpath:
            review['award'] = self.extract(response.xpath(award_xpath))
        if award_pic_xpath:
            review['AwardPic'] = self.extract(response.xpath(award_pic_xpath))
        author_xpath = "//td/font//text()"
        review['Author'] = self.extract(response.xpath(author_xpath))
        yield review
