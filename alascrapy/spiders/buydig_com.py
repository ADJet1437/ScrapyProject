__author__ = 'jim'

import re

from scrapy.http import Request

from alascrapy.items import ProductItem, CategoryItem, ReviewItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import date_format


class BuydigComSpider(AlaSpider):
    name = 'buydig_com'
    allowed_domains = ['buydig.com']
    start_urls = ['http://www.buydig.com/']

    def parse(self, response):
        category_urls = self.extract_list(response.xpath('//dd/ul/li/a[contains(@href,"category")]/@href'))

        for category_url in category_urls:
            yield Request(url=category_url+'?srt=reviewtotal&lmt=100', callback=self.parse_category)

    def parse_category(self, response):
        category = CategoryItem()
        category['category_path'] = self.extract(response.xpath('//div/h1/text()'))
        category['category_leaf'] = category['category_path']
        category['category_url'] = response.url
        yield category

        if not self.should_skip_category(category):
            product_urls = self.extract_list(response.xpath(
                    '//img[contains(@id,"imgAverageStarRating")]/ancestor::div[contains(@style,"auto")]/div/a/@href'))

            for product_url in product_urls:
                request = Request(url=product_url, callback=self.parse_product)
                request.meta['ocn'] = category['category_path']
                yield request

    def parse_product(self, response):
        product = ProductItem()
        mpn = self.extract(response.xpath('//span[@id="lblMfgPartNo"]/text()'))

        product['TestUrl'] = response.url
        product['OriginalCategoryName'] = response.meta['ocn']
        product['PicURL'] = self.extract(response.xpath('//meta[@itemprop="image"]/@content'))
        product['ProductManufacturer'] = self.extract(response.xpath('//meta[@itemprop="brand"]/@content'))
        product['ProductName'] = product['ProductManufacturer']+' '+mpn
        product['source_internal_id'] = self.extract(response.xpath('//span[@id="lblCatalog"]/text()'))
        yield product

        product_id = self.product_id(product)
        product_id['ID_kind'] = "MPN"
        product_id['ID_value'] = mpn
        product_id['source_internal_id'] = product['source_internal_id']
        yield product_id

        review_id = self.extract(response.xpath('//a[@name="aReviews"]/@onclick'))
        id_match = re.findall(r"','([\d]+)'", review_id)
        review_url = 'http://www.buydig.com/shop/productreviews.aspx?sku=&pageid=%s&srt=DateNew&lmt=50' % id_match[0]
        request = Request(url=review_url, callback=self.parse_reviews)
        request.meta['product'] = product
        yield request

    def parse_reviews(self, response):
        reviews = response.xpath('//div[@id="Reviews_box"]/div[child::b]')
       
        for review in reviews:
            name = self.extract(review.xpath('./span[contains(text(),"Review submitted for")]/text()'))
            if response.meta['product']['source_internal_id'] in name:
                user_review = ReviewItem()
                user_review['DBaseCategoryName'] = "USER"
                user_review['ProductName'] = response.meta['product']['ProductName']
                user_review['TestUrl'] = response.meta['product']['TestUrl']
                user_review['source_internal_id'] = response.meta['product']['source_internal_id']
                date = self.extract(review.xpath('./div[@class="sep"][1]/following::text()[1]'))
                date_list = date.split('\r\n')
                user_review['TestDateText'] = date_format(date_list[-1], '')
                rate = self.extract(review.xpath('./img[contains(@title,"stars")]/@title'))
                rate_match = re.findall(r'([\d]) out of', rate)
                user_review['SourceTestRating'] = rate_match[0]
                author_match = re.findall(r'By ([^()]+)', date_list[0])
                if author_match:
                    user_review['Author'] = author_match[0]
                user_review['TestSummary'] = self.extract(review.xpath(
                        './b[contains(text(),"Comments")]/following::text()[1]'))
                user_review['TestTitle'] = self.extract(review.xpath('./b[1]/text()'))
                user_review['TestPros'] = self.extract(review.xpath(
                        './b[contains(text(),"Pros")]/following::text()[1]'))
                user_review['TestCons'] = self.extract(review.xpath(
                        './b[contains(text(),"Cons")]/following::text()[1]'))
                yield user_review
