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


class Mobile_review_ruSpider(AlaSpider):
    name = 'mobile_review_ru'
    allowed_domains = ['mobile-review.com']
    start_urls = ['http://www.mobile-review.com/review.shtml']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        urls_xpath = "//div[@class='phonelist']//a/@href"
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
                
                
                "ProductName":"//h1/text()",
                
                
                "OriginalCategoryName":"smartphone",
                
                
                "PicURL":"//div[@class='article']/img[1]/@src",
                
                            }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['TestUrl'] = original_url
        picurl = product.get("PicURL", "")
        if not picurl:
            pic_url_xpath = "//center[img][1]/img/@src"
            picurl = self.extract(response.xpath(pic_url_xpath))
        if picurl:
            if picurl[:4] != 'http':
                product["PicURL"] = original_url.replace(original_url.split('/')[-1], '') + picurl
            else:
                product["PicURL"] = picurl
        manuf = product.get("ProductManufacturer", "")
        if manuf == "" and "//div[@class='article']/img[1]/@src"[:2] != "//":
            product["ProductManufacturer"] = "//div[@class='article']/img[1]/@src"
        try:
            product["OriginalCategoryName"] = category['category_path']
        except:
            pass
        ocn = product["OriginalCategoryName"]
        if ocn == "" and "smartphone"[:2] != "//":
            product["OriginalCategoryName"] = "smartphone"

        yield product

        review_xpaths = { 
                
                
                
                
                "TestDateText":"//p[@class='date']/text()",
                
                
                
                
                "TestSummary":"//meta[@name='Description']/@content",
                
                
                "TestVerdict":"//h3[contains(@id, 's')][last()]/following-sibling::*[1]/text()",
                
                
                "Author":"//p[@align='right']/strong/text()",
                
                
                "TestTitle":"//meta[@name='Keywords']/@content",
                
                
                
                            }
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        review['TestUrl'] = original_url
        try:
            review['ProductName'] = product['ProductName']
            review['source_internal_id'] = product['source_internal_id']
        except:
            pass

        test_date_xpath = "//p[@align='right']/text()[last()]"
        if not review["TestDateText"]:
            review["TestDateText"] = self.extract(response.xpath(test_date_xpath))

        matches = None
        if review["TestDateText"]:
            matches = re.search(".+ (\d{1,2} .+ \d{4}).+", review["TestDateText"], re.IGNORECASE)
        if matches:
            review["TestDateText"] = matches.group(1)
                                    

        if review["TestDateText"]:
            
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(review["TestDateText"], "%d %b %Y", ["ru"])
                                    

        review["DBaseCategoryName"] = "PRO"
                                    

        
                            
        yield review
        
