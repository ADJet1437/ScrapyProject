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


class Oxgadgets_comSpider(AlaSpider):
    name = 'oxgadgets_com'
    allowed_domains = ['oxgadgets.com']
    start_urls = ['http://www.oxgadgets.com/category/reviews']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        urls_xpath = "//h2[@class='entry-title']/a/@href"
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
        url_xpath = "//nav[contains(@class,'entry-nav')]//li[contains(@class,'right')]/a/@href"
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
        
        category_leaf_xpath = "//p[@class='entry-category']/a[last()]//text()"
        category_path_xpath = "//p[@class='entry-category']/a//text()"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
                
                
                "ProductName":"(//span[@itemprop='name']/h2[@itemprop='name'] | //h1[@class='entry-title'])[(position()>count(//span[@itemprop='name']/h2[@itemprop='name']) and count(//span[@itemprop='name']/h2[@itemprop='name'])>0) or count(//span[@itemprop='name']/h2[@itemprop='name'])=0]//text()",
                
                
                "OriginalCategoryName":"//p[@class='entry-category']/a//text()",
                
                
                "PicURL":"(//div[@class='content-part']//p[.//img][1]//img | //li[@class='entry-date'][count(//div[@class='rev-wu-image'])=0]/following::img[1])[1]/@src",
                
                
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
        if ocn == "" and "//p[@class='entry-category']/a//text()"[:2] != "//":
            product["OriginalCategoryName"] = "//p[@class='entry-category']/a//text()"
        review_xpaths = { 
                
                
                "ProductName":"(//span[@itemprop='name']/h2[@itemprop='name'] | //h1[@class='entry-title'])[(position()>count(//span[@itemprop='name']/h2[@itemprop='name']) and count(//span[@itemprop='name']/h2[@itemprop='name'])>0) or count(//span[@itemprop='name']/h2[@itemprop='name'])=0]//text()",
                
                
                "SourceTestRating":"//span[@itemprop='ratingValue']//text()",
                
                
                "TestDateText":"//li[@class='entry-date']//text()",
                
                
                "TestPros":"//h2[text()='Pros']/following::ul[1]//text()",
                
                
                "TestCons":"//h2[text()='Cons']/following::ul[1]//text()",
                
                
                "TestSummary":"//meta[@property='og:description']/@content",
                
                
                "TestVerdict":"//strong[starts-with(text(),'Verdict')]/following::p[string-length(text())>5][1]//text()",
                
                
                "Author":"//li[@class='entry-author']/a//text()",
                
                
                "TestTitle":"//h1[@class='entry-title']//text()",
                
                
                
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

        review["SourceTestScale"] = "10"
                                    

        if review["TestDateText"]:
            
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(review["TestDateText"], "%B %d, %Y", ["en"])
                                    
        if review and review['TestTitle']:
            title = review["TestTitle"].lower()
            if ":" in title:
                all_title_parts = title.split(":")
                for part in all_title_parts:
                    review["ProductName"] = part.replace("review", "") if 'review' in part else title.replace("review", "")
            else:
                review["ProductName"] = title.replace("review", "")
            
            review["ProductName"] = review["ProductName"].replace("Review:".lower(), "")
            
            review["ProductName"] = review["ProductName"].strip("-: ")
            product["ProductName"] = review["ProductName"]

        yield product


        review["DBaseCategoryName"] = "PRO"
                                    

        
                            
        yield review
        
