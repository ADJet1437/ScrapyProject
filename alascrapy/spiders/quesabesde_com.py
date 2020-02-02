__author__ = 'jim'

from scrapy.http import Request

from alascrapy.items import ProductItem, ReviewItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format


class QuesabesdeComSpider(AlaSpider):
    name = 'quesabesde_com'
    allowed_domains = ['quesabesde.com']
    start_urls = ['http://www.quesabesde.com/']

    def parse(self, response):
        category_urls = self.extract_list(
                response.xpath('//ul[@class="products"]/li[@class!="rounded-bottom"]/a/@href'))

        for category_url in category_urls:
            yield Request(url=category_url+'/con_opi/1', callback=self.parse_category)

    def parse_category(self, response):
        product_urls = self.extract_list(response.xpath('//h2/a/@href'))
        for product_url in product_urls:
            request = Request(url=product_url, callback=self.parse_product)
            yield request
            
        next_page_url = self.extract(response.xpath('//a[@class="page-next"]/@href'))
        if next_page_url:
            request = Request(url=next_page_url, callback=self.parse_category)
            yield request

    def parse_product(self, response):
        product = ProductItem()

        product['TestUrl'] = response.url
        product['OriginalCategoryName'] = self.extract(response.xpath('//div[@id="box_producto"]/h4/text()'))
        product['ProductName'] = self.extract_all(response.xpath('//h1//text()'))
        product['PicURL'] = self.extract(response.xpath('//div[@class="image-container"]//img/@src'))
        product['ProductManufacturer'] = self.extract(response.xpath('//h1/strong/text()'))
        yield product

        review_url = response.url + '/opiniones'
        request = Request(url=review_url, callback=self.parse_reviews)
        request.meta['product'] = product
        yield request
        
    def parse_reviews(self, response):
        product = response.meta['product']
        review_urls = self.extract_list(response.xpath('//div[contains(@id,"opinion")]/a/@href'))
        for review_url in review_urls:
            review_url = get_full_url(response, review_url)
            request = Request(url=review_url, callback=self.parse_user_review)
            request.meta['product'] = product
            yield request
        
    def parse_user_review(self, response):
        product = response.meta['product']
        
        user_review = ReviewItem()
        user_review['DBaseCategoryName'] = "USER"
        user_review['ProductName'] = product['ProductName']
        user_review['TestUrl'] = response.url
        date = self.extract(
                response.xpath('//div[@class="label_container"]/span[contains(@class,"gray_label")]/text()'))
        if date:
            user_review['TestDateText'] = date_format(date, '')
        user_review['SourceTestRating'] = self.extract(response.xpath('//span[@class="number-rating-big"]/text()'))
        user_review['Author'] = self.extract(response.xpath('//div[@id="user-badge"]//span[@class="username"]/text()'))
        user_review['TestTitle'] = self.extract(response.xpath('//h2/text()'))
        user_review['TestSummary'] = self.extract_all(response.xpath('//div[@id="HOTWordsTxt"]//text()'))
        yield user_review
