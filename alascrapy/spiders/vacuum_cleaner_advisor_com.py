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


class Vacuum_cleaner_advisor_comSpider(AlaSpider):
    name = 'vacuum_cleaner_advisor_com'
    allowed_domains = ['vacuum-cleaner-advisor.com']
    start_urls = ['http://vacuum-cleaner-advisor.com/Bagless-Vacuum-Reviews.html','http://vacuum-cleaner-advisor.com/Bagged-Vacuum-Reviews.html','http://vacuum-cleaner-advisor.com/Upright-Vacuum-Reviews.html','http://vacuum-cleaner-advisor.com/Canister-Vacuum-Reviews.html','http://vacuum-cleaner-advisor.com/Handheld-Vacuum-Reviews.html','http://vacuum-cleaner-advisor.com/Stick-Vacuum-Reviews.html','http://vacuum-cleaner-advisor.com/Steam-Cleaner-Reviews.html','http://vacuum-cleaner-advisor.com/HEPA-Vacuum-Reviews.html','http://vacuum-cleaner-advisor.com/Wet-Dry-Vacuum-Reviews.html','http://vacuum-cleaner-advisor.com/Cordless-Vacuum-Reviews.html','http://vacuum-cleaner-advisor.com/Allergy-Vacuum-Reviews.html']

    
    def parse(self, response):
                                     
        original_url = response.url
        product = response.meta.get("product", {})
        review = response.meta.get("review", {})
        
        urls_xpath = u"//div[@itemprop='articleBody']/div[@class='contentheading']/a/@href"
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
        
        category_leaf_xpath = u"//ul[@class='breadcrumb']/li[.//a][last()]//a//text()[normalize-space()]"
        category_path_xpath = u"//ul[@class='breadcrumb']/li[.//a]//a//text()[normalize-space()]"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
                
                
                "ProductName":u"//h1//text()",
                
                
                "OriginalCategoryName":u"//ul[@class='breadcrumb']/li[.//a]//a//text()[normalize-space()]",
                
                
                "PicURL":u"//div[@itemprop='articleBody']/div[@class='mosimage']/a/img/@src",
                
                
                            }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['TestUrl'] = original_url
        picurl = product.get("PicURL", "")
        if picurl and picurl[:2] == "//":
            product["PicURL"] = "https:" + product["PicURL"]
        if picurl and picurl[:1] == "/":
            product["PicURL"] = get_full_url(original_url, picurl)
        manuf = product.get("ProductManufacturer", "")
        if manuf == "" and u""[:2] != "//":
            product["ProductManufacturer"] = u""
        try:
            product["OriginalCategoryName"] = category['category_path']
        except:
            pass
        ocn = product.get("OriginalCategoryName", "")
        if ocn == "" and u"//ul[@class='breadcrumb']/li[.//a]//a//text()[normalize-space()]"[:2] != "//":
            product["OriginalCategoryName"] = u"//ul[@class='breadcrumb']/li[.//a]//a//text()[normalize-space()]"
        review_xpaths = { 
                
                
                "ProductName":u"//h1//text()",
                
                
                "SourceTestRating":u"substring-before(//div[@itemprop='articleBody']/p[contains(translate(.,' ',''),'rating=')]/descendant-or-self::*[name()='b' or name()='strong'][1],'/')",
                
                
                "TestDateText":u"substring-before(//time[@itemprop='datePublished']/@datetime,'T')",
                
                
                "TestPros":u"//div[@itemprop='articleBody']/p[.//text()[normalize-space()='PROS']]//text()[./preceding-sibling::node()[normalize-space()='PROS']]",
                
                
                "TestCons":u"//div[@itemprop='articleBody']/p[.//text()[normalize-space()='CONS']]//text()[./preceding-sibling::node()[normalize-space()='CONS']]",
                
                
                "TestSummary":u"//div[@itemprop='articleBody']/p[./descendant-or-self::text()[string-length(normalize-space())>1][last()][contains(.,'.')]][1]//text()[string-length(normalize-space())>1 and not(./following-sibling::*[contains(.,'/100')]) and not(./preceding::text()[1]/following-sibling::br[1]/following-sibling::text()[normalize-space()]) and not(substring-after(.,'/')='100')]",
                
                
                
                "Author":u"substring-before(substring-after(//div[translate(.,' ','')='AboutMe']/following::div[@class='module-content'][1]//p[1],' '),',')",
                
                
                "TestTitle":u"//h1//text()",
                
                
                
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
                                    

        review["SourceTestScale"] = "100"
                                    

        yield product


        
                            
        yield review
        
