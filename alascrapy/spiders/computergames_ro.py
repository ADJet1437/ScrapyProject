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


class Computergames_roSpider(AlaSpider):
    name = 'computergames_ro'
    allowed_domains = ['computergames.ro']
    start_urls = ['http://computergames.ro/review/page/2/','http://computergames.ro/review/']

    
    def parse(self, response):
                                     
        original_url = response.url
        product = response.meta.get("product", {})
        review = response.meta.get("review", {})
        
        url_xpath = "//div[@class='navigation']//div[@class='next-posts']/a/@href"
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
        urls_xpath = "//article[@class='postlist']/a/@href"
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
        
        product_xpaths = { 
                
                "source_internal_id": "//div[@class='photo']//img/@pagespeed_url_hash",
                
                
                "ProductName":"//div[@itemprop='review']//span[@itemprop='name']/text()",
                
                
                "OriginalCategoryName":"game",
                
                
                "PicURL":"//div[@class='photo']//img/@src",
                
                
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
        if ocn == "" and "game"[:2] != "//":
            product["OriginalCategoryName"] = "game"
        review_xpaths = { 
                
                "source_internal_id": "//div[@class='photo']//img/@pagespeed_url_hash",
                
                
                "ProductName":"//div[@itemprop='review']//span[@itemprop='name']/text()",
                
                
                "SourceTestRating":"//span[@itemprop='reviewRating']//span[@class='reviewscore']//text()",
                
                
                "TestDateText":"//footer[@class='meta']//time/text()",
                
                
                "TestPros":"//div[@class='result']/ul[1]/li/text()",
                
                
                "TestCons":"//div[@class='result']/ul[2]/li/text()",
                
                
                "TestSummary":"//div[@class='entry']/descendant-or-self::node()[name()='p' or not(name())][string-length(normalize-space())>1][1]/text()",
                
                
                "TestVerdict":"(//div[@class='entry']//p[contains(.,'Concluzii')]/following::p)[1]/text()|(//div[@class='entry' and not(//div[@class='entry']//p[contains(.,'Concluzii')])]/p[string-length(.)>2])[last()]/text()",
                
                
                "Author":"//footer[@class='meta']//span[@class='fn']/text()",
                
                
                "TestTitle":"//div[@itemprop='review']//span[@itemprop='name']/text()",
                
                
                
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

        review["SourceTestScale"] = "100"
                                    

        matches = None
        field_value = product.get("Productname", "")
        if field_value:
            matches = re.search("(.*(?=\sReview))", field_value, re.IGNORECASE)
        if matches:
            product["Productname"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("ProductName", "")
        if field_value:
            matches = re.search("(.*(?=\sReview))", field_value, re.IGNORECASE)
        if matches:
            review["ProductName"] = matches.group(1)
                                    

        if review["TestDateText"]:
            
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(review["TestDateText"], "%d %B %Y", ["ro"])
                                    

        review["DBaseCategoryName"] = "PRO"
                                    

        yield product

        in_another_page_xpath = "//div[@class='pages']//a[last()]/@href"
        pros_xpath = ""
        cons_xpath = ""
        rating_xpath = ""
        award_xpath = ""
        award_pic_xpath = ""
        
        test_verdict_xpath_1 = '(//div[@class="entry"]//p[contains(.,"Concluzii")]/following::p)[1]/text()|(//div[@class="entry" and not(//div[@class="entry"]//p[contains(.,"Concluzii")])]/p[string-length(.)>2])[last()]/text()'
        
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
