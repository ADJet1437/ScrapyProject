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


class Technic3d_comSpider(AlaSpider):
    name = 'technic3d_com'
    allowed_domains = ['technic3d.com']
    start_urls = ['https://www.technic3d.com/']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        urls_xpath = "//ul/li/a[contains(@href,'review')]/../div/div[@class='subnavBox']/div/a[contains(@href,'review')]/@href"
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
        
        url_xpath = "//div[@class='pagination']/a/i[contains(@class,'fa-chevron-right')]/../@href"
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
        urls_xpath = "//div[contains(@class,'excerpt')]/div/a/@href"
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
        
        category_leaf_xpath = "//li[@itemprop='itemListElement'][last()]//span//text()"
        category_path_xpath = "//li[@itemprop='itemListElement']//span//text()"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
                
                
                
                "OriginalCategoryName":"//li[@itemprop='itemListElement']//span//text()",
                
                
                "PicURL":"(//div[@class='rcolumn']/figure/img/@src | //div[@itemprop='reviewBody']/div/img/@src)[1]",
                
                
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
        if ocn == "" and "//li[@itemprop='itemListElement']//span//text()"[:2] != "//":
            product["OriginalCategoryName"] = "//li[@itemprop='itemListElement']//span//text()"
        review_xpaths = { 
                
                
                
                "SourceTestRating":"//span[@itemprop='reviewRating']/meta[@itemprop='ratingValue']/@content",
                
                
                "TestDateText":"//div[@class='rcolumn']/time[@itemprop='datePublished']//text()",
                
                
                
                
                "TestSummary":"//meta[@property='og:description']/@content",
                
                
                
                "Author":"//span[@itemprop='author']//span[@itemprop='name']//text()",
                
                
                "TestTitle":"//div[@class='headline']//h1//text()",
                
                
                
                            }
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        review['TestUrl'] = original_url
        try:
            review['ProductName'] = product['ProductName']
            review['source_internal_id'] = product['source_internal_id']
        except:
            pass

        review["SourceTestScale"] = "100"
                                    
        if review and review['TestTitle']:
            title = review["TestTitle"].lower()
            if ":" in title:
                all_title_parts = title.split(":")
                for part in all_title_parts:
                    review["ProductName"] = part.replace("review", "") if 'review' in part else title.replace("review", "")
            else:
                review["ProductName"] = title.replace("review", "")
            
            review["ProductName"] = review["ProductName"].replace("".lower(), "")
            
            review["ProductName"] = review["ProductName"].strip("-: ")
            product["ProductName"] = review["ProductName"]

        if review["TestDateText"]:
            
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(review["TestDateText"], "%d.%m.%Y", ["de"])
                                    

        yield product


        review["DBaseCategoryName"] = "PRO"
                                    

        
                            
        yield review
        
