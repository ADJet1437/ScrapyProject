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


class Videogamer_enSpider(AlaSpider):
    name = 'videogamer_en'
    allowed_domains = ['videogamer.com']
    start_urls = ['http://www.videogamer.com/reviews/']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        urls_xpath = "//div[@class='details']//h2/a/@href"
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
        url_xpath = "//li[@class='next numPaginNext']/a/@href"
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
    
    def level_2(self, response):
                                     
        original_url = response.url
        
        product_xpaths = { 
                
                
                "ProductName":"//h5[@itemprop='name']/a/text()",
                
                
                "OriginalCategoryName":"game",
                
                
                "PicURL":"//meta[@property='og:image']/@content",
                
                
                "ProductManufacturer":"//tr[td[contains(text(),'Publisher')]]/td[last()]/text()"
                
                            }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['TestUrl'] = original_url
        picurl = product.get("PicURL", "")
        if picurl and picurl[:2] == "//":
            product["PicURL"] = "https:" + product["PicURL"]
        if picurl and picurl[:1] == "/":
            product["PicURL"] = get_full_url(original_url, picurl)
        manuf = product.get("ProductManufacturer", "")
        if manuf == "" and "//tr[td[contains(text(),'Publisher')]]/td[last()]/text()"[:2] != "//":
            product["ProductManufacturer"] = "//tr[td[contains(text(),'Publisher')]]/td[last()]/text()"
        try:
            product["OriginalCategoryName"] = category['category_path']
        except:
            pass
        ocn = product["OriginalCategoryName"]
        if ocn == "" and "game"[:2] != "//":
            product["OriginalCategoryName"] = "game"
        review_xpaths = { 
                
                
                "ProductName":"//h5[@itemprop='name']/a/text()",
                
                
                "SourceTestRating":"//div[@itemprop='ratingValue']/text()",
                
                
                "TestDateText":"(//header//time[@class='publishDate'][1]/@datetime | //time[@class='publishDate'][1]/@datetime)[1]",
                
                
                "TestPros":"//div[@class='reviewSummaryBox clrfix']/ul/li[not(@class='bad')]/text()",
                
                
                "TestCons":"//ul/li[@class='bad']/text()",
                
                
                "TestSummary":"//h2[@itemprop='description']/text()",
                
                
                "TestVerdict":"//div[@itemprop='reviewBody']/p[last()-1]/text() | //div[@itemprop='reviewBody']/p[last()-2]/text()",
                
                
                "Author":"//a[@rel='author']/text()",
                
                
                "TestTitle":"//h1[@itemprop='name']/text()",
                
                
                
                            }
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        review['TestUrl'] = original_url
        try:
            review['ProductName'] = product['ProductName']
            review['source_internal_id'] = product['source_internal_id']
        except:
            pass

        review["DBaseCategoryName"] = "PRO"
                                    

        review["SourceTestScale"] = "10"
                                    

        if review["TestDateText"]:
            
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(review["TestDateText"], "%Y-%m-%dT%H:%M:%S+01:00", ["en"])
                                    

        yield product


        
                            
        yield review
        
