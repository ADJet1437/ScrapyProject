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


class The3g_co_ukSpider(AlaSpider):
    name = 'the3g_co_uk'
    allowed_domains = ['3g.co.uk']
    start_urls = ['https://3g.co.uk/reviews']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        url_xpath = "concat('/reviews',//div[@class='pagination']/a[@class='next']/@href)"
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
        urls_xpath = "//div[contains(@class,'story')]/a/@href"
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
        
        category_leaf_xpath = "//div[contains(@class,'crumb')]/descendant-or-self::a[last()]//text()[normalize-space()]"
        category_path_xpath = "//div[contains(@class,'crumb')]//a//text()[normalize-space()]"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
                
                
                "ProductName":"//h1//text()",
                
                
                "OriginalCategoryName":"//div[contains(@class,'crumb')]//a//text()[normalize-space()]",
                
                
                "PicURL":"//div[contains(@class,'reviewImage')]/img/@src",
                
                
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
        if ocn == "" and "//div[contains(@class,'crumb')]//a//text()[normalize-space()]"[:2] != "//":
            product["OriginalCategoryName"] = "//div[contains(@class,'crumb')]//a//text()[normalize-space()]"
        review_xpaths = { 
                
                
                "ProductName":"//h1//text()",
                
                
                "SourceTestRating":"substring-before(normalize-space(substring-after(substring-after(//div[contains(@class,'blogRowWrapper')]/script,'ratingValue'),':')),' ')",
                
                
                "TestDateText":"substring-before(normalize-space(substring-after(substring-after(//div[contains(@class,'blogRowWrapper')]/script,'datePublished'),':')),',')",
                
                
                "TestPros":"//table[(.//text()[normalize-space()='Pros'] or .//text()[normalize-space()='Pros:'])and (.//text()[normalize-space()='Cons'] or .//text()[normalize-space()='Cons:'])]//tr/td[starts-with(normalize-space(),'+')]//text() | //div[@class='reviewSummary']/p[contains(normalize-space(),'Pros:') or contains(normalize-space(),'Pros ')]/text()[./preceding::*[string-length(normalize-space())>1][1][contains(.,'Pros')]] | //div[@class='reviewSummary']//*[name()='h2' or name()='h3' or (./strong and not(./text()))][contains(.,'Pro')]/following-sibling::p[string-length(normalize-space())>1][1]//text() | //div[@class='reviewSummary']/p[starts-with(normalize-space(./text()),'Pros:') or starts-with(normalize-space(./text()),'Pros :') and string-length(normalize-space(substring-after(normalize-space(),':')))>1]//text()",
                
                
                "TestCons":"//table[(.//text()[normalize-space()='Pros'] or .//text()[normalize-space()='Pros:'])and (.//text()[normalize-space()='Cons'] or .//text()[normalize-space()='Cons:'])]//tr/td[starts-with(normalize-space(),'-')]//text() | //div[@class='reviewSummary']/p[contains(normalize-space(),'Cons:') or contains(normalize-space(),'Cons ')]/text()[./preceding::*[string-length(normalize-space())>1][1][contains(.,'Cons')]] | //div[@class='reviewSummary']//*[name()='h2' or name()='h3' or (./strong and not(./text()))][contains(.,'Con')]/following-sibling::p[string-length(normalize-space())>1][1]//text() | //div[@class='reviewSummary']/p[starts-with(normalize-space(./text()),'Cons:') or starts-with(normalize-space(./text()),'Cons :') and string-length(normalize-space(substring-after(normalize-space(),':')))>1]//text()",
                
                
                "TestSummary":"//div[@class='reviewSummary']//*[contains(.,'Verdict') or contains(.,'Conclusion') or contains(translate(.,' ',''),'Theverdict')]/following-sibling::p[string-length(normalize-space())>1][1]//text() | //div[@class='reviewSummary']//p[contains(.,'erdict') or contains(.,'ERDICT')][last()]//text()[not(normalize-space()='Verdict' or normalize-space()='Verdict:' or normalize-space()='VERDICT' or normalize-space()='VERDICT:') and ./preceding::text()[contains(.,'erdict') or contains(.,'ERDICT')]][string-length(normalize-space())>1] | //div[@id='tab1' and not(normalize-space(//div[@class='reviewSummary']))]/p[string-length(normalize-space(./text()))>1][1]//text() | //div[@class='reviewSummary']/p[string-length(normalize-space(substring-after(normalize-space(./text()),'Verdict:')))>1 or string-length(normalize-space(substring-after(normalize-space(./text()),'Verdict :')))>1]//text()",
                
                
                "TestVerdict":"normalize-space(//div[contains(@class,'content')]/*[contains(.,'erdict') or contains(.,'onclusion')]/following::p[string-length(normalize-space())>1][1])",
                
                
                "Author":"substring-before(normalize-space(substring-after(substring-after(normalize-space(substring-after(substring-after(//div[contains(@class,'blogRowWrapper')]/script,'author'),':')),'name'),':')),'}')",
                
                
                "TestTitle":"//h1//text()",
                
                
                
                            }
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        review['TestUrl'] = original_url
        product_name = product['ProductName']
        patterns_to_remove = ['review', "Review"]
        for pattern in patterns_to_remove:
            if pattern in product_name:
                product_name = product_name.split(pattern)[0]
        try:
            review['ProductName'] = product_name
            product['ProductName'] = product_name
            review['source_internal_id'] = product['source_internal_id']
        except:
            pass
        awpic_link = review.get("AwardPic", "")
        if awpic_link and awpic_link[:2] == "//":
            review["AwardPic"] = "https:" + review["AwardPic"]
        if awpic_link and awpic_link[:1] == "/":
            review["AwardPic"] = get_full_url(original_url, awpic_link)

        review["DBaseCategoryName"] = "PRO"
                                    

        review["SourceTestScale"] = "5"
                                    

        matches = None
        field_value = review.get("TestSummary", "")
        if field_value:
            matches = re.search("(\w[^\:]*[\w|\.|\?])", field_value, re.IGNORECASE)
        if matches:
            review["TestSummary"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("SourceTestRating", "")
        if field_value:
            matches = re.search("(\d.*\d)", field_value, re.IGNORECASE)
        if matches:
            review["SourceTestRating"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("TestDateText", "")
        if field_value:
            matches = re.search("(\d.*\d)", field_value, re.IGNORECASE)
        if matches:
            review["TestDateText"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("Author", "")
        if field_value:
            matches = re.search("(\w.*\w)", field_value, re.IGNORECASE)
        if matches:
            review["Author"] = matches.group(1)
                                    

        yield product


        
                            
        yield review
        
