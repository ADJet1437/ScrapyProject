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
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
class Gameinformer_comSpider(AlaSpider):
    name = 'gameinformer_com'
    allowed_domains = ['gameinformer.com']
    start_urls = ['http://www.gameinformer.com/reviews.aspx']
    custom_settings = {'COOKIES_ENABLED':True}
    
    def parse(self, response):
        original_url = response.url
        url='http://www.gameinformer.com/reviews.aspx'
        data = {
            "ctl00$content$ctl00$ctl00": "custom:id=fragment-3821&renderFromCurrent=True&callback_control_id=ctl00%24content%24ctl00%24fragment_3821%24ctl01%24ctl00%24delayer&callback_argument=All%3AAll%3AAll%3A",
            "__VIEWSTATE": "/wEPDwUJNDIzNjI5OTU0ZBgBBR5fX0NvbnRyb2xzUmVxdWlyZVBvc3RCYWNrS2V5X18WAQU4Y3RsMDAkY29udGVudCRjdGwwMCRmcmFnbWVudF8zODIxJGN0bDAxJGN0bDAwJFNlYXJjaFRleHStEBYojyPjr0eBrsSB+bfmPrp3RA==",
            "__VIEWSTATEGENERATOR": "3F643096",
            "ctl00$content$ctl00$fragment_3821$ctl01$ctl00$SearchText": "find a review"}
        s0="custom:id=fragment-3821&renderFromCurrent=True&callback_control_id=ctl00%24content%24ctl00%24fragment_3821%24ctl01%24ctl00%24delayer&callback_argument=All%3AAll%3AAll%3A"
        s = response.headers.getlist('Set-Cookie')
        s = ';'.join(s)
        cookieset = dict()
        for c in s.split(';'):
            index = c.find('=')
            if index != -1:
                cookieset[c[:index]] = c[index + 1:]
        for i in range(1,100):
            print i,'='*30
            data["ctl00$content$ctl00$ctl00"]=s0+str(i)
            r=FormRequest(url,formdata=data,cookies=cookieset,callback=self.level_xhr)
            yield r

    def level_xhr(self,response):
        print 'enter level_xhr','='*30
        f = response.body
        #print f
        parttern = re.compile(r'(?<=a class=\"internal-link view-post\" href\=\")(.*?)(?=\.aspx)')

        anses = parttern.findall(f)
        s = set()
        parttern2 = re.compile(r'(\/\d{4}\/\d{2}\/\d{2})')
        for ans in anses:
            # print ans
            is_review = parttern2.findall(ans)
            if len(is_review):
                s.add(ans)
        for ss in s:
            url2="http://www.gameinformer.com" + ss + ".aspx"
            yield Request(url2,callback=self.level_2)

    def level_2(self, response):
        print 'enter Level 2','='*30
        original_url = response.url
        product = response.meta.get("product", {})
        review = response.meta.get("review", {})
        
        product_xpaths = { 
                
                
                "ProductName":"//h1[@class='game-name']/text()[normalize-space()]|//h1[@class='sku-name']//text()",
                
                
                
                
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
                
                
                "ProductName":"//h1[@class='game-name']/text()[normalize-space()]",
                
                
                "SourceTestRating":"(//div[@class='sku-rating-summary']/span/text())[1]",
                
                
                "TestDateText":"//meta[@property='og:url']/@content",
                
                
                
                
                "TestSummary":"//div[@id='divRenderBody']/p[2]//text()[normalize-space()]",
                
                
                "TestVerdict":"//div[@class='extra-rating-info']/ul//text()[normalize-space()]",
                
                
                "Author":"//div[@class='post-author']/span[1]/a/text()[normalize-space()]",
                
                
                "TestTitle":"//h1[@class='game-name']/text()[normalize-space()]",
                
                
                
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
            matches = re.search("(\d{4}\/\d{2}\/\d{2})", field_value, re.IGNORECASE)
        if matches:
            review["TestDateText"] = matches.group(1)

        review["SourceTestScale"] = "10"
        if review["TestDateText"]:
            
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(review["TestDateText"], "%Y/%B/%d", ["en"])
                                    

        review["DBaseCategoryName"] = "PRO"
                                    

        yield product


        
                            
        yield review
        
