__author__ = 'jim'

import re

from scrapy.http import Request

from alascrapy.items import ProductItem, CategoryItem
from alascrapy.lib.selenium_browser import SeleniumBrowser, uses_selenium
from alascrapy.spiders.base_spiders.bazaarvoice_spider import BazaarVoiceSpider
from alascrapy.lib.generic import get_full_url

#TODO: FIX
class CdwComSpider(BazaarVoiceSpider):
    name = 'cdw_com'
    allowed_domains = ['cdw.com']
    start_urls = ['https://www.cdw.com/shop/search/browse.aspx']

    def parse(self, response):
        level_2_category_urls = self.extract_list(response.xpath(
                '//div[contains(@class,"ContainerTopRow")]/div[contains(@class,"SecondLevelInner")]/a/@href'))
        level_3_category_urls = self.extract_list(response.xpath('//div[contains(@class,"ThirdLevel")]/a/@href'))
        
        category_urls = level_2_category_urls + level_3_category_urls
        for category_url in category_urls:
            category_url = get_full_url(response, category_url)
            request = Request(url=category_url, callback=self.parse_category)
            yield request
        
    def parse_category(self, response):
        category = None

        if "category" in response.meta:
            category = response.meta['category']

        if not category:
            category = CategoryItem()
            category['category_path'] = self.extract_all(
                    response.xpath('//div[@class="breadCrumbsRow"]//a/text()'), ' > ')
            category['category_leaf'] = self.extract(
                    response.xpath('//div[@class="breadCrumbsRow"]/div[last()]/a/text()'))
            category['category_url'] = response.url
            yield category
            
        if not self.should_skip_category(category):
            product_urls = self.extract_list(response.xpath('//a[@id="lblReviewLinkInline"]/@href'))
            for product_url in product_urls:
                product_url = product_url.split('?')
                request = self.selenium_request(url=get_full_url(response, product_url[0]), callback=self.parse_product)
                request.meta['category'] = category
                yield request
            
            next_page = self.extract_list(response.xpath('//a[@title="NEXT"]/@href'))
            if next_page:
                request_url = get_full_url(response, next_page[0])
                request = Request(url=request_url, callback=self.parse_category)
                request.meta['category'] = category
                yield request

    @uses_selenium
    def parse_product(self, response):
        category = response.meta['category']
        
        product = ProductItem()
        product['TestUrl'] = response.url
        product['OriginalCategoryName'] = category['category_path']
        name = self.extract(response.xpath('//h1/span/text()'))
        name_match = re.findall(r'[^()]+', name)
        product['ProductName'] = name_match[0]
        pic_url = self.extract(response.xpath('//div[@class="main-image"]/img/@src'))
        if pic_url:
            product['PicURL'] = get_full_url(response, pic_url)
        product['ProductManufacturer'] = self.extract(response.xpath('//span[@class="brand"]/text()'))
        product['source_internal_id'] = self.extract(
                response.xpath('//body[@id="MasterPageBodyTag"]/@data-productcode'))
        yield product
        
        mpn = self.extract(response.xpath('//span[contains(text(),"Mfg")]/span/text()'))
        if mpn:
            mpn_id = self.product_id(product)
            mpn_id['ID_kind'] = "MPN"
            mpn_id['ID_value'] = mpn
            yield mpn_id
            
        product_id = self.product_id(product)
        product_id['ID_kind'] = "cdw_id"
        product_id['ID_value'] = product['source_internal_id']
        yield product_id

        with SeleniumBrowser(self, response) as browser:
            selector = browser.get(response.url, timeout=10)

            response.meta['browser'] = browser
            response.meta['product'] = product
            response.meta['product_id'] = product_id
            response.meta['_been_in_decorator'] = True

            for review in self.parse_reviews(response, selector, incremental=True):
                yield review
