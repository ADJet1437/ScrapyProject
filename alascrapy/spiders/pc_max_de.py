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


class Pc_max_deSpider(AlaSpider):
    name = 'pc_max_de'
    allowed_domains = ['pc-max.de']
    start_urls = ['http://www.pc-max.de/tags/test']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        url_xpath = "//ul[starts-with(@class,'pag')]/li[contains(@class,'next')]/a/@href"
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
        urls_xpath = "//div[@class='view-content']//ul/li/a/@href"
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
    
    def level_2(self, response):
                                     
        original_url = response.url
        
        category_leaf_xpath = "//div[contains(@class,'breadcrumb')]/a[last()]//text()"
        category_path_xpath = "//div[contains(@class,'breadcrumb')]/a//text()"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
                
                
                "ProductName":"//h1/text()",
                
                
                
                "PicURL":"//meta[@property='og:image']/@content",
                
                
                "ProductManufacturer":"//body/descendant-or-self::th[contains(.,'Hersteller')][1]/following::td[1]//text()"
                
                            }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['TestUrl'] = original_url
        picurl = product.get("PicURL", "")
        if picurl and picurl[:2] == "//":
            product["PicURL"] = "https:" + product["PicURL"]
        if picurl and picurl[:1] == "/":
            product["PicURL"] = get_full_url(original_url, picurl)
        manuf = product.get("ProductManufacturer", "")
        if manuf == "" and "//body/descendant-or-self::th[contains(.,'Hersteller')][1]/following::td[1]//text()"[:2] != "//":
            product["ProductManufacturer"] = "//body/descendant-or-self::th[contains(.,'Hersteller')][1]/following::td[1]//text()"
        try:
            product["OriginalCategoryName"] = category['category_path']
        except:
            pass
        ocn = product.get("OriginalCategoryName", "")
        if ocn == "" and ""[:2] != "//":
            product["OriginalCategoryName"] = ""
        review_xpaths = { 
                
                
                "ProductName":"//h1/text()",
                
                
                
                "TestDateText":"//div[@class='content']/descendant-or-self::*[starts-with(.,'Datum')]/following-sibling::*[string-length(normalize-space())>1][1]/text()",
                
                
                "TestPros":"//div[starts-with(@class,'content')]/*[(name()='p' or (name()='div' and not(//div[starts-with(@class,'content')]/p))) and translate(./descendant-or-self::*/text(),' ','')='Pro' or translate(./descendant-or-self::*/text(),' ','')='Pro:' or concat(substring(./descendant-or-self::*[string-length(normalize-space())=3]/text(),1,1),'o',substring(./descendant-or-self::*[string-length(normalize-space())=3]/text(),3,1))='For' or translate(concat(substring(./descendant-or-self::*/text(),1,1),'o',substring(./descendant-or-self::*/text(),3,5)),' ','')='Fordas' or translate(./descendant-or-self::*/text(),' ','')='Positiv'][1]//text()",
                
                
                "TestCons":"//div[starts-with(@class,'content')]/*[(name()='p' or (name()='div' and not(//div[starts-with(@class,'content')]/p))) and translate(./descendant-or-self::*/text(),' ','')='Contra' or translate(./descendant-or-self::*/text(),' ','')='Contra:' or (starts-with(translate(./descendant-or-self::*/text(),' ',''),'Gegen') and string-length(substring-before(concat(normalize-space(./descendant-or-self::*[starts-with(.,'Gegen')]/text()),' '),' '))<8) or starts-with(translate(./descendant-or-self::*/text(),' ',''),'Gegendas') or starts-with(translate(./descendant-or-self::*/text(),' ',''),'Dagegen') or translate(./descendant-or-self::*/text(),' ','')='Negativ'][1]//text()",
                
                
                "TestSummary":"//meta[@property='og:description' and normalize-space(@content)]/@content",
                
                
                
                "Author":"//div[@id='autorBox']/h4/a/text()",
                
                
                "TestTitle":"//h1/text()",
                
                
                
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

        id_value = self.extract(response.xpath("(//body/descendant-or-self::tr[contains(.,'Preis') and not(following-sibling::td)][1]/following-sibling::tr[1]/td[position()=count(//th[starts-with(normalize-space(),'Preis')]/preceding-sibling::*)+1]//text() | //body/descendant-or-self::tr[contains(.,'Preis')][1]/td//text())[1]"))
        if id_value:
            product_id = self.product_id(product)
            product_id['ID_kind'] = "price"
            product_id['ID_value'] = id_value
            yield product_id
        

        review["DBaseCategoryName"] = "PRO"
                                    

        matches = None
        field_value = review.get("TestDateText", "")
        if field_value:
            matches = re.search("(\d{2}\.\d{2}\.\d{4})", field_value, re.IGNORECASE)
        if matches:
            review["TestDateText"] = matches.group(1)
                                    

        if review["TestDateText"]:
            
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(review["TestDateText"], "%d.%m.%Y", ["en"])
                                    
        in_another_page_xpath = "//body/descendant-or-self::div[@class='article-navigation'][1]/ol/li[last()]/a/@href"
        pros_xpath = "//div[starts-with(@class,'content')]/*[(name()='p' or (name()='div' and not(//div[starts-with(@class,'content')]/p))) and translate(./descendant-or-self::*/text(),' ','')='Pro' or translate(./descendant-or-self::*/text(),' ','')='Pro:' or concat(substring(./descendant-or-self::*[string-length(normalize-space())=3]/text(),1,1),'o',substring(./descendant-or-self::*[string-length(normalize-space())=3]/text(),3,1))='For' or translate(concat(substring(./descendant-or-self::*/text(),1,1),'o',substring(./descendant-or-self::*/text(),3,5)),' ','')='Fordas' or translate(./descendant-or-self::*/text(),' ','')='Positiv'][1]//text()"
        cons_xpath = "//div[starts-with(@class,'content')]/*[(name()='p' or (name()='div' and not(//div[starts-with(@class,'content')]/p))) and translate(./descendant-or-self::*/text(),' ','')='Contra' or translate(./descendant-or-self::*/text(),' ','')='Contra:' or (starts-with(translate(./descendant-or-self::*/text(),' ',''),'Gegen') and string-length(substring-before(concat(normalize-space(./descendant-or-self::*[starts-with(.,'Gegen')]/text()),' '),' '))<8) or starts-with(translate(./descendant-or-self::*/text(),' ',''),'Gegendas') or starts-with(translate(./descendant-or-self::*/text(),' ',''),'Dagegen') or translate(./descendant-or-self::*/text(),' ','')='Negativ'][1]//text()"
        rating_xpath = ""
        award_xpath = ""
        award_pic_xpath = ""
        
        test_verdict_xpath_1 = '//div[contains(@class,"center")]/descendant-or-self::div[starts-with(@class,"content")][1]/descendant-or-self::*[(name()="p" or (name()="div" and not(//div[starts-with(@class,"content")]/p))) and string-length(normalize-space(.//text()))>1 and not(.//script) and (contains(//div[@class="content"]//li/a[@class="active"]/text(),"Fazit") or preceding::*[string-length(normalize-space())>1][1][starts-with(.,"Fazit")])][1]//text()'
        
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

        yield product

    
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
