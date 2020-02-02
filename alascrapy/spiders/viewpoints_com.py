__author__ = 'jim'

from scrapy.http import Request

from alascrapy.items import ProductItem, CategoryItem, ReviewItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url


class ViewpointsComSpider(AlaSpider):
    name = 'viewpoints_com'
    allowed_domains = ['viewpoints.com']
    start_urls = ['http://www.viewpoints.com/explore']

    def parse(self, response):
        categories = response.xpath('//ul[@class="stripped"]/li/a')

        for item in categories:
            category = CategoryItem()
            category['category_path'] = self.extract(item.xpath('./text()'))
            category['category_leaf'] = category['category_path']
            category['category_url'] = get_full_url(response, self.extract(item.xpath('./@href')))
            yield category

            if not self.should_skip_category(category):
                request = Request(url=category['category_url'], callback=self.parse_category)
                request.meta['ocn'] = category['category_path']
                yield request

    def parse_category(self, response):
        product_urls = self.extract_list(response.xpath('//h4/a/@href'))

        for product_url in product_urls:
            request = Request(url=get_full_url(response, product_url), callback=self.parse_product)
            request.meta['ocn'] = response.meta['ocn']
            yield request

        next_page_url = self.extract(response.xpath('//a[@class="next"]/@href'))
        if next_page_url:
            request = Request(url=get_full_url(response, next_page_url), callback=self.parse_category)
            request.meta['ocn'] = response.meta['ocn']
            yield request

    def parse_product(self, response):
        product = ProductItem()
        ids = self.extract_list(response.xpath('//span[@itemprop="model"]/text()'))

        product['TestUrl'] = response.url
        product['OriginalCategoryName'] = response.meta['ocn']
        product['PicURL'] = self.extract(response.xpath('//img[@class="photo"]/@src'))
        product['ProductManufacturer'] = self.extract(response.xpath('//a[@itemprop="brand"]/text()'))
        product['ProductName'] = self.extract(response.xpath('//span[@itemprop="name"]/text()'))
        yield product

        for mpn in ids:
            product_id = self.product_id(product)
            product_id['ID_kind'] = "MPN"
            product_id['ID_value'] = mpn
            yield product_id

        reviews = response.xpath('//div[@itemprop="review"]')
       
        for review in reviews:
            user_review = ReviewItem()
            user_review['DBaseCategoryName'] = "USER"
            user_review['ProductName'] = product['ProductName']
            user_review['TestUrl'] = product['TestUrl']
            user_review['TestDateText'] = self.extract(review.xpath('.//meta[@itemprop="dateCreated"]/@content'))
            user_review['SourceTestRating'] = self.extract(review.xpath('.//meta[@itemprop="ratingValue"]/@content'))
            user_review['Author'] = self.extract(review.xpath('.//span[@itemprop="author"]/text()'))
            user_review['TestSummary'] = self.extract_all(review.xpath('.//p[@itemprop="reviewBody"]/text()'))
            user_review['TestTitle'] = self.extract(review.xpath('.//p[@itemprop="name"]/text()'))
            user_review['TestPros'] = self.extract_all(review.xpath(
                    './/div[contains(@class,"pr-attribute-pros")]//li/text()'), '; ')
            user_review['TestCons'] = self.extract_all(review.xpath(
                    './/div[contains(@class,"pr-attribute-cons")]//li/text()'), '; ')
            yield user_review
