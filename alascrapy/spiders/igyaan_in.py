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


class Igyaan_inSpider(AlaSpider):
    name = 'igyaan_in'
    allowed_domains = ['igyaan.in']
    start_urls = ['http://www.igyaan.in/category/review/amp/']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        url_xpath = "//div[@class='next']/a/@href"
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
        urls_xpath = "//h2/a/@href"
        params_regex = {}
        urls = self.extract_list(response.xpath(urls_xpath))
        
        for single_url in urls:
            matches = None
            if "(\w.*(?=\/amp\/))":
                matches = re.search("(\w.*(?=\/amp\/))", single_url, re.IGNORECASE)
                if matches:
                    single_url = matches.group(0)
                else:
                    continue
            single_url = get_full_url(original_url, single_url)
            
            request = Request(single_url, callback=self.level_2)
            
             
            yield request
    
    def level_2(self, response):
                                     
        original_url = response.url
        
        product_xpaths = { 
                
                "source_internal_id": "substring-before(substring-after(//body/@class,'postid-'),' ')",
                
                
                "ProductName":"//meta[@property='og:title']/@content",
                
                
                "OriginalCategoryName":"//a[contains(@class,'category')]//text()",
                
                
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
        if ocn == "" and "//a[contains(@class,'category')]//text()"[:2] != "//":
            product["OriginalCategoryName"] = "//a[contains(@class,'category')]//text()"
        review_xpaths = { 
                
                "source_internal_id": "substring-before(substring-after(//body/@class,'postid-'),' ')",
                
                
                "ProductName":"//meta[@property='og:title']/@content",
                
                
                "SourceTestRating":"//div[contains(@class,'editor_rating')]/div[contains(@class,'number')]//text()",
                
                
                "TestDateText":"//meta[contains(@property,'published_time')]/@content",
                
                
                "TestPros":"//*[(starts-with(translate(.,' ',''),'GOODTHINGS') or starts-with(translate(.,' ',''),'TheGood')) and not(./ul)]/following-sibling::ul[1]/li//text() | //*[(starts-with(translate(.,' ',''),'GOODTHINGS') or starts-with(translate(.,' ',''),'TheGood')) and ./ul]/ul[1]/li//text()",
                
                
                "TestCons":"//*[(starts-with(translate(.,' ',''),'BADTHINGS') or starts-with(translate(.,' ',''),'TheBad')) and not(./ul)]/following-sibling::ul[1]/li//text() | //*[(starts-with(translate(.,' ',''),'BADTHINGS') or starts-with(translate(.,' ',''),'TheBad')) and ./ul]/ul[1]/li//text()",
                
                
                "TestSummary":"//*[normalize-space()='Overview']/following::p[string-length(normalize-space())>1][1]//text() | //div[starts-with(translate(./@class,' ',''),'postcontentcontent') and not(//*[normalize-space()='Overview'])]/span[@itemprop='description']/descendant-or-self::p[string-length(normalize-space())>1][1]//text() | //div[starts-with(translate(./@class,' ',''),'postcontentcontent') and not(./span[@itemprop='description']/p) and not(//*[normalize-space()='Overview'])]/descendant-or-self::p[string-length(normalize-space())>1][1]//text() | //div[starts-with(@id,'content') and not(//*[normalize-space()='Overview']) and not(//div[starts-with(translate(./@class,' ',''),'postcontentcontent')])]/descendant-or-self::p[string-length(normalize-space())>1][1]//text() | //meta[@property='og:description' and not(//div[starts-with(@id,'content')]//p[string-length(normalize-space())>1])]/@content",
                
                
                
                "Author":"//span[contains(@class,'author')]/a//text()",
                
                
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
                                    
        in_another_page_xpath = "//div[contains(@class,'pagination')]/a[last()]/@href"
        pros_xpath = "//*[(starts-with(translate(.,' ',''),'GOODTHINGS') or starts-with(translate(.,' ',''),'TheGood')) and not(./ul)]/following-sibling::ul[1]/li//text() | //*[(starts-with(translate(.,' ',''),'GOODTHINGS') or starts-with(translate(.,' ',''),'TheGood')) and ./ul]/ul[1]/li//text()"
        cons_xpath = "//*[(starts-with(translate(.,' ',''),'BADTHINGS') or starts-with(translate(.,' ',''),'TheBad')) and not(./ul)]/following-sibling::ul[1]/li//text() | //*[(starts-with(translate(.,' ',''),'BADTHINGS') or starts-with(translate(.,' ',''),'TheBad')) and ./ul]/ul[1]/li//text()"
        rating_xpath = ""
        award_xpath = ""
        award_pic_xpath = ""
        
        test_verdict_xpath_1 = '//div[contains(@class,"description-cell")]/p[normalize-space()][1]//text() | //*[(starts-with(.,"Conclusion") or starts-with(.,"CONCLUSION") or starts-with(.,"VERDICT") or starts-with(substring(.,2),"Conclusion") or starts-with(substring(.,2),"CONCLUSION") or starts-with(substring(.,2),"VERDICT")) and not(//div[contains(@class,"description-cell")]/p[normalize-space()])]/following-sibling::p[normalize-space()][1]//text() | //*[(starts-with(.,"Conclusion") or starts-with(.,"CONCLUSION") or starts-with(.,"VERDICT") or starts-with(substring(.,2),"Conclusion") or starts-with(substring(.,2),"CONCLUSION") or starts-with(substring(.,2),"VERDICT")) and not(//div[contains(@class,"description-cell")]/p[normalize-space()]) and not(./following-sibling::p)]/following-sibling::div[normalize-space()][1]//text() | //div[@class="reviewtop" and not(//div[contains(@class,"description-cell")]/p[normalize-space()]) and not(//*[(starts-with(.,"Conclusion") or starts-with(.,"CONCLUSION") or starts-with(.,"VERDICT"))])]//p//text() | //*[contains(.,"Roundup")]/following-sibling::p[string-length(normalize-space())>1][last()]//text()'
        
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
