__author__ = 'jim'

from scrapy.http import Request

from alascrapy.items import ProductItem, CategoryItem, ReviewItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format


class DooyooCoUkSpider(AlaSpider):
    name = 'dooyoo_co_uk'
    allowed_domains = ['dooyoo.co.uk']
    start_urls = ['http://www.dooyoo.co.uk/category/']

    def parse(self, response):
        category_urls = self.extract_list(response.xpath('//li/ul/li/a/@href'))

        for category_url in category_urls:
            category_url = get_full_url(response, category_url)
            yield Request(url=category_url, callback=self.parse_category)

    def parse_category(self, response):
        category = CategoryItem()
        category['category_path'] = self.extract_all(response.xpath('//ul[@class="m-breadcrumb"]//text()'), " > ")
        category['category_leaf'] = self.extract(response.xpath('//ul[@class="m-breadcrumb"]/li/text()'))
        category['category_url'] = response.url
        yield category

        if not self.should_skip_category(category):
            sorted_url = response.url+'?offset=0&limit=30&sort=dateopis&dir=desc&__table=item-table&action=itemlist'
            request = Request(url=sorted_url, callback=self.parse_products)
            request.meta['category'] = category
            yield request

    def parse_products(self, response):
        product_urls = self.extract_list(response.xpath('//li/a/@href'))

        for product_url in product_urls:
            request = Request(url=get_full_url(response, product_url), callback=self.parse_product)
            request.meta['category'] = response.meta['category']
            yield request

    def parse_product(self, response):
        product = ProductItem()

        product['TestUrl'] = response.url
        product['OriginalCategoryName'] = response.meta['category']['category_path']
        product['ProductName'] = self.extract(response.xpath('//h1/text()'))
        product['PicURL'] = self.extract(response.xpath('//span/img[@itemprop="image"]/@src'))
        yield product

        reviews = response.xpath('//div[@itemprop="review"]')
       
        for review in reviews:
            user_review = ReviewItem()
            user_review['DBaseCategoryName'] = "USER"
            user_review['ProductName'] = product['ProductName']
            user_review['TestUrl'] = product['TestUrl']
            date = self.extract(review.xpath('.//span[@itemprop="dateCreated"]/text()'))
            user_review['TestDateText'] = date_format(date, '%d.%m.%Y %H:%M')
            user_review['SourceTestRating'] = self.extract(review.xpath('.//meta[@itemprop="ratingValue"]/@content'))
            user_review['Author'] = self.extract(review.xpath('.//a[@itemprop="name"]/text()'))
            user_review['TestTitle'] = self.extract(review.xpath('.//h2[@itemprop="headline"]/text()'))
            user_review['TestSummary'] = self.extract_all(review.xpath('.//div[@itemprop="text"]//text()'))
            user_review['TestPros'] = self.extract_all(review.xpath(
                './/h4[i[contains(@class,"plus")]]/following-sibling::ul[1]//text()'), '; ')
            user_review['TestCons'] = self.extract_all(review.xpath(
                './/h4[i[contains(@class,"minus")]]/following-sibling::ul[1]//text()'), '; ')
            yield user_review
