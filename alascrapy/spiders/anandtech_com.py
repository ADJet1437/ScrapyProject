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


class Anandtech_comSpider(AlaSpider):
    name = 'anandtech_com'
    allowed_domains = ['anandtech.com']
    start_urls = ['http://www.anandtech.com/']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        url_xpath = "//a[@rel='next']/@href"
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
        urls_xpath = "//section/div[starts-with(@class,'cont_box1') or @class='featured_banner']/div[1]/a[1]/@href"
        params_regex = {}
        urls = self.extract_list(response.xpath(urls_xpath))
        
        for single_url in urls:
            matches = None
            if "(.*[^p](?=review))":
                matches = re.search("(.*[^p](?=review))", single_url, re.IGNORECASE)
                if matches:
                    single_url = matches.group(0)
                else:
                    continue
            single_url = get_full_url(original_url, single_url)
            
            request = Request(single_url, callback=self.level_2)
            
             
            yield request
    
    def level_2(self, response):
                                     
        original_url = response.url
        
        category_leaf_xpath = "//nav[@class='breadcrumb']//li[last()]/a/text()"
        category_path_xpath = "//nav[@class='breadcrumb']//li/a/text()"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
                
                "source_internal_id": "//link[@rel='shortlink']/@href",
                
                
                "ProductName":"//div[@class='blog_top_left']/a/h1/text()",
                
                
                
                "PicURL":"(//div[@class='articleContent']//img/@src)[1]",
                
                
                            }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['TestUrl'] = original_url
        manuf = product.get("ProductManufacturer", "")
        if manuf == "" and ""[:2] != "//":
            product["ProductManufacturer"] = ""
        try:
            product["OriginalCategoryName"] = category['category_path']
        except:
            pass
        ocn = product.get("OriginalCategoryName", "")
        if ocn == "" and ""[:2] != "//":
            product["OriginalCategoryName"] = ""
        review_xpaths = { 
                
                "source_internal_id": "//link[@rel='shortlink']/@href",
                
                
                "ProductName":"//div[@class='blog_top_left']/a/h1/text()",
                
                
                
                "TestDateText":"//div[starts-with(@class,'blog_top')]/span/em",
                
                
                
                
                "TestSummary":"//div[contains(@class,'Content')]/p[string-length(normalize-space())>1][not(strong)][1]//text()",
                
                
                
                "Author":"//meta[@name='author']/@content",
                
                
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
                                    

        matches = None
        field_value = product.get("source_internal_id", "")
        if field_value:
            matches = re.search("((?<=\/show\/)\d.*\d)", field_value, re.IGNORECASE)
        if matches:
            product["source_internal_id"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("source_internal_id", "")
        if field_value:
            matches = re.search("((?<=\/show\/)\d.*\d)", field_value, re.IGNORECASE)
        if matches:
            review["source_internal_id"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("TestDateText", "")
        if field_value:
            matches = re.search("((?<=on\s).*(?=\s\d))", field_value, re.IGNORECASE)
        if matches:
            review["TestDateText"] = matches.group(1)
                                    

        matches = None
        field_value = product.get("ProductName", "")
        if field_value:
            matches = re.search("(\w.*(?=\sreview))", field_value, re.IGNORECASE)
        if matches:
            product["ProductName"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("ProductName", "")
        if field_value:
            matches = re.search("(\w.*(?=\sreview))", field_value, re.IGNORECASE)
        if matches:
            review["ProductName"] = matches.group(1)
                                    

        matches = None
        field_value = product.get("ProductName", "")
        if field_value:
            matches = re.search("((?<=the\s).*)", field_value, re.IGNORECASE)
        if matches:
            product["ProductName"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("ProductName", "")
        if field_value:
            matches = re.search("((?<=the\s).*)", field_value, re.IGNORECASE)
        if matches:
            review["ProductName"] = matches.group(1)
                                    

        if review["TestDateText"]:
            
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(review["TestDateText"], "%B %d, %Y", ["en"])
                                    
        in_another_page_xpath = "//select[@name='ContentPagesListTop']/option[last()]/@value"
        pros_xpath = ""
        cons_xpath = ""
        rating_xpath = ""
        award_xpath = ""
        award_pic_xpath = ""
        
        test_verdict_xpath_1 = '//h2[(contains(.,"Final") and contains(.,"Words")) or contains(.,"Conclusion") or contains(.,"Conclud")]/following::p[string-length(normalize-space())>1 and not(./preceding::h3/preceding::h2) and not(./preceding::div[contains(@class,"ShoppingWidget")]) and not(@align)][starts-with(.,"Overall") or starts-with(.,"Last") or contains(.,"summary") or position()=last()][1]//text()'
        
        review["TestVerdict"] = None
        in_another_page_url = None
        if in_another_page_xpath:
            in_another_page_url = self.extract(response.xpath(in_another_page_xpath))
        if in_another_page_url:
            in_another_page_url = get_full_url(response, in_another_page_url)
            request = Request(in_another_page_url, callback=self.parse_fields_page)
            request.meta['review'] = review
            
            request.meta['test_verdict_xpath_1'] = test_verdict_xpath_1
            
            request.meta['pros_xpath'] = pros_xpath
            request.meta['cons_xpath'] = cons_xpath
            request.meta['rating_xpath'] = rating_xpath
            request.meta['award_xpath'] = award_xpath
            request.meta['award_pic_xpath'] = award_pic_xpath
            yield request
        else:
            
            if not review["TestVerdict"]:
                review["TestVerdict"] = self.extract(response.xpath(test_verdict_xpath_1))
            
            yield review

        yield product

    
    def parse_fields_page(self, response):
        review = response.meta['review']
        
        test_verdict_xpath_1 = response.meta['test_verdict_xpath_1']
        
        
        if not review["TestVerdict"]:
            review["TestVerdict"] = self.extract(response.xpath(test_verdict_xpath_1))
        
        pros_xpath = response.meta['pros_xpath']
        cons_xpath = response.meta['cons_xpath']
        rating_xpath = response.meta['rating_xpath']
        award_xpath = response.meta['award_xpath']
        award_pic_xpath = response.meta['award_pic_xpath']
        if pros_xpath:
            review["TestPros"] = self.extract_all(response.xpath(pros_xpath), ' ; ')
        if cons_xpath:
            review["TestCons"] = self.extract_all(response.xpath(cons_xpath), ' ; ')
        if rating_xpath:
            review['SourceTestRating'] = self.extract(response.xpath(rating_xpath), '%')
        if award_xpath:
            review['award'] = self.extract(response.xpath(award_xpath))
        if award_pic_xpath:
            review['AwardPic'] = self.extract(response.xpath(award_pic_xpath))
        yield review
