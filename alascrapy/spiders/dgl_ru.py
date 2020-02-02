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


class Dgl_ruSpider(AlaSpider):
    name = 'dgl_ru'
    allowed_domains = ['dgl.ru']
    start_urls = ['http://www.dgl.ru/reviews/']

    
    def parse(self, response):
                                     
        original_url = response.url
        product = response.meta.get("product", {})
        review = response.meta.get("review", {})
        
        url_xpath = u"//div[@class='pagination']//li[.//a[@class='active']]/following-sibling::li[1]//a/@href"
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
        urls_xpath = u"//div[@class='post-module']/a/@href"
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
                
                "source_internal_id": u"substring-before(substring-after(//meta[@itemprop='url']/@content,'_'),'.')",
                
                
                "ProductName":u"//h1[@itemprop='name']//text()",
                
                
                "OriginalCategoryName":u"//span[@itemprop='articleSection']//text()",
                
                
                "PicURL":u"//meta[@property='og:image']/@content",
                
                
                "ProductManufacturer":u"//p//text()[string-length(normalize-space())>1 and ./preceding::text()[1][contains(.,'Производитель')]]"
                
                            }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['TestUrl'] = original_url
        picurl = product.get("PicURL", "")
        if picurl and picurl[:2] == "//":
            product["PicURL"] = "https:" + product["PicURL"]
        if picurl and picurl[:1] == "/":
            product["PicURL"] = get_full_url(original_url, picurl)
        manuf = product.get("ProductManufacturer", "")
        if manuf == "" and u"//p//text()[string-length(normalize-space())>1 and ./preceding::text()[1][contains(.,'Производитель')]]"[:2] != "//":
            product["ProductManufacturer"] = u"//p//text()[string-length(normalize-space())>1 and ./preceding::text()[1][contains(.,'Производитель')]]"
        try:
            product["OriginalCategoryName"] = category['category_path']
        except:
            pass
        ocn = product.get("OriginalCategoryName", "")
        if ocn == "" and u"//span[@itemprop='articleSection']//text()"[:2] != "//":
            product["OriginalCategoryName"] = u"//span[@itemprop='articleSection']//text()"
        review_xpaths = { 
                
                "source_internal_id": u"substring-before(substring-after(//meta[@itemprop='url']/@content,'_'),'.')",
                
                
                "ProductName":u"//h1[@itemprop='name']//text()",
                
                
                "SourceTestRating":u"translate(concat(translate((//div[@class='aecms-cut' or @class='article-vrezka']/p//text()[string-length(normalize-space())>1 or not(string(number(normalize-space()))='NaN')][./preceding::text()[string-length(normalize-space())>1][1][(contains(.,'Оценка') or contains(.,'Итого:')) and not(./following::*[contains(.,'Оценка') or contains(.,'Итого:')])]] | //div[@class='aecms-cut']/p[(contains(.,'Оценка:') or contains(.,'Итого:')) and string-length(normalize-space(substring-after(.,':')))>1][last()] | //div[@class='aecms-cut']/p[contains(./u,' звезды')])[not(contains(.,'100')) and string(number(substring(normalize-space(),1,2)))='NaN'],',','.') , string(number(substring(substring-after(normalize-space(translate((//div[@class='aecms-cut']/p//text()[string-length(normalize-space())>1 or not(string(number(.))='NaN')][./preceding::text()[string-length(normalize-space())>1][1][(contains(.,'Оценка') or contains(.,'Итого:')) and not(./following::*[contains(.,'Оценка') or contains(.,'Итого:')])]] | //div[@class='aecms-cut']/p[(contains(.,'Оценка:') or contains(.,'Итого:')) and string-length(normalize-space(substring-after(.,':')))>1][last()] | //div[@class='aecms-cut']/p[contains(./u,' звезды')])[contains(.,'100') or not(string(number(substring(normalize-space(),1,2)))='NaN')],',','.')),' '),1,2)) div 20)),'Na','')",
                
                
                "TestDateText":u"//span[@itemprop='datePublished']/@content",
                
                
                "TestPros":u"//p[starts-with(normalize-space(),'•') and ./preceding-sibling::p[./u][1][contains(.,'Достоинства') or contains(.,'Преимущества')]]//text() | //p[string-length(normalize-space(substring-after(.,'Достоинства')))>1 or string-length(normalize-space(substring-after(.,'Преимущества')))>1]//text()[(./preceding::text()[contains(.,'Достоинства')] or ./preceding::text()[contains(.,'Преимущества')]) and string-length(normalize-space())>1] | //ul[./preceding-sibling::*[1][contains(.,'Достоинства') or contains(.,'Преимущества')]]/li//text() | //p[./preceding-sibling::*[1][normalize-space()='Достоинства' or normalize-space()='Достоинства:' or normalize-space()='Преимущества' or normalize-space()='Преимущества:']]//text()",
                
                
                "TestCons":u"//p[starts-with(normalize-space(),'•') and ./preceding-sibling::p[./u][1][contains(.,'Недостатки')]]//text() | //p[string-length(normalize-space(substring-after(.,'Недостатки')))>1]//text()[./preceding::text()[contains(.,'Недостатки')] and string-length(normalize-space())>1] | //ul[./preceding-sibling::*[1][contains(.,'Недостатки')]]/li//text() | //p[./preceding-sibling::*[1][normalize-space()='Недостатки' or normalize-space()='Недостатки:']]//text()",
                
                
                "TestSummary":u"//div[@itemprop='articleBody']/descendant-or-self::p[string-length(normalize-space())>1][1]//text()",
                
                
                "TestVerdict":u"(//div[@class='article-vrezka']/p[normalize-space(./text())][1]//text() | //p//text()[./preceding::text()[1][contains(.,'Вывод') and string-length(normalize-space(substring-after(.,'Вывод')))<2]])[last()]",
                
                
                "Author":u"//div[@id='header']//a[contains(@class,'logo')]/@title",
                
                
                "TestTitle":u"//h1[@itemprop='name']//text()",
                
                
                
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

        product_id = self.product_id(product)
        id_value = self.extract(response.xpath(u"//p//text()[string-length(normalize-space())>1 and ./preceding::text()[1][contains(.,'Цена')]]"))
        if id_value:
            product_id['ID_kind'] = "Price"
            product_id['ID_value'] = id_value
            yield product_id
        

        review["DBaseCategoryName"] = "PRO"
                                    

        review["SourceTestScale"] = "5"
                                    

        matches = None
        field_value = product.get("ProductManufacturer", "")
        if field_value:
            matches = re.search("(\w.*\w)", field_value, re.IGNORECASE)
        if matches:
            product["ProductManufacturer"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("SourceTestRating", "")
        if field_value:
            matches = re.search("(\d\.\d)", field_value, re.IGNORECASE)
        if matches:
            review["SourceTestRating"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("SourceTestRating", "")
        if field_value:
            matches = re.search("(\d)", field_value, re.IGNORECASE)
        if matches:
            review["SourceTestRating"] = matches.group(1)
                                    

        matches = None
        field_value = review.get("SourceTestRating", "")
        if field_value:
            matches = re.search("(\d(?=\s|\/))", field_value, re.IGNORECASE)
        if matches:
            review["SourceTestRating"] = matches.group(1)
                                    

        yield product


        
                            
        yield review
        
