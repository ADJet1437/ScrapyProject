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


class Cravingtech_comSpider(AlaSpider):
    name = 'cravingtech_com'
    allowed_domains = ['cravingtech.com']
    start_urls = ['http://www.cravingtech.com/category/reviews']

    
    def parse(self, response):
                                     
        original_url = response.url
        

        with SeleniumBrowser(self, response) as browser:
        
            wait_for = None
            wait_type, wait_for_xpath = "wait_none", ""
            if wait_for_xpath :
                wait_for = EC.wait_none((By.XPATH, wait_for_xpath))
            browser.get(response.url)
            selector = browser.scroll_until_the_end(2000, wait_for)
            response = selector.response
        urls_xpath = "//h3[contains(@class,'entry-title')]/a/@href"
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
        
        category_leaf_xpath = "//div[@class='entry-crumbs']/span[last()]//text()"
        category_path_xpath = "//div[@class='entry-crumbs']/span//text()"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
                
                
                
                "OriginalCategoryName":"//div[@class='entry-crumbs']/span//text()",
                
                
                "PicURL":"(//div[@itemprop='reviewBody']/p[img][1]/img/@src|//div[contains(@class,'main-content')]//p[descendant-or-self::img][1]//img/@src)[1]",
                
                
                "ProductManufacturer":"//span[contains(text(),'Manufacturer')]/../text()"
                
                            }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['TestUrl'] = original_url
        picurl = product.get("PicURL", "")
        if picurl and picurl[:2] == "//":
            product["PicURL"] = "https:" + product["PicURL"]
        if picurl and picurl[:1] == "/":
            product["PicURL"] = get_full_url(original_url, picurl)
        manuf = product.get("ProductManufacturer", "")
        if manuf == "" and "//span[contains(text(),'Manufacturer')]/../text()"[:2] != "//":
            product["ProductManufacturer"] = "//span[contains(text(),'Manufacturer')]/../text()"
        try:
            product["OriginalCategoryName"] = category['category_path']
        except:
            pass
        ocn = product["OriginalCategoryName"]
        if ocn == "" and "//div[@class='entry-crumbs']/span//text()"[:2] != "//":
            product["OriginalCategoryName"] = "//div[@class='entry-crumbs']/span//text()"
        review_xpaths = { 
                
                
                
                "SourceTestRating":"//div[@itemprop='reviewRating']/div[@class='result']//text()",
                
                
                "TestDateText":"//header/div[@class='meta-info']//time[contains(@class,'entry-date')]//text()",
                
                
                
                
                "TestSummary":"(//div[contains(@class,'summary')]|//article//div[p][1]/p[text()][1])[1]//text()",
                
                
                "TestVerdict":"//h2[contains(text(),'Conclusion')]/following::p[text()][1]//text()",
                
                
                "Author":"//div[@class='meta-info']/div[contains(@class,'author-name')]/a//text()",
                
                
                "TestTitle":"//header/h1//text()",
                
                
                
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
            
            review["ProductName"] = review["ProductName"].replace("Review".lower(), "")
            
            review["ProductName"] = review["ProductName"].strip("-: ")
            product["ProductName"] = review["ProductName"]

        if review["TestDateText"]:
            
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(review["TestDateText"], "%b %d, %Y", ["en"])
                                    

        yield product


        review["DBaseCategoryName"] = "PRO"
                                    

        
                            
        yield review
        
