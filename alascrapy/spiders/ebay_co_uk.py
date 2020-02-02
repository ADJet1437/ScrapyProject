# -*- coding: utf8 -*-
import re

from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format
from alascrapy.items import CategoryItem, ReviewItem


class Ebay_co_ukSpider(AlaSpider):
    name = 'ebay_co_uk'
    allowed_domains = ['ebay.co.uk']
    start_urls = ['http://www.ebay.co.uk/rpp/electronics']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        urls_xpath = "//li[@data-node-id='0']/ul/li/a[contains(@href, 'rpp')]/@href"
        urls = self.extract_list(response.xpath(urls_xpath))
        for single_url in urls:
            matches = None
            if "":
                matches = re.search("", single_url, re.IGNORECASE)
            if matches:
                single_url = matches.group(0)
            single_url = get_full_url(original_url, single_url)
            
            request = Request(single_url, callback=self.level_2)
             
            yield request
    
    def level_2(self, response):
                                     
        original_url = response.url
        
        urls_xpath = "//li[@data-node-id='0']/ul/li/a[contains(@href, 'sch')]/@href"
        urls = self.extract_list(response.xpath(urls_xpath))
        for single_url in urls:
            matches = None
            if "":
                matches = re.search("", single_url, re.IGNORECASE)
            if matches:
                single_url = matches.group(0)
            single_url = get_full_url(original_url, single_url)
            
            request = Request(single_url, callback=self.level_3)
             
            yield request
    
    def level_3(self, response):
                                     
        original_url = response.url
        
        url_xpath = "//a[@class='gspr next']/@href"
        single_url = self.extract(response.xpath(url_xpath))
        if single_url:
            matches = None
            if "":
                matches = re.search("", single_url, re.IGNORECASE)
            if matches:
                single_url = matches.group(0)
            single_url = get_full_url(original_url, single_url)
            
            request = Request(single_url, callback=self.level_3)
            
            yield request
        urls_xpath = "//div[@class='mimg itmcd img']//a[@class='vip']/@href"
        urls = self.extract_list(response.xpath(urls_xpath))
        for single_url in urls:
            matches = None
            if "":
                matches = re.search("", single_url, re.IGNORECASE)
            if matches:
                single_url = matches.group(0)
            single_url = get_full_url(original_url, single_url)
            
            request = Request(single_url, callback=self.level_4)
             
            yield request
    
    def level_4(self, response):
                                     
        original_url = response.url
        
        category_leaf_xpath = "//li[@itemprop='itemListElement'][last()]//text()"
        category_path_xpath = "//li[@itemprop='itemListElement']//text()"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
                
                
                "ProductName":"//h1[@itemprop='name']/text()",
                
                
                
                "PicURL":"//img[@itemprop='image']/@src",
                
                
                            }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['TestUrl'] = original_url
        try:
            product["OriginalCategoryName"] = category['category_path']
        except:
            pass

        id_value = self.extract(response.xpath("//td[contains(text(), 'MPN')]/following-sibling::td[1]/span/text()"))
        if id_value:
            product_id = self.product_id(product)
            product_id['ID_kind'] = "mpn"
            product_id['ID_value'] = id_value
            yield product_id
        

        id_value = self.extract(response.xpath("//td[contains(text(), 'EAN')]/following-sibling::td[1]/span/text()"))
        if id_value:
            product_id = self.product_id(product)
            product_id['ID_kind'] = "ean"
            product_id['ID_value'] = id_value
            yield product_id
        

        yield product

        url_xpath = "//div[@id='rwid']//a[@class='btn btn-ter right']/@href"
        single_url = self.extract(response.xpath(url_xpath))
        if single_url:
            matches = None
            if "":
                matches = re.search("", single_url, re.IGNORECASE)
            if matches:
                single_url = matches.group(0)
            single_url = get_full_url(original_url, single_url)
            
            request = Request(single_url, callback=self.level_5)
            
            yield request
    
    def level_5(self, response):
                                     
        original_url = response.url
        

        button_next_url = self.extract(response.xpath("//a[@rel='next']/@href"))
        if button_next_url:
            button_next_url = get_full_url(original_url, button_next_url)
            request = Request(button_next_url, callback=self.level_5)
            
            yield request

        containers_xpath = "//div[@itemprop='review']"
        containers = response.xpath(containers_xpath)
        for review_container in containers:
            review = ReviewItem()
            
            
            review['ProductName'] = self.extract(review_container.xpath("//h1[@itemprop='name']/a/text()"))
            
            
            review['SourceTestRating'] = self.extract(review_container.xpath(".//span[@class='star-rating']/@aria-label"))
            
            
            review['TestDateText'] = self.extract(review_container.xpath(".//span[@class='review-item-date']/text()"))
            
            
            
            
            review['TestSummary'] = self.extract(review_container.xpath(".//p[@itemprop='reviewBody']//text()"))
            
            
            
            review['Author'] = self.extract(review_container.xpath(".//a[@class='review-item-author']/text()"))
            
            
            review['TestTitle'] = self.extract(review_container.xpath(".//p[@itemprop='name']//text()"))
            
            
            
            review['TestUrl'] = original_url
            try:
                review['ProductName'] = product['ProductName']
                review['source_internal_id'] = product['source_internal_id']
            except:
                pass
        

           

            
            review["DBaseCategoryName"] = "USER"
            
                                     
            
            if review["TestDateText"]:
                
                review["TestDateText"] = date_format(review["TestDateText"], "%d %b, %Y", ["en"])
            
                                    

            
            review["SourceTestScale"] = "5"
             
                                    

            
            matches = None
            if review["SourceTestRating"]:
                matches = re.search("(.+) stars", review["SourceTestRating"], re.IGNORECASE)
            if matches:
                review["SourceTestRating"] = matches.group(1)
            
                                    

        
            
                            
            yield review
            
        
