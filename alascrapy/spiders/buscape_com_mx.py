__author__ = 'jim'

import re

from scrapy.http import Request

from alascrapy.items import ProductItem, CategoryItem, ReviewItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import date_format


class BuscapeComMxSpider(AlaSpider):
    name = 'buscape_com_mx'
    allowed_domains = ['buscape.com.mx']
    start_urls = ['http://www.buscape.com.mx/']

    def parse(self, response):
        sub_category_urls = self.extract_list(response.xpath('//h3/a/@href'))

        for sub_category_url in sub_category_urls:
            yield Request(url=sub_category_url, callback=self.parse_sub_category)

    def parse_sub_category(self, response):
        category_urls = self.extract_list(response.xpath('//ul[@class="list"]/li/a/@href'))

        for category_url in category_urls:
            yield Request(url=category_url, callback=self.parse_category)
            
    def parse_category(self, response):
        category = None

        if "category" in response.meta:
            category = response.meta['category']

        if not category:
            category = CategoryItem()
            category['category_path'] = self.extract_all(
                    response.xpath('//nav/div/div[@class="content"]//text()'))
            category['category_leaf'] = self.extract(
                    response.xpath('//nav/div/div[@class="content"]/span[@class="active"]/text()'))
            category['category_url'] = response.url
            yield category

        if not self.should_skip_category(category):
            products = response.xpath('//li[@id]')
            for product in products:
                no_rates = product.xpath('.//a[contains(@class,"no-rates")]')
                if not no_rates:
                    product_url = self.extract(product.xpath('./a/@href'))
                    request = Request(url=product_url, callback=self.parse_product)
                    request.meta['category'] = category
                    yield request
                    
            next_page_url = self.extract(response.xpath('//li[@class="next"]/a/@href'))
            if next_page_url:
                request = Request(url=next_page_url, callback=self.parse_category)
                request.meta['category'] = category
                yield request

    def parse_product(self, response):
        product = ProductItem()

        product['TestUrl'] = response.url
        product['OriginalCategoryName'] = response.meta['category']['category_path']
        product['ProductName'] = self.extract(response.xpath('//h1/text()'))
        product['PicURL'] = self.extract(response.xpath('//div[@class="images"]/a/img/@src'))
        product['ProductManufacturer'] = self.extract(
                response.xpath('//span[text()="Marca"]/parent::li/span[@class="value"]/text()'))
        product['source_internal_id'] = self.extract(response.xpath('//input[@id="prodId"]/@value'))
        yield product

        reviews = response.xpath('//article[@itemscope]')
       
        for review in reviews:
            user_review = ReviewItem()
            user_review['DBaseCategoryName'] = "USER"
            user_review['ProductName'] = product['ProductName']
            user_review['source_internal_id'] = product['source_internal_id']
            user_review['TestUrl'] = product['TestUrl']
            date = self.extract(review.xpath('.//div[@class="date"]/text()'))
            date_match = re.findall(r'[\d/]{10}', date)
            if date_match:
                user_review['TestDateText'] = date_format(date_match[0], "%d/%m/%Y")
            user_review['SourceTestRating'] = self.extract(review.xpath('.//span[@itemprop="ratingValue"]/text()'))
            user_review['Author'] = self.extract(review.xpath('.//h2/a/text()'))
            user_review['TestTitle'] = self.extract(review.xpath('.//h3/a/text()'))
            user_review['TestSummary'] = self.extract_all(review.xpath('.//p[@itemprop="reviewBody"]/text()'))
            user_review['TestPros'] = self.extract_all(review.xpath('.//div[@class="pro"]//li/text()'), '; ')
            user_review['TestCons'] = self.extract_all(review.xpath('.//div[@class="con"]//li/text()'), '; ')
            yield user_review
