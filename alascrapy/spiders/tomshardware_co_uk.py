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


class Tomshardware_co_ukSpider(AlaSpider):
    name = 'tomshardware_co_uk'
    allowed_domains = ['tomshardware.co.uk']
    start_urls = ['http://www.tomshardware.co.uk/articles/review/']

    
    def parse(self, response):
                                     
        original_url = response.url
        product = response.meta.get("product", {})
        review = response.meta.get("review", {})
        
        url_xpath = "//ul[@class='pager']/li/ul/li[last()]/a/@href"
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
        urls_xpath = "//li[@class='listing-item']//a[@itemprop='image']/@href"
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
        
        category_leaf_xpath = "(//ul[@class='breadcrumb']//span[@itemprop='name']/text())[1]"
        category_path_xpath = "//ul[@class='breadcrumb']//span[@itemprop='name']/text()"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
                
                "source_internal_id": "//link[@rel='canonical']/@href",
                
                
                "ProductName":"//h1[@itemprop='headline']/text()",
                
                
                "OriginalCategoryName":"(//ul[@class='breadcrumb']//span[@itemprop='name']/text())[1]",
                
                
                
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
        if ocn == "" and "(//ul[@class='breadcrumb']//span[@itemprop='name']/text())[1]"[:2] != "//":
            product["OriginalCategoryName"] = "(//ul[@class='breadcrumb']//span[@itemprop='name']/text())[1]"
        review_xpaths = { 
                
                "source_internal_id": "//link[@rel='canonical']/@href",
                
                
                "ProductName":"//h1[@itemprop='headline']/text()",
                
                
                
                "TestDateText":"//header[@class='headline']//time/text()",
                
                
                "TestSummary":"//div[@class='content']/p[1]//text()[normalize-space()]",
                
                
                
                "Author":"//span[@itemprop='author']/text()",
                
                
                "TestTitle":"//h1[@itemprop='headline']/text()",
                
                
                
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
            matches = re.search("review-(\d+)", field_value, re.IGNORECASE)
        if matches:
            product["source_internal_id"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("source_internal_id", "")
        if field_value:
            matches = re.search("review-(\d+)", field_value, re.IGNORECASE)
        if matches:
            review["source_internal_id"] = matches.group(1)
                                    

        matches = None
        field_value = product.get("ProductName", "")
        if field_value:
            matches = re.search("(.+)(?=\sReview)", field_value, re.IGNORECASE)
        if matches:
            product["ProductName"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("ProductName", "")
        if field_value:
            matches = re.search("(.+)(?=\sReview)", field_value, re.IGNORECASE)
        if matches:
            review["ProductName"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("TestDateText", "")
        if field_value:
            matches = re.search("(.+)(?=\sat)", field_value, re.IGNORECASE)
        if matches:
            review["TestDateText"] = matches.group(1)
                                    

        if review["TestDateText"]:
            
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(review["TestDateText"], "%B %d, %Y", ["en"])
                                    

        review["DBaseCategoryName"] = "PRO"
                                    

        yield product

        in_another_page_xpath = "//div[@class='summary-listing']/ol/li[last()]/a/@href"
        pros_xpath = "//div[@class='p-g']/div[2]/ul/li/text()"
        cons_xpath = "//div[@class='p-g']/div[3]/ul/li/text()"
        rating_xpath = ""
        award_xpath = ""
        award_pic_xpath = ""
        
        test_verdict_xpath_1 = "//div[@class='p-g']/div[last()]/p/text()"
        
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
