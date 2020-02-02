# -*- coding: utf8 -*-
import re

from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format
from alascrapy.items import ProductItem, ReviewItem


class DigitalcameraworldSpider(AlaSpider):
    name = 'digitalcameraworld'
    allowed_domains = ['digitalcameraworld.com']
    start_urls = ['http://www.digitalcameraworld.com/category/reviews/']

    
    def parse(self, response):
                                     
        original_url = response.url
        url_xpath = "//a[@class='next page-numbers']/@href"
        single_url = self.extract(response.xpath(url_xpath))
        if single_url:
            single_url = get_full_url(original_url, single_url)
            matches = None
            if "":
                matches = re.search("", single_url, re.IGNORECASE)
            if matches:
                single_url = matches.group(0)
            
            request = Request(single_url, callback=self.parse)
             
            yield request
        containers_xpath = "//article"
        url_xpath = ".//header/h2/a/@href"
        params_regex = {}
        containers = response.xpath(containers_xpath)
        for container in containers:
            single_url = self.extract(container.xpath(url_xpath))
            single_url = get_full_url(response, single_url)
            request = Request(single_url, callback=self.level_2)
            
            extract_text = self.extract(container.xpath('.//small//p/a[not(contains(text(), "Reviews"))][1]//text()'))
            matches = None
            if extract_text:
                matches = re.search(params_regex["OriginalCategoryName"], extract_text, re.IGNORECASE)
            text_1 = ""
            if matches:
                text_1 = matches.group(1)
            request.meta["OriginalCategoryName"] = text_1
            
            yield request
    
    def level_2(self, response):
                                     
        original_url = response.url
        product_xpaths = { 
                
                
                
                
                "PicURL":"//meta[@property='og:image']/@content",
                
                
                            }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        try:
            product["OriginalCategoryName"] = category['category_path']
        except:
            pass
        review_xpaths = { 
                
                
                
                "SourceTestRating":"//p/strong[contains(text(), 'Overall Score')]/parent::p//text()",
                
                
                "TestDateText":"//span[@class='posted-at']//text()",
                
                
                
                
                "TestSummary":"//meta[@property='og:description']//@content",
                
                
                "TestVerdict":"//*[contains(text(), 'Verdict')]/following-sibling::p[1]//text()",
                
                
                "Author":"//a[@rel='author']//text()",
                
                
                "TestTitle":"//meta[@property='og:title']/@content",
                
                
                
                            }
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        try:
            review['ProductName'] = product['ProductName']
            review['source_internal_id'] = product['source_internal_id']
        except:
            pass
        if review and review['TestTitle']:
            title = review["TestTitle"].lower()
            if ":" in title:
                all_title_parts = title.split(":")
                for part in all_title_parts:
                    review["ProductName"] = part.replace("review", "") if 'review' in part else title.replace("review", "")
            else:
                review["ProductName"] = title.replace("review", "")
            
            review["ProductName"] = review["ProductName"].strip("-: ")
            product["ProductName"] = review["ProductName"]

        if review["TestDateText"]:
            
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(review["TestDateText"], "%B %d, %Y", ["en"])
                                    

        review["SourceTestScale"] = "5"
                                    

        matches = None
        if review["SourceTestRating"]:
            matches = re.search(".+: (\d.*\d*)/5", review["SourceTestRating"], re.IGNORECASE)
        if matches:
            review["SourceTestRating"] = matches.group(1)
                                    

        if "OriginalCategoryName" in ProductItem.fields:
            product["OriginalCategoryName"] = response.meta["OriginalCategoryName"]
        
        yield product

        
        if "OriginalCategoryName" in ReviewItem.fields:
            review["OriginalCategoryName"] = response.meta["OriginalCategoryName"]
        
        yield review
        
