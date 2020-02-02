# -*- coding: utf8 -*-
from datetime import datetime
import re

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

review_link_template = 'http://h30379.www3.hp.com/8844-nl_nl/%s/reviews.htm'


class Hp_nlSpider(BVNoSeleniumSpider):
    name = 'hp_nl'
    allowed_domains = ['hp.com']
    start_urls = ['http://store.hp.com/NetherlandsStore/Merch/Offer.aspx']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        urls_xpath = "//div[h4[contains(text(), 'Producten')]]//li[contains(@class, 'menu-link-list')]/a/@href"
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

        matches, category = None, None
        matches = re.search(".+(sel=.{3}).+", original_url, re.IGNORECASE)
        if matches:
            category = matches.group(1)
        
        product_list_xpath = "//div[@class='product']"
        product_list = response.xpath(product_list_xpath)
        rating_xpath = ".//div[@class='product__rating']"
        product_url_xpath = ".//div[contains(@class, 'product__title')]/h3/a/@href"
        for product in product_list:
            rating = self.extract(product.xpath(rating_xpath))
            if rating:
                product_url = self.extract(product.xpath(product_url_xpath))
                product_url = 'http://store.hp.com/NetherlandsStore/Merch/' + product_url
                request = Request(product_url, callback=self.level_3)
                yield request

        url_xpath = "//li[@class='pagination__item '][last()]/a/@href"
        single_url = self.extract(response.xpath(url_xpath))
        if single_url and category:
            single_url = 'http://store.hp.com/NetherlandsStore' + single_url
            #website error: all categories use 'NTB' 
            single_url = single_url.replace('sel=NTB', category)
            request = Request(single_url, callback=self.level_2)
            yield request
    
    def level_3(self, response):
                                     
        original_url = response.url
        
        category_leaf_xpath = "//li[contains(@class, 'breadcrumbs-list')][not(contains(@class, 'last'))][last()]//a/text()"
        category_path_xpath = "//li[contains(@class, 'breadcrumbs-list')][not(contains(@class, 'last'))]//a/text()"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
                
                "source_internal_id": "//div[contains(@class, 'write-btn')]/a/@href",
                
                
                "ProductName":"//h1[contains(@class, 'product__name')]/text()",
                
                
                
                "PicURL":"//div[contains(@class, 'product__image')]/img/@src",
                
                
                "ProductManufacturer":"//div[contains(@class, 'brand')]//meta[@itemprop='name']/@content"
                
                            }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['TestUrl'] = original_url
        try:
            product["OriginalCategoryName"] = category['category_path']
        except:
            pass

        matches = None
        if product["source_internal_id"]:
            matches = re.search(".+_nl/(.+)/writereview.+", product["source_internal_id"], re.IGNORECASE)
        if matches:
            product["source_internal_id"] = matches.group(1)
                                    

        yield product

        if product["source_internal_id"]:
            review_link = review_link_template % (product["source_internal_id"])
            request = Request(review_link, callback=self.parse_reviews)
            request.meta['product'] = product
            yield request
