# -*- coding: utf8 -*-
from datetime import datetime
import re

from scrapy.http import Request, HtmlResponse,FormRequest
from scrapy.selector import Selector

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.spiders.base_spiders.bazaarvoice_spider import BVNoSeleniumSpider
from alascrapy.lib.generic import get_full_url, date_format
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import CategoryItem, ProductItem, ReviewItem, ProductIdItem
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from alascrapy.lib.selenium_browser import SeleniumBrowser
import json

class Gamona_deSpider(AlaSpider):
    name = 'gamona_de'
    allowed_domains = ['gamona.de']
    start_urls = ['http://www.gamona.de/games/reviews.html']

    
    def parse(self, response):
        original_url = response.url
        url0='http://www.gamona.de/$invoke/games/reviews.html'
        for i in range(1,100):
            data0={"name":"more","arguments":[{"page":i}]}
            #r=FormRequest(url=url0,formdata=json.dumps(data0),callback=self.level_xhr)
            r = Request(url0, method='POST',body=json.dumps(data0),headers={'Content-Type': 'application/json'},callback=self.level_xhr)
            yield r
        product = response.meta.get("product", {})
        review = response.meta.get("review", {})
        
        url_xpath = "//li[@class='game']/a/@href"
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
    def level_xhr(self,response):
        #print 'enter level_xhr'
        t=response.body
        pattern = re.compile(r'(?<=href)(.*?)(?=data\-)')
        anses = pattern.findall(t)
        for ans in anses:
            url='http://www.gamona.de'+ans[3:-3]
            yield Request(url=url,callback=self.level_2)
    def level_2(self, response):
                                     
        original_url = response.url
        product = response.meta.get("product", {})
        review = response.meta.get("review", {})
        
        product_xpaths = { 
                
                
                "ProductName":"//span[@itemprop='name']/h1/a/text()",
                
                
                
                
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
                
                
                "ProductName":"//span[@itemprop='name']/h1/a/text()",
                
                
                
                "TestDateText":"//span[@class='date']/text()",
                
                
                
                
                "TestSummary":"//div[contains(@class,'articlebody')]/p[1]//text()",
                
                
                
                "Author":"//a[@rel='author']//span[@itemprop='name']//text()",
                
                
                "TestTitle":"//span[@itemprop='name']/h2/text()",
                
                
                
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
        field_value = review.get("TestDateText", "")
        if field_value:
            matches = re.search("(\d{2}\.\d{2}\.\d{4})", field_value, re.IGNORECASE)
        if matches:
            review["TestDateText"] = matches.group(1)
                                    

        if review["TestDateText"]:
            
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(review["TestDateText"], "%d.%B.%Y", ["en"])
                                    

        review["DBaseCategoryName"] = "PRO"
                                    

        review["SourceTestScale"] = "10"
                                    

        yield product

        in_another_page_xpath = "//p[@class='nextpage']/a/@href"
        pros_xpath = "//div[@class='box pro']/ul//text()"
        cons_xpath = "//div[@class='box contra']/ul//text()"
        rating_xpath = "//span[@class='award']/img/@alt"
        award_xpath = ""
        award_pic_xpath = ""
        
        test_verdict_xpath_1 = '//span[@class="content"]/h3/text()'
        
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

if __name__=='__main__':
    from scrapy.crawler import CrawlerProcess

    process = CrawlerProcess({})
    process.crawl(Gamona_deSpider)
    process.start()