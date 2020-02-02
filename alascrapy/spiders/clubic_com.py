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


class Clubic_comSpider(AlaSpider):
    name = 'clubic_com'
    allowed_domains = ['clubic.com']
    start_urls = ['http://www.clubic.com/guide-test-comparatif-informatique/']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        url_xpath = "//a[./i[contains(@class,'angle-right')]]/@href"
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
        urls_xpath = "//div[@class='row']/div[starts-with(@class,'large') and .//h2]//h2/a/@href"
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
        
        category_leaf_xpath = "//ul[contains(@class,'breadcrumb')]/li[last()]//text()"
        category_path_xpath = "//ul[contains(@class,'breadcrumb')]/li//text()"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
                
                "source_internal_id": "substring-before(substring-after(//meta[@property='og:url']/@content,'article-'),'-')",
                
                
                "ProductName":"//h1/text()",
                
                
                
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
                
                "source_internal_id": "substring-before(substring-after(//meta[@property='og:url']/@content,'article-'),'-')",
                
                
                "ProductName":"//h1/text()",
                
                
                "SourceTestRating":"(//div[@itemprop='reviewRating']/span[@itemprop='ratingValue' and normalize-space(@content)]/@content | //figure//span/text())[1]",
                
                
                "TestDateText":"substring-before(//meta[contains(@property,'published_time')]/@content,'T')",
                
                
                "TestPros":"//div[contains(translate(.,' ',''),'Lesplus')]/following-sibling::*[contains(@class,'txt-success')][1]//text()",
                
                
                "TestCons":"//div[contains(translate(.,' ',''),'Lesmoins')]/following-sibling::*[contains(@class,'txt-alert')][1]//text()",
                
                
                "TestSummary":"string(//div[contains(@class,'article-container')]/node()[((name()='strong') or (not(name()) and not(../strong)) or name()='b') and string-length(normalize-space())>1 and (contains(.,'.') or contains(.,',') or contains(.,'?') or contains(.,';'))][1])",
                
                
                
                "Author":"//meta[contains(@property,'author')]/@content",
                
                
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

        review["DBaseCategoryName"] = "PRO"
                                    

        review["SourceTestScale"] = "5"
                                    
        in_another_page_xpath = "//div[contains(@class,'summary-content')]/descendant-or-self::div[./a][last()]/a/@href"
        pros_xpath = "//div[contains(translate(.,' ',''),'Lesplus')]/following-sibling::*[contains(@class,'txt-success')][1]//text()"
        cons_xpath = "//div[contains(translate(.,' ',''),'Lesmoins')]/following-sibling::*[contains(@class,'txt-alert')][1]//text()"
        rating_xpath = "(//div[@itemprop='reviewRating']/span[@itemprop='ratingValue' and normalize-space(@content)]/@content | //figure//span/text())[1]"
        award_xpath = ""
        award_pic_xpath = ""
        
        test_verdict_xpath_1 = '//h2[contains(translate(.," ",""),"Notreavis") or contains(.,"Conclusion")]/following-sibling::node()[./preceding::node()[1][name()="br" or name()="h2"] and ./following-sibling::node()[1][name()="br" or name()="i"]][string-length(normalize-space())>1][last()] | //div[contains(@class,"article-container") and not(./h2) and (contains(translate(//div[contains(@class,"summary-content")]/descendant-or-self::div[./a][last()]/a/@title," ",""),"Notreavis") or contains(//div[contains(@class,"summary-content")]/descendant-or-self::div[./a][last()]/a/@title,"Conclusion"))]/node()[not(./descendant-or-self::script) and string-length(normalize-space())>1 and ./preceding::node()[1][name()="br" or name()="h2"] and ./following-sibling::node()[1][name()="br" or name()="i"]][string-length(normalize-space())>1][1]'
        
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
