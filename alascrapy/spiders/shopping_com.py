__author__ = 'jim'

import re

from scrapy.http import Request

from alascrapy.items import ProductItem, CategoryItem, ReviewItem, ProductIdItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format


class ShoppingComSpider(AlaSpider):
    name = 'shopping_com'
    allowed_domains = ['shopping.com']
    start_urls = ['http://www.shopping.com/xSN']

    def parse(self, response):
        category_urls = self.extract_list(response.xpath('//h3/following::ul//@href'))

        for category_url in category_urls:
            url_match = re.findall(r'xFA-(^"")+~FD', category_url)
            if url_match:
                category_url = 'http://www.shopping.com/' + url_match[0] + '/products~S-214~OR-1'
                yield Request(url=category_url, callback=self.parse_category)

    def parse_category(self, response):
        category = None

        if "category" in response.meta:
            category = response.meta['category']

        if not category:
            category = CategoryItem()
            category['category_path'] = self.extract_all(
                response.xpath('//div[@class="breadCrumb"]//span/text()'), " > ")
            category['category_leaf'] = self.extract(response.xpath('//h1/span/text()'))
            category['category_url'] = response.url
            yield category

        if not self.should_skip_category(category):
            products = response.xpath('//div[contains(@id,"quickLookItem")]')
            for product in products:
                has_reviews = product.xpath('.//span[@class="numReviews"]')
                if has_reviews:
                    product_url = self.extract(product.xpath('.//h2/a/@href'))
                    product_url = get_full_url(response, product_url)
                    request = Request(url=product_url, callback=self.parse_product)
                    request.meta['category'] = category
                    yield request

            next_page_url = self.extract(response.xpath('//span[@class="paginationNext"]/a/@href'))
            if next_page_url and response.xpath('//div[contains(@id,"quickLookItem")][40]//span[@class="numReviews"]'):
                next_page_url = get_full_url(response, next_page_url)
                request = Request(url=next_page_url, callback=self.parse_category)
                request.meta['category'] = category
                yield request

    def parse_product(self, response):
        review_urls = self.extract_list(response.xpath('//a[@class="readFullReviewLink"]/@href'))
        if review_urls:
            product = ProductItem()

            product['TestUrl'] = response.url
            product['OriginalCategoryName'] = response.meta['category']['category_path']
            product['ProductName'] = self.extract(response.xpath('//h1/text()'))
            product['PicURL'] = self.extract(response.xpath('//div[@class="enlargeText"]/a/@href'))
            yield product

            upc = self.extract(response.xpath('//td[contains(text(),"UPC")]/parent::tr/td[@class=""]/text()'))
            if upc:
                product_id = ProductIdItem()
                product_id['ProductName'] = product["ProductName"]
                product_id['ID_kind'] = "UPC"
                product_id['ID_value'] = upc
                yield product_id

            mpn = self.extract(response.xpath('//td[contains(text(),"MPN")]/parent::tr/td[@class=""]/text()'))
            if mpn:
                product_id = ProductIdItem()
                product_id['ProductName'] = product["ProductName"]
                product_id['ID_kind'] = "MPN"
                product_id['ID_value'] = mpn
                yield product_id

            for review_url in review_urls:
                review_url = get_full_url(response, review_url.strip('#tabAnchor'))
                request = Request(url=review_url, callback=self.parse_review)
                request.meta['product'] = product
                yield request
        
    def parse_review(self, response):
        product = response.meta['product']

        user_review = ReviewItem()
        user_review['DBaseCategoryName'] = "USER"
        user_review['ProductName'] = product['ProductName']
        user_review['TestUrl'] = response.url
        date = self.extract(response.xpath('//span[@class="dtreviewed"]/span[@class="value-title"]/@title'))
        if date:
            user_review['TestDateText'] = date_format(date, '')
        rating = self.extract(response.xpath('//div[@class="contentBox"]//a[contains(@class,"iReviewStars")]/@title'))
        rating = re.findall(r'[^"]+ star', rating)
        user_review['SourceTestRating'] = rating[0]
        user_review['Author'] = self.extract(response.xpath('//a[@class="memberName"]/text()'))
        user_review['TestTitle'] = self.extract(response.xpath('//h3[contains(@class,"reviewTitle")]/text()'))
        user_review['TestSummary'] = self.extract_all(response.xpath('//div[contains(@class,"reviewText")]//text()'))
        user_review['TestPros'] = self.extract_all(response.xpath('//span[@class="reviewPros"]/parent::div/text()'))
        user_review['TestCons'] = self.extract_all(response.xpath('//span[@class="reviewCons"]/parent::div/text()'))
        yield user_review
