__author__ = 'jim'

from scrapy.http import Request

from alascrapy.items import ProductItem, ReviewItem, ProductIdItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format


class SonyComSpider(AlaSpider):
    name = 'sony_com'
    allowed_domains = ['www.sony.com']
    start_urls = ['http://www.sony.com/all-electronics']

    def parse(self, response):
        category_urls = self.extract_list(response.xpath(
            '//ul[@class="products-list-main"]/li[@class="products-li"]/a/@href'))

        for category_url in category_urls:
            category_url = get_full_url(response, category_url)
            yield Request(url=category_url, callback=self.parse_category)

    def parse_category(self, response):
        products = response.xpath('//div[@class="container"]/div[contains(@class,"products")]/a')
        for product in products:
            has_reviews = product.xpath('.//div[@data-stars]')
            if has_reviews:
                product_url = self.extract(product.xpath('./@href'))
                product_url = get_full_url(response, product_url)
                request = Request(url=product_url, callback=self.parse_product)
                yield request

    def parse_product(self, response):
        product = ProductItem()

        product['TestUrl'] = response.url
        product['OriginalCategoryName'] = self.extract(response.xpath('//a[contains(@class,"breadcrumb")]/text()'))
        model = self.extract(response.xpath('//span[@itemprop="model"]/text()'))
        pic_url = self.extract(response.xpath('//meta[@name="analytics-product-image_url"]/@content'))
        if pic_url:
            product['PicURL'] = get_full_url(response, pic_url)
        product['ProductManufacturer'] = 'Sony'
        product['ProductName'] = product['ProductManufacturer'] + ' ' + model
        yield product

        id_values = self.extract(response.xpath('//@data-model_ids'))
        if id_values:
            id_values = id_values.strip('[').strip(']').split(',')
            for id_value in id_values:
                product_id = ProductIdItem()
                product_id['ProductName'] = product["ProductName"]
                product_id['ID_kind'] = "MPN"
                product_id['ID_value'] = id_value
                yield product_id

        review_url = response.url + '/reviews-ratings'
        request = Request(url=review_url, callback=self.parse_reviews)
        request.meta['product'] = product
        yield request

    def parse_reviews(self, response):
        product = response.meta['product']
        reviews = response.xpath('//div[@id="ReviewsListings"]/div')

        for review in reviews:
            user_review = ReviewItem()
            user_review['DBaseCategoryName'] = "USER"
            user_review['ProductName'] = product['ProductName']
            user_review['TestUrl'] = product['TestUrl']
            date = self.extract(review.xpath('.//span[contains(@class,"date")]/text()'))
            user_review['TestDateText'] = date_format(date, "%d/%m/%Y")
            user_review['SourceTestRating'] = self.extract(review.xpath('.//@data-stars'))
            user_review['Author'] = self.extract(review.xpath('.//span[contains(@class,"nickname")]/text()'))
            user_review['TestTitle'] = self.extract(review.xpath('.//h4/text()'))
            user_review['TestSummary'] = self.extract_all(
                review.xpath('.//p[@itemprop="description"]/text() | .//span[@class="more-content"]/span/text()'))
            yield user_review
