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


class Gameblog_frSpider(AlaSpider):
    name = 'gameblog_fr'
    allowed_domains = ['gameblog.fr']
    start_urls = ['http://www.gameblog.fr/tests.php']

    
    def parse(self, response):
                                     
        original_url = response.url
        product = response.meta.get("product", {})
        review = response.meta.get("review", {})
        
        url_xpath = "//td[@class='nextPage']/a/@href"
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
            try:
                request.meta["product"] = product
            except:
                pass
            try:
                request.meta["review"] = review
            except:
                pass
            yield request
        urls_xpath = "//article/div[@class='wrapper']/a/@href"
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
            
             
            try:
                request.meta["product"] = product
            except:
                pass
            try:
                request.meta["review"] = review
            except:
                pass
            yield request
    
    def level_2(self, response):
                                     
        original_url = response.url
        product = response.meta.get("product", {})
        review = response.meta.get("review", {})
        
        category_leaf_xpath = "(//div[@class='ariane']/div[@class='section_name']//text()[normalize-space()])[last()]"
        category_path_xpath = "//div[@class='ariane']/div[@class='section_name']//text()[normalize-space()]"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
                
                "source_internal_id": "//div[@id='add_favorites']/@data-value",
                
                
                "ProductName":"//header[@id='gbArticleHeader']//h1/text()[normalize-space()]",
                
                
                "OriginalCategoryName":"//div[@class='ariane']/div[@class='section_name']//text()[normalize-space()]",
                
                
                
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
        if ocn == "" and "//div[@class='ariane']/div[@class='section_name']//text()[normalize-space()]"[:2] != "//":
            product["OriginalCategoryName"] = "//div[@class='ariane']/div[@class='section_name']//text()[normalize-space()]"
        review_xpaths = { 
                
                "source_internal_id": "//div[@id='add_favorites']/@data-value",
                
                
                "ProductName":"//header[@id='gbArticleHeader']//h1/text()[normalize-space()]",
                
                
                "SourceTestRating":"//span[@itemprop='ratingValue']/text()",
                
                
                "TestDateText":"//header//time[last()]/@datetime",
                
                
                "TestPros":"(//div[@class='plus_minus_title'])[1]/following::ul[1]/li/text()[normalize-space()]",
                
                
                "TestCons":"(//div[@class='plus_minus_title'])[1]/following::ul[2]/li/text()[normalize-space()]",
                
                
                "TestSummary":"//p[@class='chapeau']//text()",
                
                
                "TestVerdict":"//div[@itemprop='reviewBody']//text()[normalize-space()]",
                
                
                "Author":"//span[@class='author']//text()",
                
                
                "TestTitle":"//header[@id='gbArticleHeader']//h1/text()[normalize-space()]",
                
                
                
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
        field_value = review.get("TestDateTest", "")
        if field_value:
            matches = re.search("(\d{4}-\d{2}-\d{2})", field_value, re.IGNORECASE)
        if matches:
            review["TestDateTest"] = matches.group(1)
                                    

        review["DBaseCategoryName"] = "PRO"
                                    

        yield product


        
                            
        yield review
        
