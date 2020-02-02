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


class Gadgetgear_nlSpider(AlaSpider):
    name = 'gadgetgear_nl'
    allowed_domains = ['gadgetgear.nl']
    start_urls = ['http://www.gadgetgear.nl/tag/review/']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        urls_xpath = "//h2[contains(@class,'biglink')]//a[contains(text(),'Review:')]//@href"
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
        url_xpath = "//h2[contains(@class,'biglink')]//a[contains(text(),'Volgende pagina')]/@href"
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
        
        category_leaf_xpath = "//p[@class='link']//a[@title][last()-1]//text()"
        category_path_xpath = "//p[@class='link']//a[@title]//text()"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
                
                
                
                "OriginalCategoryName":"//p[@class='link']//a[@title]//text()",
                
                
                "PicURL":"//article//h1/../img/@src",
                
                
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
        ocn = product["OriginalCategoryName"]
        if ocn == "" and "//p[@class='link']//a[@title]//text()"[:2] != "//":
            product["OriginalCategoryName"] = "//p[@class='link']//a[@title]//text()"
        review_xpaths = { 
                
                
                
                "SourceTestRating":"//span[@itemprop='ratingValue']//text()",
                
                
                "TestDateText":"//span[@itemprop='datePublished']//text()",
                
                
                "TestPros":"//div[@class='col-md-8']//ul[position()=1]//li//text()",
                
                
                "TestCons":"//div[@class='col-md-8']//ul[position()=2]//li//text()",
                
                
                "TestSummary":"//span[@itemprop='reviewBody']//div//p[1]//text()|//div[@class='mainContent']/p[1]//text()",
                
                
                "TestVerdict":"//h2[text()='Conclusie']//following-sibling::p[1]//text()",
                
                
                "Author":"//span[@itemprop='author']//span[@itemprop='name']//text()",
                
                
                "TestTitle":"//article//h1//text()",
                
                
                "award":"//div[@class='col-md-4']//img//@alt",
                
                
                "AwardPic":"//div[@class='col-md-4']//img//@src"
                
                            }
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        review['TestUrl'] = original_url
        try:
            review['ProductName'] = product['ProductName']
            review['source_internal_id'] = product['source_internal_id']
        except:
            pass

        review["SourceTestScale"] = "5"
                                    
        if review and review['TestTitle']:
            title = review["TestTitle"].lower()
            if ":" in title:
                all_title_parts = title.split(":")
                for part in all_title_parts:
                    review["ProductName"] = part.replace("review", "") if 'review' in part else title.replace("review", "")
            else:
                review["ProductName"] = title.replace("review", "")
            
            review["ProductName"] = review["ProductName"].replace("REVIEW: ".lower(), "")
            
            review["ProductName"] = review["ProductName"].strip("-: ")
            product["ProductName"] = review["ProductName"]

        matches = None
        if review["TestDateText"]:
            matches = re.search("\w+ (.+)", review["TestDateText"], re.IGNORECASE)
        if matches:
            review["TestDateText"] = matches.group(1)
                                    

        if review["TestDateText"]:
            
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(review["TestDateText"], "%d %B %Y", ["nl"])
                                    

        yield product


        review["DBaseCategoryName"] = "PRO"
                                    

        
                            
        yield review
        
