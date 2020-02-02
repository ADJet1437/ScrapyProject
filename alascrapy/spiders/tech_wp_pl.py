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


class Tech_wp_plSpider(AlaSpider):
    name = 'tech_wp_pl'
    allowed_domains = ['tech.wp.pl']
    start_urls = ['http://tech.wp.pl/kat,111804,name,testy,kategoria.html']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        url_xpath = "//div[@class='pgs']/a[last()]/@href"
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
        urls_xpath = "//div[@id='stgMain']/div[starts-with(@id,'stgCol')][1]//div[@class='bx']//h3/a/@href"
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
        
        url_xpath = "//meta[@property='og:url']/@content"
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
            
            request = Request(single_url, callback=self.level_3)
            
            yield request
    
    def level_3(self, response):
                                     
        original_url = response.url
        
        category_leaf_xpath = "//ul[@class='lsPath']/li[last()]//text()"
        category_path_xpath = "//ul[@class='lsPath']/li//text()"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
                
                "source_internal_id": "//*[@name='entry']/@value",
                
                
                "ProductName":"//meta[@property='og:title']/@content",
                
                
                
                "PicURL":"//meta[@property='og:image']/@content",
                
                
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
                
                "source_internal_id": "//*[@name='entry']/@value",
                
                
                "ProductName":"//meta[@property='og:title']/@content",
                
                
                
                "TestDateText":"//meta[contains(@property,'time')]/@content",
                
                
                
                
                "TestSummary":"//div[@class='art']/descendant-or-self::p[string-length(normalize-space())>0][1]//text()",
                
                
                
                "Author":"//meta[@name='author']/@content",
                
                
                "TestTitle":"//meta[@property='og:title']/@content",
                
                
                
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
                                    

        matches = None
        field_value = review.get("TestDateText", "")
        if field_value:
            matches = re.search("(\d[^\s]*(?=\s))", field_value, re.IGNORECASE)
        if matches:
            review["TestDateText"] = matches.group(1)
                                    
        in_another_page_xpath = "//div[@class='pgs']/a[last()-1]/@href"
        pros_xpath = "//node()[starts-with(normalize-space(),'Zalety')]/following-sibling::node()[not(name()) and string-length(normalize-space())>0] | //node()[starts-with(normalize-space(),'Zalety')]/following::*[1]//text() | //*[starts-with(.,'PLUSY')]/preceding::*[1]/following::*[1]/text()"
        cons_xpath = "//node()[starts-with(normalize-space(),'Wady')]/following-sibling::node()[not(name()) and string-length(normalize-space())>0 and not(preceding::*[starts-with(.,'Zalety')])] | //node()[starts-with(normalize-space(),'Wady')]/following::*[not(./descendant-or-self::i)][1]//text() | //*[starts-with(.,'MINUSY')]/preceding::*[1]/following::*[1]/text()"
        rating_xpath = "translate(normalize-space(concat(substring(substring-before(//div[@class='content']//p[contains(.,'/10')]/descendant-or-self::text()[contains(.,'/10') and substring(translate(translate(concat(substring-before(normalize-space(substring-after(//div[@class='content']//p[contains(.,'/10')]/descendant-or-self::text()[contains(.,'/10') and contains(.,':')],':')),'/'),substring-before(normalize-space(substring-after(//div[@class='content']//p[contains(.//text(),'/10')]/descendant-or-self::text()[contains(.,'/10') and contains(.,'to') and not(contains(.,':'))],'to')),'/'),string(number(//p[contains(.,'ocena') or contains(.,'Ocena') or contains(.,'OCENA')]/descendant-or-self::text()[contains(.,'5') and not(contains(.,'10')) and not(contains(.,'/'))][last()]) * 2)),'NaN',''),',','.'),string-length(translate(translate(concat(substring-before(normalize-space(substring-after(//div[@class='content']//p[contains(.,'/10')]/descendant-or-self::text()[contains(.,'/10') and contains(.,':')],':')),'/'),substring-before(normalize-space(substring-after(//div[@class='content']//p[contains(.//text(),'/10')]/descendant-or-self::text()[contains(.,'/10') and contains(.,'to') and not(contains(.,':'))],'to')),'/'),string(number(//p[contains(.,'ocena') or contains(.,'Ocena') or contains(.,'OCENA')]/descendant-or-self::text()[contains(.,'5') and not(contains(.,'10')) and not(contains(.,'/'))][last()]) * 2)),'NaN',''),',','.'))-1,1)='.'],'/'),string-length(translate(translate(concat(substring-before(normalize-space(substring-after(//div[@class='content']//p[contains(.,'/10')]/descendant-or-self::text()[contains(.,'/10') and contains(.,':')],':')),'/'),substring-before(normalize-space(substring-after(//div[@class='content']//p[contains(.//text(),'/10')]/descendant-or-self::text()[contains(.,'/10') and contains(.,'to') and not(contains(.,':'))],'to')),'/'),string(number(//p[contains(.,'ocena') or contains(.,'Ocena') or contains(.,'OCENA')]/descendant-or-self::text()[contains(.,'5') and not(contains(.,'10')) and not(contains(.,'/'))][last()]) * 2)),'NaN',''),',','.'))-2,1),' ',substring(translate(translate(concat(substring-before(normalize-space(substring-after(//div[@class='content']//p[contains(.,'/10')]/descendant-or-self::text()[contains(.,'/10') and contains(.,':')],':')),'/'),substring-before(normalize-space(substring-after(//div[@class='content']//p[contains(.//text(),'/10')]/descendant-or-self::text()[contains(.,'/10') and contains(.,'to') and not(contains(.,':'))],'to')),'/'),string(number(//p[contains(.,'ocena') or contains(.,'Ocena') or contains(.,'OCENA')]/descendant-or-self::text()[contains(.,'5') and not(contains(.,'10')) and not(contains(.,'/'))][last()]) * 2)),'NaN',''),',','.'),string-length(translate(translate(concat(substring-before(normalize-space(substring-after(//div[@class='content']//p[contains(.,'/10')]/descendant-or-self::text()[contains(.,'/10') and contains(.,':')],':')),'/'),substring-before(normalize-space(substring-after(//div[@class='content']//p[contains(.//text(),'/10')]/descendant-or-self::text()[contains(.,'/10') and contains(.,'to') and not(contains(.,':'))],'to')),'/'),string(number(//p[contains(.,'ocena') or contains(.,'Ocena') or contains(.,'OCENA')]/descendant-or-self::text()[contains(.,'5') and not(contains(.,'10')) and not(contains(.,'/'))][last()]) * 2)),'NaN',''),',','.'))))),' ','.')"
        award_xpath = ""
        award_pic_xpath = ""
        
        test_verdict_xpath_1 = '//*[starts-with(.//text(),"OG") or contains(.//text(),"Podsumowanie")]/preceding::*[1]/following::p[contains(.,".") or contains(.,",") or contains(.,";") or contains(normalize-space()," ")][1]//text()'
        
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

        matches = None
        field_value = review.get("SourceTestRating", "")
        if field_value:
            matches = re.search("((?<=\s)\d\.*\d*(?!\D))", field_value, re.IGNORECASE)
        if matches:
            review["SourceTestRating"] = matches.group(1)
                                    

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
