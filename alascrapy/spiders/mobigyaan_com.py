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


class Mobigyaan_comSpider(AlaSpider):
    name = 'mobigyaan_com'
    allowed_domains = ['mobigyaan.com']
    start_urls = ['https://www.mobigyaan.com/category/reviews']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        urls_xpath = "//article//h2/a/@href"
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
        url_xpath = "//div[@class='wp-pagenavi']/a[@class='nextpostslink']/@href"
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
        
        category_leaf_xpath = "//nav[@class='gk-breadcrumbs']/span[last()]//text()"
        category_path_xpath = "//nav[@class='gk-breadcrumbs']//text()"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
                
                "source_internal_id": "//article/@id",
                
                
                "ProductName":"//h1//text()",
                
                
                "OriginalCategoryName":"//nav[@class='gk-breadcrumbs']//text()",
                
                
                "PicURL":"//a[@rel='author']/following::img[1]/@src",
                
                
                "ProductManufacturer":"(//nav[@class='gk-breadcrumbs']//*[contains(@href,'mobile-phones-tablets')] | //nav[@class='gk-breadcrumbs'][count(//nav[@class='gk-breadcrumbs']//*[contains(@href,'mobile-phones-tablets')])=0]//*[contains(@href,'category')][1])//text()"
                
                            }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['TestUrl'] = original_url
        picurl = product.get("PicURL", "")
        if picurl and picurl[:2] == "//":
            product["PicURL"] = "https:" + product["PicURL"]
        if picurl and picurl[:1] == "/":
            product["PicURL"] = get_full_url(original_url, picurl)
        manuf = product.get("ProductManufacturer", "")
        if manuf == "" and "(//nav[@class='gk-breadcrumbs']//*[contains(@href,'mobile-phones-tablets')] | //nav[@class='gk-breadcrumbs'][count(//nav[@class='gk-breadcrumbs']//*[contains(@href,'mobile-phones-tablets')])=0]//*[contains(@href,'category')][1])//text()"[:2] != "//":
            product["ProductManufacturer"] = "(//nav[@class='gk-breadcrumbs']//*[contains(@href,'mobile-phones-tablets')] | //nav[@class='gk-breadcrumbs'][count(//nav[@class='gk-breadcrumbs']//*[contains(@href,'mobile-phones-tablets')])=0]//*[contains(@href,'category')][1])//text()"
        try:
            product["OriginalCategoryName"] = category['category_path']
        except:
            pass
        ocn = product.get("OriginalCategoryName", "")
        if ocn == "" and "//nav[@class='gk-breadcrumbs']//text()"[:2] != "//":
            product["OriginalCategoryName"] = "//nav[@class='gk-breadcrumbs']//text()"
        review_xpaths = { 
                
                "source_internal_id": "//article/@id",
                
                
                "ProductName":"//h1//text()",
                
                
                
                "TestDateText":"//time[@class='entry-date']//text()",
                
                
                "TestPros":"((//h2|//strong)[contains(.//text(),'Strength') or contains(.//text(),'Pros')][1]/following::ul[1]/li | //p[strong[contains(.//text(),'Strength') or contains(.//text(),'Pros')]][count(node())>2][count(following-sibling::ul[1])=0] | //p[strong[contains(.//text(),'Strength') or contains(.//text(),'Pros')]][count(node())=1][count(following-sibling::ul[1])=0]/following::p[string-length(.//text())>2][1])//text()",
                
                
                "TestCons":"((//h2|//strong)[contains(.//text(),'Weakness') or contains(.//text(),'Cons')][1]/following::ul[1]/li | //p[strong[contains(.//text(),'Weakness') or contains(.//text(),'Cons')]][count(node())>2][count(following-sibling::ul[1])=0] | //p[strong[contains(.//text(),'Weakness') or contains(.//text(),'Cons')]][count(node())=1][count(following-sibling::ul[1])=0]/following::p[string-length(.//text())>2][1])//text()",
                
                
                "TestSummary":"//meta[@property='og:description']/@content",
                
                
                "TestVerdict":"((//h2|//strong)[contains(.//text(),'Verdict') or contains(.//text(),'Conclusion')][1]/following::p[string-length(.//text())>2][1] | //text()[contains(.,'Final') and contains(.,'Words')][count((//h2|//strong)[contains(.//text(),'Verdict') or contains(.//text(),'Conclusion')])=0]/following::*[name()='span' or name()='p'][1][string-length(.//text())>2][1])//text()",
                
                
                "Author":"//a[@rel='author']//text()",
                
                
                "TestTitle":"//h1//text()",
                
                
                
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

        matches = None
        field_value = product.get("source_internal_id", "")
        if field_value:
            matches = re.search("(\d+)", field_value, re.IGNORECASE)
        if matches:
            product["source_internal_id"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("source_internal_id", "")
        if field_value:
            matches = re.search("(\d+)", field_value, re.IGNORECASE)
        if matches:
            review["source_internal_id"] = matches.group(1)
                                    

        matches = None
        field_value = product.get("ProductName", "")
        if field_value:
            matches = re.search("(.*(?=Review)|.*(?=review)|.*(?=:)|.*(?=Test Results))", field_value, re.IGNORECASE)
        if matches:
            product["ProductName"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("ProductName", "")
        if field_value:
            matches = re.search("(.*(?=Review)|.*(?=review)|.*(?=:)|.*(?=Test Results))", field_value, re.IGNORECASE)
        if matches:
            review["ProductName"] = matches.group(1)
                                    

        if review["TestDateText"]:
            
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(review["TestDateText"], "%B %d, %Y", ["en"])
                                    

        yield product


        review["DBaseCategoryName"] = "PRO"
                                    

        
                            
        yield review
        
