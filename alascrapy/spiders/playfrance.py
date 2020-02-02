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


class PlayfranceSpider(AlaSpider):
    name = 'playfrance'
    allowed_domains = ['playfrance.com']
    start_urls = ['http://www.playfrance.com/tests.html']

    
    def parse(self, response):
                                     
        original_url = response.url
        product = response.meta.get("product", {})
        review = response.meta.get("review", {})
        
        url_xpath = "//div[@class='navig'][1]//a[last()-1]/@href"
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
        urls_xpath = "//div[@class='preview-text']/h3/a/@href"
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
        
        category_leaf_xpath = "//ul[@itemprop='breadcrumb']//text()[normalize-space()][last()-2]"
        category_path_xpath = "//ul[@itemprop='breadcrumb']//text()[normalize-space()]"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
                
                
                "ProductName":"//h2[@class='game-pref']//text()",
                
                
                "OriginalCategoryName":"//ul[@itemprop='breadcrumb']//text()[normalize-space()]",
                
                
                "PicURL":"//div[@class='game-photo']//img/@src",
                
                
                "ProductManufacturer":"//span[@class='field'][contains(.,'veloppeur')]/following::span[1]//text()"
                
                            }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['TestUrl'] = original_url
        picurl = product.get("PicURL", "")
        if picurl and picurl[:2] == "//":
            product["PicURL"] = "https:" + product["PicURL"]
        if picurl and picurl[:1] == "/":
            product["PicURL"] = get_full_url(original_url, picurl)
        manuf = product.get("ProductManufacturer", "")
        if manuf == "" and "//span[@class='field'][contains(.,'veloppeur')]/following::span[1]//text()"[:2] != "//":
            product["ProductManufacturer"] = "//span[@class='field'][contains(.,'veloppeur')]/following::span[1]//text()"
        try:
            product["OriginalCategoryName"] = category['category_path']
        except:
            pass
        ocn = product.get("OriginalCategoryName", "")
        if ocn == "" and "//ul[@itemprop='breadcrumb']//text()[normalize-space()]"[:2] != "//":
            product["OriginalCategoryName"] = "//ul[@itemprop='breadcrumb']//text()[normalize-space()]"
        review_xpaths = { 
                
                
                "ProductName":"//h2[@class='game-pref']//text()",
                
                
                "SourceTestRating":"//span[@itemprop='ratingValue']/text()",
                
                
                "TestDateText":"//meta[@itemprop='datePublished']/@content",
                
                
                "TestPros":"//div[@class='test-plus']//text()",
                
                
                "TestCons":"//div[@class='test-moins']//text()",
                
                
                
                "TestVerdict":"//div[@class='verdict verdict-2']/p//text()[1]",

                "TestSummary":"//div[@class='content']/p[1]//text()",
                
                
                "Author":"(//a[@itemprop='author']//text())[1]",
                
                
                "TestTitle":"//h1[@class='heading']//text()[normalize-space()]",
                
                
                
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
        field_value = review.get("TestDateText", "")
        if field_value:
            matches = re.search("([0-9-]+)T", field_value, re.IGNORECASE)
        if matches:
            review["TestDateText"] = matches.group(1)
                                    

        if review["TestDateText"]:
            
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(review["TestDateText"], "%Y-%B-%d", ["en"])
                                    

        review["DBaseCategoryName"] = "PRO"
                                    

        yield product


        
                            
        yield review
        
