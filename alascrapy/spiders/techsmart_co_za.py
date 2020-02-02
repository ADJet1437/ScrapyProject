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


class Techsmart_co_zaSpider(AlaSpider):
    name = 'techsmart_co_za'
    allowed_domains = ['techsmart.co.za']
    start_urls = ['http://techsmart.co.za/reviews']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        url_xpath = "//div[contains(@class,'pagination') and contains(@class,'right')]/a[1]/@href"
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
        urls_xpath = "//div[@class='article_list_item' or @class='feature_article']/a/@href"
        params_regex = {}
        urls = self.extract_list(response.xpath(urls_xpath))
        
        for single_url in urls:
            matches = None
            if "(^(?!.*((\/movies\/)|(\/beer\/))).*$)":
                matches = re.search("(^(?!.*((\/movies\/)|(\/beer\/))).*$)", single_url, re.IGNORECASE)
                if matches:
                    single_url = matches.group(0)
                else:
                    continue
            single_url = get_full_url(original_url, single_url)
            
            request = Request(single_url, callback=self.level_2)
            
             
            yield request
    
    def level_2(self, response):
                                     
        original_url = response.url
        
        category_leaf_xpath = "//div[@id='main_content']/descendant-or-self::div[contains(@class,'breadcrumb')][1]/a[last()]//text()"
        category_path_xpath = "//div[@id='main_content']/descendant-or-self::div[contains(@class,'breadcrumb')][1]/a//text()"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
                
                
                "ProductName":"//*[@itemprop='itemReviewed']//text()",
                
                
                
                "PicURL":"//article/descendant-or-self::img[1]/@src",
                
                
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
        if ocn == "" and ""[:2] != "//":
            product["OriginalCategoryName"] = ""
        review_xpaths = { 
                
                
                "ProductName":"//*[@itemprop='itemReviewed']//text()",
                
                
                
                "TestDateText":"//span[@itemprop='dtreviewed']//text()",
                
                
                "TestPros":"normalize-space(//div[contains(normalize-space(./span),'PROS')]/following-sibling::node()[string-length(normalize-space())>1 or normalize-space()='-'][1])",
                
                
                "TestCons":"normalize-space(//div[contains(normalize-space(./span),'CONS')]/following-sibling::node()[string-length(normalize-space())>1 or normalize-space()='-'][1])",
                
                
                "TestSummary":"//meta[@name='description']/@content",
                
                
                "TestVerdict":"//body/descendant-or-self::p[contains(.//strong,'verdict') or contains(.//strong,'get') or contains(.//strong,'buy') or contains(.//strong,'choice') or starts-with(.//strong,'Final') or contains(.//strong,'decision') or starts-with(translate(.//strong,' ',''),'Thebest') or starts-with(translate(.//strong,' ',''),'Summingup') or contains(translate(.//strong,' ',''),'bestyet')][last()]/following-sibling::p[string-length(normalize-space())>1][1]//text()[normalize-space()]",
                
                
                "Author":"//span[@itemprop='reviewer']//text()",
                
                
                "TestTitle":"//*[@itemprop='itemReviewed']//text()",
                
                
                
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
                                    

        if review["TestDateText"]:
            
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(review["TestDateText"], "%d %B %Y", ["en"])
                                    

        yield product


        
                            
        yield review
        
