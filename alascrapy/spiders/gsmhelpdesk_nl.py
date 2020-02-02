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


class Gsmhelpdesk_nlSpider(AlaSpider):
    name = 'gsmhelpdesk_nl'
    allowed_domains = ['gsmhelpdesk.nl']
    start_urls = ['http://www.gsmhelpdesk.nl/reviews']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        url_xpath = "//div[@class='pagination']/a[contains(@class,'active')]/following-sibling::a[1]/@href"
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
        urls_xpath = "//div[contains(@class,'main-list')]/div[@class='row']//a[@class='title']/@href"
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
                
                "source_internal_id": "substring-before(substring-after(//meta[@property='og:url']/@content,'/reviews/'),'/')",
                
                
                "ProductName":"//meta[@property='og:title']/@content",
                
                
                "OriginalCategoryName":"//ol[@class='breadcrumb']/li[last()-1]//text()",
                
                
                "PicURL":"//meta[@property='og:image']/@content",
                
                
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
        if ocn == "" and "//ol[@class='breadcrumb']/li[last()-1]//text()"[:2] != "//":
            product["OriginalCategoryName"] = "//ol[@class='breadcrumb']/li[last()-1]//text()"
        review_xpaths = { 
                
                "source_internal_id": "substring-before(substring-after(//meta[@property='og:url']/@content,'/reviews/'),'/')",
                
                
                "ProductName":"//meta[@property='og:title']/@content",
                
                
                "SourceTestRating":"concat(' ',translate(concat(string(number(translate(//div[starts-with(@id,'body')]/descendant-or-self::img[@class='rating'][1]/@title,',','.'))*2),translate(string(//*[contains(.,'Conclusie') and not(//img[@class='rating'])]/following::node()[(contains(.,'eindcijfer') or contains(.,'rapportcijfer') or contains(.,'totaal') or contains(.,'afgerond')) and not(./following::node()[1][name()='b'] or ./preceding::node()[1][name()='b'] or ./b)][last()]),',','.'),translate(//*[contains(.,'Conclusie') and not(//img[@class='rating'])]/following::node()[(contains(.,'eindcijfer') or contains(.,'rapportcijfer') or contains(.,'totaal') or contains(.,'afgerond')) and (./following::node()[1][name()='b'] or ./preceding::node()[1][name()='b'] or ./b)][last()]/descendant-or-self::b[1]/text(),',','.')),'NaN',''))",
                
                
                "TestDateText":"//body/descendant-or-self::h1[1]/following::div[starts-with(@class,'date')][1]//text()",
                
                
                "TestPros":"//div[starts-with(@id,'body')]/descendant-or-self::h2[contains(.,'Plus') and contains(.,'minpunten')][1]/following::p[.//*[starts-with(.,'+')]][1]//text()[string-length(normalize-space())>1] | //li[./preceding::b[starts-with(.,'Voordelen') or starts-with(.,'Pluspunten')] and ./following::b[starts-with(.,'Nadelen') or starts-with(.,'Minpunten')]]/descendant-or-self::*[last()]/text()",
                
                
                "TestCons":"//div[starts-with(@id,'body')]/descendant-or-self::h2[contains(.,'Plus') and contains(.,'minpunten')][1]/following::p[.//*[starts-with(.,'-')]][1]//text()[string-length(normalize-space())>1] | //li[./preceding::b[starts-with(.,'Nadelen') or starts-with(.,'Minpunten')]/preceding::b[starts-with(.,'Voordelen') or starts-with(.,'Pluspunten')]]/b[not(./ancestor::div[@id='comment-area'])]/text()",
                
                
                "TestSummary":"//body/descendant-or-self::h1[1]/following::p[string-length(normalize-space())>1][1]//text()",
                
                
                "TestVerdict":"//div[starts-with(@id,'body')]/descendant-or-self::*[(name()='h2' or name()='h1' or (name()='div' and @class='title')) and contains(.,'Conclusie') and count(//tbody[contains(.,'Conclusie')])<2][1]/following::node()[(name()='p' or (name()='div' and @class='content')) and string-length(normalize-space())>1][1]//text()[not(./preceding-sibling::br/preceding-sibling::node()[normalize-space()]) and not(../preceding-sibling::br/preceding-sibling::node()[normalize-space()]) and not(../preceding-sibling::img)] | //div[starts-with(@id,'body')]/descendant-or-self::*[(name()='h2' or name()='h1' or (name()='div' and @class='title')) and contains(.,'Conclusie') and count(//tbody[contains(.,'Conclusie')])<2][1]/following::node()[not(name()) and string-length(normalize-space())>1 and not(./preceding-sibling::br/preceding-sibling::node()[normalize-space()])][1] | //body/descendant-or-self::tbody[contains(.,'Conclusie') and count(//tbody[contains(.,'Conclusie')])>1][last()]/following::node()[string-length(normalize-space())>1][1]",
                
                
                "Author":"//body/descendant-or-self::h1[1]/following::div[starts-with(@class,'date')][1]//text()",
                
                
                "TestTitle":"//meta[@property='og:title']/@content",
                
                
                
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

        review["DBaseCategoryName"] = "PRO"
                                    

        review["SourceTestScale"] = "10"
                                    

        matches = None
        field_value = review.get("TestDateText", "")
        if field_value:
            matches = re.search("(\d{2}\-\d{2}\-\d{4})", field_value, re.IGNORECASE)
        if matches:
            review["TestDateText"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("Author", "")
        if field_value:
            matches = re.search("((?<=\|)\D*\w)", field_value, re.IGNORECASE)
        if matches:
            review["Author"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("Author", "")
        if field_value:
            matches = re.search("(\D*(?=\|))", field_value, re.IGNORECASE)
        if matches:
            review["Author"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("Author", "")
        if field_value:
            matches = re.search("(\w.*\w)", field_value, re.IGNORECASE)
        if matches:
            review["Author"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("SourceTestRating", "")
        if field_value:
            matches = re.search("((?<=\s)\d{1}\.\d{2}(?=(\s|\.)))", field_value, re.IGNORECASE)
        if matches:
            review["SourceTestRating"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("SourceTestRating", "")
        if field_value:
            matches = re.search("((?<=\s)\d{1}\.\d{1}(?=(\s|\.)))", field_value, re.IGNORECASE)
        if matches:
            review["SourceTestRating"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("SourceTestRating", "")
        if field_value:
            matches = re.search("((?<=\s)\d{1}(?=(\s|\.)))", field_value, re.IGNORECASE)
        if matches:
            review["SourceTestRating"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("SourceTestRating", "")
        if field_value:
            matches = re.search("(\d\.\d(?=\s|\.))", field_value, re.IGNORECASE)
        if matches:
            review["SourceTestRating"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("SourceTestRating", "")
        if field_value:
            matches = re.search("(\d\.\d{2}(?=\s|\.))", field_value, re.IGNORECASE)
        if matches:
            review["SourceTestRating"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("SourceTestRating", "")
        if field_value:
            matches = re.search("(\d(?=\s|\.))", field_value, re.IGNORECASE)
        if matches:
            review["SourceTestRating"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("SourceTestRating", "")
        if field_value:
            matches = re.search("(\s)", field_value, re.IGNORECASE)
        if matches:
            review["SourceTestRating"] = matches.group(1)
                                    

        if review["TestDateText"]:
            
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(review["TestDateText"], "%d-%m-%Y", ["nl"])
                                    

        yield product


        
                            
        yield review
        
