# -*- coding: utf8 -*-
import re

from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format
from alascrapy.items import CategoryItem, ReviewItem


class DellSpider(AlaSpider):
    name = 'dell'
    allowed_domains = ['dell.com']
    start_urls = ['http://www.dell.com/']

    
    def parse(self, response):
                                     
        original_url = response.url
        urls_xpath = "//div[contains(@class,'main-nav-section')][1]/ul[@class='tier1']/li[1]//a[@href!='#']/@href"
        urls = self.extract_list(response.xpath(urls_xpath))
        for single_url in urls:
            single_url = get_full_url(original_url, single_url)
            matches = None
            if "":
                matches = re.search("", single_url, re.IGNORECASE)
            if matches:
                single_url = matches.group(0)
            
            request = Request(single_url, callback=self.level_2)
             
            yield request
    
    def level_2(self, response):
                                     
        original_url = response.url
        urls_xpath = "//a[@class='title'][@href!='#']/@href"
        urls = self.extract_list(response.xpath(urls_xpath))
        for single_url in urls:
            single_url = get_full_url(original_url, single_url)
            matches = None
            if "":
                matches = re.search("", single_url, re.IGNORECASE)
            if matches:
                single_url = matches.group(0)
            
            request = Request(single_url, callback=self.level_3)
             
            yield request
    
    def level_3(self, response):
                                     
        original_url = response.url
        category_leaf_xpath = "//div[@class='breadCrumb']//li[a][last()]/a/text()"
        category_path_xpath = "//div[@class='breadCrumb']//a/text()"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
                
                
                "ProductName":"//*[@id='mastheadPageTitle']/text()",
                
                
                
                "PicURL":"//meta[@property='og:image']/@content",
                
                
                "ProductManufacturer":"//a[@class='mhLogo']/img/@alt"
                
                            }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        try:
            product["OriginalCategoryName"] = category['category_path']
        except:
            pass

        yield product

        url_xpath = "//noscript/iframe/@src"
        single_url = self.extract(response.xpath(url_xpath))
        if single_url:
            single_url = get_full_url(original_url, single_url)
            matches = None
            if "":
                matches = re.search("", single_url, re.IGNORECASE)
            if matches:
                single_url = matches.group(0)
            
            request = Request(single_url, callback=self.level_4)
            
            request.meta["ProductName"] = product["ProductName"]
            
            yield request
    
    def level_4(self, response):
                                     
        original_url = response.url

        button_next_url = self.extract(response.xpath("//span[@class='BVRRPageLink BVRRNextPage']/a/@href"))
        if button_next_url:
            button_next_url = get_full_url(original_url, button_next_url)
            request = Request(button_next_url, callback=self.level_4)
            
            request.meta["ProductName"] = response.meta["ProductName"]
            
            yield request

        containers_xpath = "//div[@id='BVSubmissionPopupContainer']"
        containers = response.xpath(containers_xpath)
        for review_container in containers:
            review = ReviewItem()
            
            
            
            review['SourceTestRating'] = self.extract(review_container.xpath(".//div[@class='BVRRReviewDisplayStyle3Summary']//div[@class='BVRROverallRatingContainer']//img/@alt"))
            
            
            review['TestDateText'] = self.extract(review_container.xpath(".//span[@class='BVRRValue BVRRReviewDate']//text()"))
            
            
            review['TestPros'] = self.extract(review_container.xpath(".//span[@class='BVRRLabel BVRRTagsPrefix'][contains(text(),'Pros:')]/following-sibling::span//text()"))
            
            
            review['TestCons'] = self.extract(review_container.xpath(".//span[@class='BVRRLabel BVRRTagsPrefix'][contains(text(),'Cons:')]/following-sibling::span//text()"))
            
            
            review['TestSummary'] = self.extract(review_container.xpath(".//span[@class='BVRRReviewText']//text()"))
            
            
            
            review['Author'] = self.extract(review_container.xpath(".//span[@class='BVRRNickname']//text()"))
            
            
            review['TestTitle'] = self.extract(review_container.xpath(".//span[@class='BVRRValue BVRRReviewTitle']//text()"))
            
            
            review['award'] = self.extract(review_container.xpath("//div[@class='iconographyContainer']//img/@alt"))
            
            
            review['AwardPic'] = self.extract(review_container.xpath("//div[@class='iconographyContainer']//img/@src"))
            
            review['TestUrl'] = original_url
            try:
                review['ProductName'] = product['ProductName']
                review['source_internal_id'] = product['source_internal_id']
            except:
                pass
        

           

            
            review["DBaseCategoryName"] = "USER"
            
                                     
            
            if review["TestDateText"]:
                
                review["TestDateText"] = date_format(review["TestDateText"], "%B %d, %Y", ["en"])
            
                                    

            
            review["SourceTestScale"] = "5"
             
                                    

            
            matches = None
            if review["SourceTestRating"]:
                matches = re.search("(\d.*\d*) / 5", review["SourceTestRating"], re.IGNORECASE)
            if matches:
                review["SourceTestRating"] = matches.group(1)
            
                                    

        
            
                            
            if "ProductName" in ReviewItem.fields:
                review["ProductName"] = response.meta["ProductName"]
                            
            yield review
            
        
