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


class Vortez_netSpider(AlaSpider):
    name = 'vortez_net'
    allowed_domains = ['vortez.net']
    start_urls = ['http://www.vortez.net/articles_categories/cpusandmotherboards.html','http://www.vortez.net/articles_categories/memory.html','http://www.vortez.net/articles_categories/graphics.html','http://www.vortez.net/articles_categories/cooling.html','http://www.vortez.net/articles_categories/cases_and_psu.html','http://www.vortez.net/articles_categories/storage.html','http://www.vortez.net/articles_categories/peripherals.html','http://www.vortez.net/articles_categories/audio.html','http://www.vortez.net/articles_categories/full_systems.html','http://www.vortez.net/articles_categories/misc.html','http://www.vortez.net/articles_categories/games.html']

    
    def parse(self, response):
                                     
        original_url = response.url
        product = response.meta.get("product", {})
        review = response.meta.get("review", {})
        
        url_xpath = u"//div[contains(@class,'the-article-content')]/span[@class='pagelinkselected'][1]/following-sibling::span[1]//a/@href"
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
        urls_xpath = u"//h1/a/@href"
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
            single_url = "http://www.vortez.net/" + single_url
            
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
                
                "source_internal_id": u"//div[@class='article-icons']//@data-disqus-identifier",
                
                
                "ProductName":u"//div[contains(@class,'the-article-title')]//h2//text() | //div[@id='content']//h1//text()",
                
                
                "OriginalCategoryName":u"//ul[translate(@rel,' ','')='MainMenu']/li/a[contains(@href,'articles/')]//text()",
                
                
                "PicURL":u"//div[@align='justify']//div[contains(@style,'center')]//img/@src",
                
                
                "ProductManufacturer":u"//div[@align='justify']/a[./preceding-sibling::*[string-length(normalize-space())>1][1][normalize-space()='Manufacturer']]//text()"
                
                            }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['TestUrl'] = original_url
        picurl = product.get("PicURL", "")
        if picurl and picurl[:2] == "//":
            product["PicURL"] = "https:" + product["PicURL"]
        if picurl and picurl[:1] == "/":
            product["PicURL"] = get_full_url(original_url, picurl)
        manuf = product.get("ProductManufacturer", "")
        if manuf == "" and u"//div[@align='justify']/a[./preceding-sibling::*[string-length(normalize-space())>1][1][normalize-space()='Manufacturer']]//text()"[:2] != "//":
            product["ProductManufacturer"] = u"//div[@align='justify']/a[./preceding-sibling::*[string-length(normalize-space())>1][1][normalize-space()='Manufacturer']]//text()"
        try:
            product["OriginalCategoryName"] = category['category_path']
        except:
            pass
        ocn = product.get("OriginalCategoryName", "")
        if ocn == "" and u"//ul[translate(@rel,' ','')='MainMenu']/li/a[contains(@href,'articles/')]//text()"[:2] != "//":
            product["OriginalCategoryName"] = u"//ul[translate(@rel,' ','')='MainMenu']/li/a[contains(@href,'articles/')]//text()"
        review_xpaths = { 
                
                "source_internal_id": u"//div[@class='article-icons']//@data-disqus-identifier",
                
                
                "ProductName":u"//div[contains(@class,'the-article-title')]//h2//text() | //div[@id='content']//h1//text()",
                
                
                
                "TestDateText":u"normalize-space(//div[@class='article-icons'])",
                
                
                
                
                "TestSummary":u"//meta[@name='description']/@content",
                
                
                
                "Author":u"concat(substring-after(//div[@class='article-icons']//text()[starts-with(normalize-space(),'by ')],'by'),substring-before(substring-after(//base[not(//div[@class='article-icons']//text()[starts-with(normalize-space(),'by ')])]/@href,'www.'),'/'))",
                
                
                "TestTitle":u"//div[contains(@class,'the-article-title')]//h2//text() | //div[@id='content']//h1//text()",
                
                
                
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
        id_value = self.extract(response.xpath(u"//div[@align='justify']//text()[./preceding-sibling::*[1][translate(.,' ','')='StreetPrice']]"))
        if id_value:
            product_id['ID_kind'] = "Price"
            product_id['ID_value'] = id_value
            yield product_id
        

        review["DBaseCategoryName"] = "PRO"
                                    

        matches = None
        field_value = review.get("TestDateText", "")
        if field_value:
            matches = re.search("(\d{2}\-\d{2}\-\d{2})", field_value, re.IGNORECASE)
        if matches:
            review["TestDateText"] = matches.group(1)
                                    

        if review["TestDateText"]:
            
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(review["TestDateText"], "%d-%m-%y", ["en"])
                                    
        in_another_page_xpath = u"//div[contains(@class,'the-article-content')]//span[@class='pagelink' and ./a][last()]/a/@href"
        pros_xpath = u"//div[@class='quoteblock']//text()[./preceding-sibling::*[normalize-space()='Pros' or normalize-space()='Pros:'] and not(./preceding-sibling::*[normalize-space()='Cons' or normalize-space()='Cons:'])]"
        cons_xpath = u"//div[@class='quoteblock']//text()[./preceding-sibling::*[normalize-space()='Cons' or normalize-space()='Cons:']]"
        rating_xpath = u""
        award_xpath = u"translate(substring-before(substring-after(//div[contains(@class,'main-content')]/descendant-or-self::div[@class='the-article-content'][1]/descendant-or-self::a[contains(@href,'vortez_net_awards')]/@href,'/content_page/'),'.html'),'_',' ')"
        award_pic_xpath = u"//div[contains(@class,'main-content')]/descendant-or-self::div[@class='the-article-content'][1]/descendant-or-self::img[contains(@src,'award')]/@src"
        
        test_verdict_xpath_1 = u'//div[contains(@class,"main-content")]/descendant-or-self::div[@class="the-article-content"][1]/*[normalize-space()="Conclusion" or starts-with(normalize-space(),"Conclu")]/following::text()[string-length(normalize-space())>1][1]'
        
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
