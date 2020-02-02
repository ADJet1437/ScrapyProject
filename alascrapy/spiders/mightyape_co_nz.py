__author__ = 'jim'

from scrapy.http import Request

from alascrapy.items import ProductItem, CategoryItem, ReviewItem, ProductIdItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format


class MightyapeCoNzSpider(AlaSpider):
    name = 'mightyape_co_nz'
    allowed_domains = ['mightyape.co.nz']
    start_urls = ['https://www.mightyape.co.nz/Computers', 'https://www.mightyape.co.nz/Electronics']

    def parse(self, response):
        category_urls = self.extract_list(response.xpath('//table[@class="menuColumns"]//li/a/@href'))

        for category_url in category_urls:
            category_url = get_full_url(response, category_url)
            yield Request(url=category_url, callback=self.parse)

        if category_urls:
            return

        category = None

        if "category" in response.meta:
            category = response.meta['category']

        if not category:
            category = CategoryItem()
            category['category_path'] = self.extract_all(response.xpath('//div[@class="breadcrumb"]//text()'))
            category['category_leaf'] = self.extract(response.xpath('//h1/text()'))
            category['category_url'] = response.url
            yield category

        if not self.should_skip_category(category):
            product_urls = self.extract_list(response.xpath('//div[@class="product"]/div[@class="title"]/a/@href'))
            for product_url in product_urls:
                product_url = get_full_url(response, product_url)
                request = Request(url=product_url, callback=self.parse_product)
                request.meta['category'] = category
                yield request

            next_page = self.extract(response.xpath('//a[@rel="next"]/@href'))
            if next_page:
                request = Request(url=get_full_url(response, next_page), callback=self.parse)
                request.meta['category'] = category
                yield request

    def parse_product(self, response):
        reviews = response.xpath('//div[@class="review"]')
        if reviews:
            product = None

            if "product" in response.meta:
                product = response.meta['product']

            if not product:
                product = ProductItem()

                product['TestUrl'] = response.url
                product['OriginalCategoryName'] = response.meta['category']['category_path']
                product['ProductName'] = self.extract(response.xpath('//span[@itemprop="name"]/text()'))
                product['PicURL'] = self.extract(response.xpath('//div[@class="main-image"]/a/img/@src'))
                product['ProductManufacturer'] = self.extract(response.xpath('//div[@itemprop="brand"]//a/text()'))
                if not product['ProductManufacturer']:
                    product['ProductManufacturer'] = self.extract_all(response.xpath(
                        '//div[@class="label"][contains(text(),"Developer")]'
                        '/following-sibling::div[@class="value"]//text()'))
                yield product

                mpn = self.extract(response.xpath(
                    '//div[@class="label"][contains(text(),"Manufacturer")]'
                    '/following-sibling::div[@class="value"]/text()'))
                if mpn:
                    product_id = ProductIdItem()
                    product_id['ProductName'] = product["ProductName"]
                    product_id['ID_kind'] = "MPN"
                    product_id['ID_value'] = mpn
                    yield product_id

                review_url = self.extract(response.xpath('//a[@class="more"]/@href'))
                if review_url:
                    review_url = get_full_url(response, review_url)
                    request = Request(url=review_url, callback=self.parse_product)
                    request.meta['product'] = product
                    yield request
                    return

            for review in reviews:
                user_review = ReviewItem()
                user_review['DBaseCategoryName'] = "USER"
                user_review['ProductName'] = product['ProductName']
                user_review['TestUrl'] = product['TestUrl']
                date = self.extract(review.xpath('.//div[@class="author"]/text()[last()]'))
                user_review['TestDateText'] = date_format(date, '')
                rating = self.extract(review.xpath('.//span[@class="ratingImage"]/img/@alt'))
                user_review['SourceTestRating'] = rating.split(' ')[0]
                user_review['Author'] = self.extract(review.xpath('.//div[@class="author"]/b/text()'))
                user_review['TestTitle'] = self.extract(review.xpath('.//div[@class="title"]/text()[last()]'))
                user_review['TestSummary'] = self.extract_all(review.xpath('.//div[@class="body"]//text()'))
                yield user_review
