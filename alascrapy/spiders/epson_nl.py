# -*- coding: utf8 -*-
from datetime import datetime
import re

from scrapy.http import Request
from scrapy.selector import Selector

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import CategoryItem, ProductItem, ReviewItem, ProductIdItem
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from alascrapy.lib.selenium_browser import SeleniumBrowser
from alascrapy.spiders.base_spiders.bazaarvoice_spiderAPI5_5 import BazaarVoiceSpiderAPI5_5


class Epson_nlSpider(BazaarVoiceSpiderAPI5_5):
    name = 'epson_nl'
    allowed_domains = ['epson.nl']
    start_urls = ['http://www.epson.nl/nl/nl/viewcon/corporatesite/search/ajax?limit=348&type=product%2Cinksymbol&offset=0&sort=launched_dt%3Adesc&filter_count=0&filter=product&current=1']

    
    def parse(self, response):
                                     
        original_url = response.url

        regx = r'"link_s":"\\/viewcon\\/corporatesite\\/products\\/mainunits\\/overview\\/\d+"'
        urls_regx = re.compile(regx)
        urls = re.findall(urls_regx,response.body)

        for single_url in urls:
            single_url = '/nl/nl' + single_url.replace('"link_s":"', '').replace('\\', '').strip('"')
            single_url = get_full_url(original_url, single_url)
            request = Request(single_url, callback=self.level_2)
             
            yield request

    
    def level_2(self, response):
                                     
        original_url = response.url
        
        category_leaf_xpath = "//div[@class='breadcrumb']//li[last()-1]//text()"
        category_path_xpath = "//div[@class='breadcrumb']//li//text()"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
                
                "source_internal_id": "//div[@class='sku']//text()",
                
                
                "ProductName":"//div[@class='breadcrumb']//li[last()]//text()",
                
                
                
                "PicURL":"//figure[@class='hero-image']/img/@src",
                
                
                "ProductManufacturer":"epson"
                
                            }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['TestUrl'] = original_url
        picurl = product.get("PicURL", "")
        if picurl and picurl[:2] == "//":
            product["PicURL"] = "https:" + product["PicURL"]
        if picurl and picurl[:1] == "/":
            product["PicURL"] = get_full_url(original_url, picurl)
        manuf = product.get("ProductManufacturer", "")
        if manuf == "" and "epson"[:2] != "//":
            product["ProductManufacturer"] = "epson"
        try:
            product["OriginalCategoryName"] = category['category_path']
        except:
            pass

        matches = None
        if product["source_internal_id"]:
            matches = re.search("SKU: (.+)", product["source_internal_id"], re.IGNORECASE)
        if matches:
            product["source_internal_id"] = matches.group(1)

        yield product
                                    

        product_id = self.product_id(product)
        product_id['ID_kind'] = "sku"
        product_id['ID_value'] = product["source_internal_id"]
        yield product_id

        review_link_xpath = "//a[contains(@href, 'writereview.htm')]/@href"
        review_link = self.extract(response.xpath(review_link_xpath))
        review_link = review_link.replace('writereview.htm', 'reviews.htm')
        request = Request(url=review_link, callback=self.parse_reviews)
        request.meta['product'] = product
        request.meta['product_id'] = product_id
        yield request
