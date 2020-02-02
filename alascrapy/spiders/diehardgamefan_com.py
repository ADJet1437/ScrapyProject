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


class Diehardgamefan_comSpider(AlaSpider):
    name = 'diehardgamefan_com'
    allowed_domains = ['diehardgamefan.com']
    start_urls = ['http://diehardgamefan.com/category/reviews/']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        urls_xpath = "//h2[@class='title']/a/@href"
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
        url_xpath = "//li[contains(.//text(),'Next')]/a/@href"
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
        
        category_leaf_xpath = "//div[@class='post-info']/span[@class='thecategory']/a[last()-1]//text()"
        category_path_xpath = "//div[@class='post-info']/span[@class='thecategory']/a//text()"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
                
                
                
                "OriginalCategoryName":"//div[@class='post-info']/span[@class='thecategory']/a//text()",
                
                
                "PicURL":"//header/following::img[1]/@src",
                
                
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
        if ocn == "" and "//div[@class='post-info']/span[@class='thecategory']/a//text()"[:2] != "//":
            product["OriginalCategoryName"] = "//div[@class='post-info']/span[@class='thecategory']/a//text()"
        review_xpaths = { 
                
                
                
                
                "TestDateText":"//div[@class='post-info']/span[@class='thetime']//text()",
                
                
                
                
                "TestSummary":"//center/following::p[position()>1][string-length(.//text())>2][1]//text()",
                
                
                "TestVerdict":"(//p[count(.//node())>4][contains(.//text(),'Attention') and contains(.//text(),'Summary')] | //p[count(.//node())<=4][contains(.//text(),'Attention') and contains(.//text(),'Summary')]/following::p[string-length(.//text())>2][1])//text()",
                
                
                "Author":"//div[@class='post-info']/span[@class='theauthor']//text()",
                
                
                "TestTitle":"//header//h1//text()",
                
                
                
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
        if review and review['TestTitle']:
            title = review["TestTitle"].lower()
            if ":" in title:
                all_title_parts = title.split(":")
                for part in all_title_parts:
                    review["ProductName"] = part.replace("review", "") if 'review' in part else title.replace("review", "")
            else:
                review["ProductName"] = title.replace("review", "")
            
            review["ProductName"] = review["ProductName"].strip("-: ")
            product["ProductName"] = review["ProductName"]

        if review["TestDateText"]:
            
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(review["TestDateText"], "%B %d, %Y", ["en"])
                                    

        matches = None
        field_value = review.get("TestVerdict", "")
        if field_value:
            matches = re.search("((?<=Short Attention Span Summary).*)", field_value, re.IGNORECASE)
        if matches:
            review["TestVerdict"] = matches.group(1)
                                    

        yield product


        review["DBaseCategoryName"] = "PRO"
                                    

        
                            
        yield review
        
