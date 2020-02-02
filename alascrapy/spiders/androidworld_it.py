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


class Androidworld_itSpider(AlaSpider):
    name = 'androidworld_it'
    allowed_domains = ['androidworld.it']
    start_urls = ['http://www.androidworld.it/recensioni/']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        url_xpath = "//div[@id='pagination']/a[last()]/@href"
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
        urls_xpath = "//h2[starts-with(@class,'entry')]/a/@href"
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
                
                "source_internal_id": "//body/@class",
                
                
                "ProductName":"//h3[@itemprop='itemReviewed']/span[@itemprop='name']/text()",
                
                
                "OriginalCategoryName":"//section[@id='content']/article[1]//span[@class='cat']//text()",
                
                
                "PicURL":"//meta[@property='og:image']/@content",
                
                
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
        if ocn == "" and "//section[@id='content']/article[1]//span[@class='cat']//text()"[:2] != "//":
            product["OriginalCategoryName"] = "//section[@id='content']/article[1]//span[@class='cat']//text()"
        review_xpaths = { 
                
                "source_internal_id": "//body/@class",
                
                
                "ProductName":"//h3[@itemprop='itemReviewed']/span[@itemprop='name']/text()",
                
                
                "SourceTestRating":"//div[@class='head-vote']//p/text()",
                
                
                "TestDateText":"//meta[contains(@property,'date')]/@content",
                
                
                "TestPros":"//span[starts-with(normalize-space(),'Pro')]/following-sibling::*[1]//*[text()]/text()",
                
                
                "TestCons":"//span[starts-with(normalize-space(),'Contro')]/following-sibling::*[1]//*[text()]/text()",
                
                
                "TestSummary":"//span[@class='fix']/following-sibling::p[text()][1]//text()",
                
                
                "TestVerdict":"string(//*[text()=(//meta[@itemprop='ratingValue']/following-sibling::node()[not(name()) or text()[preceding-sibling::meta[@itemprop='ratingValue']]])])",
                
                
                "Author":"//span[@class='authorname']//text()",
                
                
                "TestTitle":"//h1[@itemtype='headline']/text()",
                
                
                
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

        review["DBaseCategoryName"] = "PRO"
                                    

        review["SourceTestScale"] = "10"
                                    

        matches = None
        field_value = product.get("source_internal_id", "")
        if field_value:
            matches = re.search("((?<=id-)\d*(?=\s))", field_value, re.IGNORECASE)
        if matches:
            product["source_internal_id"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("source_internal_id", "")
        if field_value:
            matches = re.search("((?<=id-)\d*(?=\s))", field_value, re.IGNORECASE)
        if matches:
            review["source_internal_id"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("TestDateText", "")
        if field_value:
            matches = re.search("(\d[^\s]*\d(?=T))", field_value, re.IGNORECASE)
        if matches:
            review["TestDateText"] = matches.group(1)
                                    

        yield product


        
                            
        yield review
        
