__author__ = 'jim'

from scrapy.http import Request

from alascrapy.items import ProductItem, CategoryItem, ReviewItem, ProductIdItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import date_format, get_full_url


class YopiDeSpider(AlaSpider):
    name = 'yopi_de'
    allowed_domains = ['yopi.de']
    start_urls = ['http://www.yopi.de/alle-kategorien.html']

    def parse(self, response):
        category_urls = self.extract_list(response.xpath('//div[contains(@class,"child-cats")]/a/@href'))

        for category_url in category_urls:
            yield Request(url=category_url, callback=self.parse_category)
            
    def parse_category(self, response):
        sub_category_urls = self.extract_list(response.xpath('//h3/a/@href'))
        if sub_category_urls:
            for sub_category_url in sub_category_urls:
                yield Request(url=sub_category_url, callback=self.parse_category)
        else:
            for item in self.parse_sub_category(response):
                yield item

    def parse_sub_category(self, response):
        products_xpath = "//ul[@id='product-offer-list']/li[contains(@class, 'list-item')]"
        product_url_xpath = ".//h4[@class='item-name']/a/@href"
        has_reviews_xpath = './/div[@class="rating-in-words"]/a/@href'
        category = response.meta.get('category', None)
        if not category:
            category = CategoryItem()
            category['category_path'] = self.extract_all(
                    response.xpath('//ol[@class="breadcrumb"]//span/text()'), " > ")
            category['category_leaf'] = self.extract(response.xpath('//h1/text()'))
            category['category_url'] = response.url
            yield category

        if not self.should_skip_category(category):
            products = response.xpath(products_xpath)
            for product in products:
                has_reviews = product.xpath(has_reviews_xpath)
                if not has_reviews:
                    continue

                product_url = self.extract(product.xpath(product_url_xpath))
                if product_url:
                    product_url = get_full_url(response, product_url)
                    request = Request(url=product_url, callback=self.parse_product)
                    request.meta['category'] = category
                    yield request

            next_page_url = self.extract(response.xpath('//a[@class="next_page"]/@href'))
            if next_page_url:
                next_page_url = get_full_url(response, next_page_url)
                request = Request(url=next_page_url, callback=self.parse_sub_category)
                request.meta['category'] = category
                yield request

    def parse_product(self, response):
        manufacturer_xpath = "//strong[contains(@class,'property-name') and contains(text(),'Hersteller')]/following-sibling::span/a[1]/text()"
        review_url_xpath = "//div[@id='product-head-reviews']//a[@class='headbutton']/@href"
        product = ProductItem()
        
        product['TestUrl'] = response.url
        product['OriginalCategoryName'] = response.meta['category']['category_path']
        product['ProductName'] = self.extract(response.xpath('//h1//text()'))
        product['PicURL'] = self.extract(response.xpath('//div[@class="data"]/div/img/@src'))
        product['ProductManufacturer'] = self.extract(response.xpath(manufacturer_xpath))
        yield product

        id_values = self.extract(response.xpath('//strong[contains(text(),"EAN")]/parent::div/span/text()'))
        if id_values:
            id_values = id_values.split(',')
            for id_value in id_values:
                productid = ProductIdItem()
                productid['ProductName'] = product["ProductName"]
                productid['ID_kind'] = "EAN"
                productid['ID_value'] = id_value.strip(' ')
                yield productid          

        review_url = self.extract(response.xpath(review_url_xpath))
        if review_url:
            review_url = get_full_url(response, review_url)
            request = Request(url=review_url, callback=self.parse_reviews)
            request.meta['product'] = product
            yield request



    def parse_reviews(self, response):
        product = response.meta["product"]
        reviews = response.xpath('//ul[@id="reviews-list"]/li')

        next_page_xpath = "//div[@id='review-list']/div[@class='see-more-bar']//a/@href"
       
        for review in reviews:
            user_review = ReviewItem()
            user_review['DBaseCategoryName'] = "USER"
            user_review['ProductName'] = product['ProductName']
            user_review['TestUrl'] = self.extract(review.xpath('.//h3/a/@href'))
            date = self.extract(review.xpath('.//meta[@itemprop="datePublished"]/@content'))
            if date:
                date = date[:10]
                user_review['TestDateText'] = date_format(date, "%Y-%m-%d")
            user_review['SourceTestRating'] = self.extract(review.xpath('.//span[@itemprop="reviewRating"]/@content'))
            if user_review['SourceTestRating']:
                user_review['SourceTestScale'] = 5
            user_review['Author'] = self.extract(review.xpath('.//a[@class="user-link"]//text()'))
            user_review['TestTitle'] = self.extract(review.xpath('.//h3//text()'))
            user_review['TestSummary'] = self.extract_all(
                    review.xpath('.//div[@class="review-text"]//span/span/text()'))
            user_review['TestPros'] = self.extract_all(
                    review.xpath(".//p[contains(@class, 'label-cons')]/following::p[1][not(text()='-')]/text()"))
            user_review['TestCons'] = self.extract_all(
                    review.xpath(".//p[contains(@class,'label-pros')]/following::p[1][not(text()='-')]/text()"))
            yield user_review

        next_page_url = self.extract(response.xpath(next_page_xpath))
        if next_page_url:
            request = Request(url=next_page_url, callback=self.parse_reviews)
            request.meta['product'] = product
            yield request
