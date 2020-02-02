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


class Frandroid_comSpider(AlaSpider):
    name = 'frandroid_com'
    allowed_domains = ['frandroid.com']
    start_urls = ['http://www.frandroid.com/test']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        url_xpath = "//div[starts-with(@class,'newer')]/a/@href"
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
        urls_xpath = "//div[contains(@class,'bloc-wrapper')]/a/@href"
        params_regex = {}
        urls = self.extract_list(response.xpath(urls_xpath))
        
        for single_url in urls:
            matches = None
            if "(\w.*(test).*)":
                matches = re.search("(\w.*(test).*)", single_url, re.IGNORECASE)
                if matches:
                    single_url = matches.group(0)
                else:
                    continue
            single_url = get_full_url(original_url, single_url)
            
            request = Request(single_url, callback=self.level_2)
            
             
            yield request
    
    def level_2(self, response):
                                     
        original_url = response.url
        
        category_leaf_xpath = "//div[@class='breadcrumb']/ul/li[position()=last()-2]/a/text() | //span[contains(@typeof,'Breadcrumb')]/*[last()]/text()"
        category_path_xpath = "//div[@class='breadcrumb']/ul/li[position()<last()-1]/a/text() | //span[contains(@typeof,'Breadcrumb')]//text()"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
                
                "source_internal_id": "//div[starts-with(@class,'bg-content')]/div/@data-single-post-id",
                
                
                "ProductName":"(//head/meta[@itemprop='itemreviewed']/@content | //h1[contains(@class,'title')]/text())[1]",
                
                
                
                "PicURL":"//meta[@property='og:image']/@content",
                
                
                "ProductManufacturer":"//*[starts-with(@class,'after-content')]//a[@class='brand']//text()"
                
                            }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['TestUrl'] = original_url
        picurl = product.get("PicURL", "")
        if picurl and picurl[:2] == "//":
            product["PicURL"] = "https:" + product["PicURL"]
        if picurl and picurl[:1] == "/":
            product["PicURL"] = get_full_url(original_url, picurl)
        manuf = product.get("ProductManufacturer", "")
        if manuf == "" and "//*[starts-with(@class,'after-content')]//a[@class='brand']//text()"[:2] != "//":
            product["ProductManufacturer"] = "//*[starts-with(@class,'after-content')]//a[@class='brand']//text()"
        try:
            product["OriginalCategoryName"] = category['category_path']
        except:
            pass
        ocn = product.get("OriginalCategoryName", "")
        if ocn == "" and ""[:2] != "//":
            product["OriginalCategoryName"] = ""
        review_xpaths = { 
                
                "source_internal_id": "//div[starts-with(@class,'bg-content')]/div/@data-single-post-id",
                
                
                "ProductName":"(//head/meta[@itemprop='itemreviewed']/@content | //h1[contains(@class,'title')]/text())[1]",
                
                
                "SourceTestRating":"(//span[contains(@class,'rate-frandroid')]/text() | //div[starts-with(@class,'global-grade')]/div[@class='grade']//descendant-or-self::span[last()]/text() | //div[starts-with(@class,'article-content')]//span[@class='rank-value' and not(./preceding::canvas[1]/@data-rankvalue='0')]/text())[1]",
                
                
                "TestDateText":"substring-before(//meta[contains(@property,'published_time')]/@content,'T')",
                
                
                "TestPros":"//ul[starts-with(@class,'good-bad-container')]/li[starts-with(@class,'good')]/ul/li/text()",
                
                
                "TestCons":"//ul[starts-with(@class,'good-bad-container')]/li[starts-with(@class,'bad')]/ul/li/text()",
                
                
                "TestSummary":"//div[@itemprop='reviewBody' or @itemprop='articleBody']/p[string-length(normalize-space())>1][1]//text()",
                
                
                "TestVerdict":"//div[@class='conclusion']/span[@itemprop='description']/descendant::node()[string-length(normalize-space())>1][1] | //span[@id='conclusion']/following::p[1]//text()",
                
                
                "Author":"(//meta[@name='author']/@content | //span[@class='author']//text())[1]",
                
                
                "TestTitle":"//h1[contains(@class,'title')]/text()",
                
                
                
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

        id_value = self.extract(response.xpath("(//a[@class='buy-button']/span[last()]//text() | //div[starts-with(@class,'product-info')]//div[@class='offers']/a[1]/span[@class='offer']/span[last()]/text())[1]"))
        if id_value:
            product_id = self.product_id(product)
            product_id['ID_kind'] = "price"
            product_id['ID_value'] = id_value
            yield product_id
        

        review["DBaseCategoryName"] = "PRO"
                                    

        review["SourceTestScale"] = "10"
                                    

        matches = None
        field_value = review.get("SourceTestRating", "")
        if field_value:
            matches = re.search("(\d+(?=\/))", field_value, re.IGNORECASE)
        if matches:
            review["SourceTestRating"] = matches.group(1)
                                    

        yield product


        
                            
        yield review
        
