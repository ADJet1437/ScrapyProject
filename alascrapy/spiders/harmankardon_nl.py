# -*- coding: utf8 -*-
from datetime import datetime
import re, json

from scrapy.http import Request
from scrapy.selector import Selector

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.spiders.base_spiders.bazaarvoice_spider import BVNoSeleniumSpider
from alascrapy.lib.generic import get_full_url, date_format
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import CategoryItem, ProductItem, ReviewItem, ProductIdItem
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from alascrapy.lib.selenium_browser import SeleniumBrowser


api_link_template = '''http://api.bazaarvoice.com/data/batch.json?passkey=tvphe3l9jzskz01ozb1xpjja1&apiversion=5.5&displaycode=7458-nl_nl&resource.q0=reviews&filter.q0=isratingsonly%3Aeq%3Afalse&filter.q0=productid%3Aeq%3A{0}&filter.q0=contentlocale%3Aeq%3Ada_DK%2Cde_AT%2Cde_CH%2Cde_DE%2Cen_GB%2Cen_NO%2Cen_US%2Cfi_FI%2Cfr_FR%2Cnl_BE%2Cnl_NL%2Csv_SE%2Czh_CN%2Czh_TW&sort.q0=rating%3Adesc&stats.q0=reviews&filteredstats.q0=reviews&include.q0=authors%2Cproducts%2Ccomments&filter_reviews.q0=contentlocale%3Aeq%3Ada_DK%2Cde_AT%2Cde_CH%2Cde_DE%2Cen_GB%2Cen_NO%2Cen_US%2Cfi_FI%2Cfr_FR%2Cnl_BE%2Cnl_NL%2Csv_SE%2Czh_CN%2Czh_TW&filter_reviewcomments.q0=contentlocale%3Aeq%3Ada_DK%2Cde_AT%2Cde_CH%2Cde_DE%2Cen_GB%2Cen_NO%2Cen_US%2Cfi_FI%2Cfr_FR%2Cnl_BE%2Cnl_NL%2Csv_SE%2Czh_CN%2Czh_TW&filter_comments.q0=contentlocale%3Aeq%3Ada_DK%2Cde_AT%2Cde_CH%2Cde_DE%2Cen_GB%2Cen_NO%2Cen_US%2Cfi_FI%2Cfr_FR%2Cnl_BE%2Cnl_NL%2Csv_SE%2Czh_CN%2Czh_TW&limit.q0=30&offset.q0=0&limit_comments.q0=3&callback=bv_1111_60234'''

class Harmankardon_nlSpider(AlaSpider):
    name = 'harmankardon_nl'
    allowed_domains = ['harmankardon.nl', 'bazaarvoice.com']
    start_urls = ['http://www.harmankardon.nl/sitemap']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        urls_xpath = "//div[@id='primary']//ul/li/a[not(contains(@href, 'sale'))]/@href"
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
        
        urls_xpath = "//a[@class='thumb-link']/@href"
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
            
            request = Request(single_url, callback=self.level_3)
            
             
            yield request
        urls_xpath = "//div[@class='product-row']//div[1]/a[@class='inline-button more']/@href"
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
            
            request = Request(single_url, callback=self.level_3)
            
             
            yield request
    
    def level_3(self, response):
                                     
        original_url = response.url
        
        category_leaf_xpath = "//div[@class='breadcrumb']//div[a][last()]//span/text()"
        category_path_xpath = "//div[@class='breadcrumb']//div[a]//span/text()"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
                
                "source_internal_id": "//span[@itemprop='mpn']//text()",
                
                
                "ProductName":"//h1[@class='product-name']/text()",
                
                
                
                "PicURL":"//img[@itemprop='image']/@src",
                
                
                "ProductManufacturer":"harmankardon"
                
                            }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['TestUrl'] = original_url
        picurl = product.get("PicURL", "")
        if picurl and picurl[:2] == "//":
            product["PicURL"] = "https:" + product["PicURL"]
        manuf = product.get("ProductManufacturer", "")
        if manuf == "" and "harmankardon"[:2] != "//":
            product["ProductManufacturer"] = "harmankardon"
        try:
            product["OriginalCategoryName"] = category['category_path']
        except:
            pass

        product_id = self.product_id(product)
        product_id['ID_kind'] = "mpn"
        product_id['ID_value'] = product["source_internal_id"]
        yield product_id
        

        yield product

        if product["source_internal_id"]:
            ssi_short = product["source_internal_id"].strip().lower()
            if "/" in ssi_short:
                ssi_short = ssi_short.replace(" ", "").split("/")[0]
            api_link = api_link_template.format(ssi_short)
            request = Request(api_link, callback=self.level_4)
            request.meta['ProductName'] = product['ProductName']
            request.meta['TestUrl'] = product['TestUrl']
            yield request

    def level_4(self, response):
        original_url = response.url
        pname = response.meta["ProductName"]
        test_url = response.meta["TestUrl"]
        json_string = response.body.replace('bv_1111_60234', '').strip('()')
        data = json.loads(json_string)
        results = data['BatchedResults']['q0']['Results']
        try:
            for item in results:
                review = ReviewItem()
                review['DBaseCategoryName'] = "USER"
                review['ProductName'] = pname
                review['TestUrl'] = test_url
                review['source_internal_id'] = item['ProductId']
                review['TestDateText'] = item['SubmissionTime']
                if review['TestDateText']:
                    review['TestDateText'] = date_format(review['TestDateText'], '')
                review['SourceTestRating'] = item['Rating']
                review['SourceTestScale'] = '5'
                review['Author'] = item['UserNickname']
                review['TestTitle'] = item['Title']
                review['TestSummary'] = item['ReviewText']
                review['TestPros'] = item['Pros']
                review['TestCons'] = item['Cons']
                yield review
        except:
            pass
        pass