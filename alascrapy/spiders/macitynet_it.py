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


class Macitynet_itSpider(AlaSpider):
    name = 'macitynet_it'
    allowed_domains = ['macitynet.it']
    start_urls = ['http://www.macitynet.it/category/macity/recensioni/']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        url_xpath = "//div[@class='pagination']/a[last()-1]/@href"
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
        urls_xpath = "//ul[@class='category3']/li//a[@class='main-headline']/@href | //div[@class='featured-box']//a/@href"
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
        
        category_leaf_xpath = "//div[@class='breadcrumb']/descendant::a[name(..)='span' and ../@typeof][last()]//text()"
        category_path_xpath = "//div[@class='breadcrumb']/descendant::a[name(..)='span' and ../@typeof]//text()"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
                
                "source_internal_id": "substring-before(substring-after(//body/@class,'postid-'),' ')",
                
                
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
                
                "source_internal_id": "substring-before(substring-after(//body/@class,'postid-'),' ')",
                
                
                "ProductName":"//h1/text()",
                
                
                "SourceTestRating":"substring-after(//div[@itemprop='aggregateRating']/img/@src,'rat=')",
                
                
                "TestDateText":"substring-before(//meta[starts-with(@property,'DC.date')]/@content,'T')",
                
                
                "TestPros":"//*[(name()='p' or name()='h3' or name()='h2') and (.//text()='Pro' or .//text()='PRO' or .//text()='Pro:') and count(./node()[string-length(normalize-space())>1])=1]/following::*[(name()='p' or name()='ul') and string-length(normalize-space())>1][1]//text() | //p[.//text()='Pro' and count(./node()[string-length(normalize-space())>1])>1]/descendant-or-self::node()[normalize-space()='Pro']/following-sibling::text() | //*[name()='b' and (.//text()='Pro' or .//text()='PRO' or .//text()='Pro:') and count(./node()[string-length(normalize-space())>1])=1]/following::div[contains(./following::b[1]/text(),'Contro') or contains(./preceding::b[1]/text(),'CONTRO')]//text()",
                
                
                "TestCons":"//*[(name()='p' or name()='h3' or name()='h2') and (.//text()='Contro' or .//text()='CONTRO' or .//text()='Contro:') and count(./node()[string-length(normalize-space())>1])=1]/following::*[(name()='p' or name()='ul') and string-length(normalize-space())>1][1]//text() | //p[.//text()='Contro' and count(./node()[string-length(normalize-space())>1])>1]/descendant-or-self::node()[normalize-space()='Contro']/following-sibling::text() | //div[contains(./b,'Contro') or contains(./b,'CONTRO')]/following::div[string-length(normalize-space())>1 and (contains(./preceding::b[1]/text(),'Contro') or contains(./preceding::b[1]/text(),'Contro')) and not(./b)]//text()",
                
                
                "TestSummary":"//span[@itemprop='articleBody']/p[(./preceding::div[starts-with(@class,'side_col')] or not(//span[@itemprop='articleBody']/div[starts-with(@class,'side_col')])) and string-length(normalize-space())>1][1]//text() | //span[@itemprop='articleBody']/div[string-length(normalize-space())>1 and not(.//script) and not(//span[@itemprop='articleBody']/p)][1]//text()",
                
                
                
                "Author":"//span[@itemprop='author']//text()",
                
                
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
                                    
        in_another_page_xpath = "//*[@id='post-pagination']/a[last()]/@href"
        pros_xpath = "//*[(name()='p' or name()='h3' or name()='h2') and (.//text()='Pro' or .//text()='PRO' or .//text()='Pro:') and count(./node()[string-length(normalize-space())>1])=1]/following::*[(name()='p' or name()='ul') and string-length(normalize-space())>1][1]//text() | //p[.//text()='Pro' and count(./node()[string-length(normalize-space())>1])>1]/descendant-or-self::node()[normalize-space()='Pro']/following-sibling::node() | //*[name()='b' and (.//text()='Pro' or .//text()='PRO' or .//text()='Pro:') and count(./node()[string-length(normalize-space())>1])=1]/following::div[contains(./following::b[1]/text(),'Contro') or contains(./preceding::b[1]/text(),'CONTRO')]//text()"
        cons_xpath = "//*[(name()='p' or name()='h3' or name()='h2') and (.//text()='Contro' or .//text()='CONTRO' or .//text()='Contro:') and count(./node()[string-length(normalize-space())>1])=1]/following::*[(name()='p' or name()='ul') and string-length(normalize-space())>1][1]//text() | //p[.//text()='Contro' and count(./node()[string-length(normalize-space())>1])>1]/descendant-or-self::node()[normalize-space()='Contro']/following-sibling::node() | //div[contains(./b,'Contro') or contains(./b,'CONTRO')]/following::div[string-length(normalize-space())>1 and (contains(./preceding::b[1]/text(),'Contro') or contains(./preceding::b[1]/text(),'Contro')) and not(./b)]//text()"
        rating_xpath = "substring-after(//div[@itemprop='aggregateRating']/img/@src,'rat=')"
        award_xpath = ""
        award_pic_xpath = ""
        
        test_verdict_xpath_1 = '//*[(name()="h2" or name()="h3" or name()="strong") and (starts-with(.//text(),"Conclusioni") or starts-with(.//text(),"Conclusione"))]/preceding::*[1]/following::p[not(count(./*[string-length(normalize-space())>1])=1 and (.//text()="Conclusioni" or .//text()="Conclusione")) and string-length(normalize-space())>1][1]//text()'
        
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
