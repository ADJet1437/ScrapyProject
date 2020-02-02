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


class Gaminglives_comSpider(AlaSpider):
    name = 'gaminglives_com'
    allowed_domains = ['gaminglives.com']
    start_urls = ['http://www.gaminglives.com/category/reviews/']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        urls_xpath = "//div[@class='post-inner']//h3/a/@href"
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
        url_xpath = "//div[@class='pagination']/a[last()-1]/@href"
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
        
        category_leaf_xpath = "'gaminglives.com'"
        category_path_xpath = "'gaminglives.com'"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
                
                
                "ProductName":"//tr[@class='reviewtxt'][.//text()='Title']/td[last()]//text()",
                
                
                "OriginalCategoryName":"'gaminglives.com'",
                
                
                "PicURL":"(//div[@class='entry_author_image']/img/@src | //div[@class='post-date']/following::img[1]/@src)[1]",
                
                
                "ProductManufacturer":"//tr[@class='reviewtxt'][.//text()='Publisher']/td[last()]//text()"
                
                            }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['TestUrl'] = original_url
        picurl = product.get("PicURL", "")
        if picurl and picurl[:2] == "//":
            product["PicURL"] = "https:" + product["PicURL"]
        if picurl and picurl[:1] == "/":
            product["PicURL"] = get_full_url(original_url, picurl)
        manuf = product.get("ProductManufacturer", "")
        if manuf == "" and "//tr[@class='reviewtxt'][.//text()='Publisher']/td[last()]//text()"[:2] != "//":
            product["ProductManufacturer"] = "//tr[@class='reviewtxt'][.//text()='Publisher']/td[last()]//text()"
        try:
            product["OriginalCategoryName"] = category['category_path']
        except:
            pass
        ocn = product.get("OriginalCategoryName", "")
        if ocn == "" and "'gaminglives.com'"[:2] != "//":
            product["OriginalCategoryName"] = "'gaminglives.com'"
        review_xpaths = { 
                
                
                "ProductName":"//tr[@class='reviewtxt'][.//text()='Title']/td[last()]//text()",
                
                
                "SourceTestRating":"//img[contains(@title, 'review') and contains(@title, 'policy')]/@src",
                
                
                "TestDateText":"//div[@class='post-date']/text()",
                
                
                "TestPros":"//span[text()='Pros']/following-sibling::ul[1]//text()",
                
                
                "TestCons":"//span[text()='Cons']/following-sibling::ul[1]//text()",
                
                
                "TestSummary":"(//span[text()='Summary']/following-sibling::p[string-length(text())>5][1] | //div[@class='post-date']/following::p[string-length(text())>5][1])[(position()>count(//span[text()='Summary']/following-sibling::p[string-length(text())>5][1]) and count(//span[text()='Summary']/following-sibling::p[string-length(text())>5][1]) > 0) or count(//span[text()='Summary']/following-sibling::p[string-length(text())>5][1]) = 0]//text()",
                
                
                
                "Author":"//a[@rel='author']//text()",
                
                
                "TestTitle":"//div[@class='post']//h1//text()",
                
                
                
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

        review["SourceTestScale"] = "10"
                                    

        matches = None
        field_value = review.get("SourceTestRating", "")
        if field_value:
            matches = re.search("((?<=-)\d+(?=.gif))", field_value, re.IGNORECASE)
        if matches:
            review["SourceTestRating"] = matches.group(1)
                                    

        if review["TestDateText"]:
            
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(review["TestDateText"], "%B %d, %Y", ["en"])
                                    

        yield product


        review["DBaseCategoryName"] = "PRO"
                                    

        
                            
        yield review
        
