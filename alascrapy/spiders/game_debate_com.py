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
import requests
import json
import time
class Game_debate_comSpider(AlaSpider):
    name = 'game_debate_com'
    allowed_domains = ['game-debate.com']
    start_urls = ['http://www.game-debate.com/articles/']
    custom_settings = {'COOKIES_ENABLED': True}
    
    def parse(self, response):
        original_url = response.url
        url1 = "http://www.game-debate.com/articles/a_menuTable.php?sEcho="
        url2 = "&iColumns=4&sColumns=&iDisplayStart="
        url3 = "&iDisplayLength=11&mDataProp_0=a_title&mDataProp_1=visualName&mDataProp_2=m_username&mDataProp_3=a_date&sSearch=&bRegex=false&sSearch_0=&bRegex_0=false&bSearchable_0=true&sSearch_1=&bRegex_1=false&bSearchable_1=true&sSearch_2=&bRegex_2=false&bSearchable_2=true&sSearch_3=&bRegex_3=false&bSearchable_3=true&iSortCol_0=2&sSortDir_0=desc&iSortingCols=1&bSortable_0=true&bSortable_1=true&bSortable_2=true&bSortable_3=true&_=1476362811995"
        s = response.headers.getlist('Set-Cookie')
        print type(s),s

        s=';'.join(s)
        print type(s), s
        cookieset=dict()
        for c in s.split(';'):
            index=c.find('=')
            if index!=-1:
                #print c[:index],c[index+1:]
                cookieset[c[:index]]=c[index+1:]

        print cookieset
        i = 1
        while i<100:
            #print i, '=' * 30
            url = url1 + str(i) + url2 + str(11 * (i - 1)) + url3
            yield Request(url=url,callback=self.level_xhr,cookies=cookieset)
            i+=1

    def level_xhr(self,response):
        contents=json.loads(response.body)['aaData']
        url0 = "http://www.game-debate.com"
        for content in contents:
            s = content['a_title']
            left = s.find('href=\"')
            right = s.find('>')
            yield Request(url=url0 + s[left + 6:right - 1], callback=self.level_2)
    def level_2(self, response):
        print 'enter level 2=========================='
                                     
        original_url = response.url
        product = response.meta.get("product", {})
        review = response.meta.get("review", {})
        
        product_xpaths = { 
                
                "source_internal_id": "//link[@rel='canonical']/@href",
                
                
                "ProductName":"//div[@class='title-text']/text()",
                
                
                "OriginalCategoryName":"game",
                

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
                
                "source_internal_id": "//link[@rel='canonical']/@href",
                
                
                "ProductName":"//div[@class='title-text']/text()",
                
                
                "SourceTestRating":"//div[@class='article-rating-box-right-rating']/text()",
                
                
                "TestDateText":"//div[@class='by-author']/text()[last()]",
                
                
                "TestPros":"//div[@class='pros-title']/following-sibling::ul//text()",
                
                
                "TestCons":"//div[@class='cons-title']/following-sibling::ul//text()",
                
                
                
                "TestVerdict":"//div[@class='article-body']/p[last()]//text()",

                "TestSummary": "//div[@class='article-body']/p[1]//text()[normalize-space()]",
                
                
                "Author":"//div[@class='by-author']/a/text()",
                
                
                "TestTitle":"//div[@class='title-text']/text()",
                
                
                
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
                                    

        matches = None
        field_value = product.get("source_internal_id", "")
        if field_value:
            matches = re.search("(?<=articles\/)(\d+)", field_value, re.IGNORECASE)
        if matches:
            product["source_internal_id"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("source_internal_id", "")
        if field_value:
            matches = re.search("(?<=articles\/)(\d+)", field_value, re.IGNORECASE)
        if matches:
            review["source_internal_id"] = matches.group(1)
                                    

        matches = None
        field_value = product.get("ProductName", "")
        if field_value:
            matches = re.search("([\s\w\:\-]+)(?=Review)", field_value, re.IGNORECASE)
        if matches:
            product["ProductName"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("PorductName", "")
        if field_value:
            matches = re.search("([\s\w\:\-]+)(?=Review)", field_value, re.IGNORECASE)
        if matches:
            review["PorductName"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("TestDateText", "")
        if field_value:
            matches = re.search("(?<=on)([\w\s,]+)(?=at)", field_value, re.IGNORECASE)
        if matches:
            review["TestDateText"] = matches.group(1)
                                    

        if review["TestDateText"]:
            
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(review["TestDateText"], "%B %d,%Y", ["en"])
                                    

        review["DBaseCategoryName"] = "PRO"
                                    

        yield product


        
                            
        yield review
        
