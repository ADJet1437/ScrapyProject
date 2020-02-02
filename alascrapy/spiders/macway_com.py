__author__ = 'jim'

from scrapy.http import Request

from alascrapy.items import ProductItem, CategoryItem, ReviewItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format


class MacwayComSpider(AlaSpider):
    name = 'macway_com'
    allowed_domains = ['macway.com']
    start_urls = ['http://www.macway.com/fr/']

    def parse(self, response):
        category_urls = self.extract_list(response.xpath(
            '//a[contains(@class,"menuitems")][not(contains(@class,"title"))]/@href'))

        for category_url in category_urls:
            category_url = get_full_url(response, category_url)
            yield Request(url=category_url, callback=self.parse_category)

    def parse_category(self, response):
        category = None

        if "category" in response.meta:
            category = response.meta['category']

        if not category:
            category = CategoryItem()
            category['category_path'] = self.extract_all(response.xpath('//nav[@id="breadcrumb"]//text()'), " > ")
            category['category_leaf'] = self.extract(response.xpath(
                '//nav[@id="breadcrumb"]//span[@class="current"]/text()'))
            category['category_url'] = response.url
            yield category

        if not self.should_skip_category(category):
            product_urls = self.extract_list(response.xpath(
                '//li[@class="product"]/div[@class="product-reviews"][span]/a/@href'))
            for product_url in product_urls:
                product_url = get_full_url(response, product_url).replace('#reviews-anchor', '')
                request = Request(url=product_url, callback=self.parse_product)
                request.meta['category'] = category
                yield request

    def parse_product(self, response):
        product = ProductItem()

        product['TestUrl'] = response.url
        product['OriginalCategoryName'] = response.meta['category']['category_path']
        product['ProductName'] = self.extract(response.xpath('//h1/text()'))
        pic_url = self.extract(response.xpath('//div[@class="product-carousel"]//img[@itemprop="image"][1]/@src'))
        product['PicURL'] = get_full_url(response, pic_url)
        product['ProductManufacturer'] = self.extract(response.xpath(
            '//td[text()="Constructeur"]/following-sibling::td/text()'))
        yield product

        reviews = response.xpath('//li[@itemprop="review"]')
       
        for review in reviews:
            user_review = ReviewItem()
            user_review['DBaseCategoryName'] = "USER"
            user_review['ProductName'] = product['ProductName']
            user_review['TestUrl'] = product['TestUrl']
            date = self.extract(review.xpath('.//span[@itemprop="datePublished"]/text()'))
            user_review['TestDateText'] = date_format(date, '%d/%m/%Y')
            user_review['SourceTestRating'] = self.extract(review.xpath('.//span[@itemprop="ratingValue"]/text()'))
            user_review['Author'] = self.extract(review.xpath('.//span[@itemprop="author"]/text()'))
            user_review['TestTitle'] = self.extract(review.xpath('.//div[@itemprop="name"]/text()'))
            user_review['TestSummary'] = self.extract_all(review.xpath('.//blockquote/text()'))
            yield user_review
