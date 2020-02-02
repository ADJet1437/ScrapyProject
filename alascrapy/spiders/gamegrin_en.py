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


class Gamegrin_enSpider(AlaSpider):
    name = 'gamegrin_en'
    allowed_domains = ['gamegrin.com']
    start_urls = ['http://www.gamegrin.com/reviews/']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        urls_xpath = "//div[@class='article__image']/a[img]/@href"
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
        url_xpath = "//div[@class='pagination']/a[text()='Next']/@href"
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
        
        product_xpaths = { 
                
                
                "ProductName":"//h1[@class='splitter']/span[@itemprop='title']/text()",
                
                
                "OriginalCategoryName":"game",
                
                
                "PicURL":"//meta[@name='twitter:image']/@content",
                
                
                "ProductManufacturer":"//td[text()='Publisher']/following-sibling::td[1]/*/text()"
                
                            }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['TestUrl'] = original_url
        picurl = product.get("PicURL", "")
        if picurl and picurl[:2] == "//":
            product["PicURL"] = "https:" + product["PicURL"]
        if picurl and picurl[:1] == "/":
            product["PicURL"] = get_full_url(original_url, picurl)
        manuf = product.get("ProductManufacturer", "")
        if manuf == "" and "//td[text()='Publisher']/following-sibling::td[1]/*/text()"[:2] != "//":
            product["ProductManufacturer"] = "//td[text()='Publisher']/following-sibling::td[1]/*/text()"
        try:
            product["OriginalCategoryName"] = category['category_path']
        except:
            pass
        ocn = product.get("OriginalCategoryName", "")
        if ocn == "" and "game"[:2] != "//":
            product["OriginalCategoryName"] = "game"

        matches = None
        field_value = product.get("ProductName", "")
        if field_value:
            matches = re.search("(.*)Review", field_value, re.IGNORECASE)
        if matches:
            product["ProductName"] = matches.group(1)
                                    

        yield product

        review_xpaths = { 
                
                
                "ProductName":"//h1[@class='splitter']/span[@itemprop='title']/text()",
                
                
                "SourceTestRating":"//span[@itemprop='ratingValue']/text()",
                
                
                "TestDateText":"//meta[@itemprop='datePublished']/@content",
                
                
                
                
                "TestSummary":"//meta[@property='og:description']/@content",
                
                
                "TestVerdict":"//p[@itemprop='reviewBody']/text()",
                
                
                "Author":"//div[contains(@class,'breadcrumbs')]/span/a/text()",
                
                
                "TestTitle":"//h1[@class='splitter']/span[@itemprop='title']/text()",
                
                
                
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
                                    

        
                            
        yield review
        
