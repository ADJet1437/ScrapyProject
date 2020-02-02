__author__ = 'jim'

from scrapy.http import Request

from alascrapy.items import ProductItem, CategoryItem, ReviewItem, ProductIdItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format


class FlipkartComSpider(AlaSpider):
    name = 'flipkart_com'
    allowed_domains = ['flipkart.com']
    start_urls = ['http://www.flipkart.com/mobiles-accessories/pr?sid=tyy',
                  'http://www.flipkart.com/wearable-smart-devices/pr?sid=ajy',
                  'http://www.flipkart.com/automation-robotics/pr?sid=igc',
                  'http://www.flipkart.com/computers/pr?sid=6bo',
                  'http://www.flipkart.com/home-entertainment/pr?sid=ckf',
                  'http://www.flipkart.com/home-kitchen/pr?sid=j9e',
                  'http://www.flipkart.com/beauty-and-personal-care/pr?sid=t06',
                  'http://www.flipkart.com/cameras-accessories/pr?sid=jek',
                  'http://www.flipkart.com/gaming/pr?sid=4rr']

    def parse(self, response):
        category_urls = self.extract_list(response.xpath('//li[@class="store"]/a/@href'))

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
            category['category_path'] = self.extract_all(response.xpath('//div[@id="breadcrumb"]//text()'))
            category['category_leaf'] = self.extract(response.xpath('//h1/text()'))
            category['category_url'] = response.url
            yield category

        if not self.should_skip_category(category):
            product_urls = self.extract_list(response.xpath(
                '//div[@class="pu-rating"]/preceding-sibling::div[contains(@class,"pu-title")]/a/@href'))
            for product_url in product_urls:
                product_url = get_full_url(response, product_url)
                request = Request(url=product_url, callback=self.parse_product)
                request.meta['category'] = category
                yield request

            next_page_url = self.extract(response.xpath('//a[@class="next"]/@href'))
            if next_page_url:
                next_page_url = get_full_url(response, next_page_url)
                request = Request(url=next_page_url, callback=self.parse)
                request.meta['category'] = category
                yield request

    def parse_product(self, response):
        product = ProductItem()

        product['TestUrl'] = response.url
        product['OriginalCategoryName'] = response.meta['category']['category_path']
        product['ProductName'] = self.extract(response.xpath('//h1/text()'))
        product['PicURL'] = self.extract(response.xpath('//div[@class="imgWrapper"]/img[1]/@data-src'))
        product['ProductManufacturer'] = self.extract(response.xpath(
            '//td[@class="specsKey"][contains(text(),"Brand")]/following-sibling::td[@class="specsValue"]/text()'))
        sii = self.extract(response.xpath('//div/@data-item-id'))
        product['source_internal_id'] = sii.split('#')[0]
        yield product

        id_value = self.extract(response.xpath(
            '//td[@class="specsKey"][contains(text(),"Model ID")]/following-sibling::td[@class="specsValue"]/text()'))
        if id_value:
            product_id = ProductIdItem()
            product_id['ProductName'] = product["ProductName"]
            product_id['ID_kind'] = "MPN"
            product_id['ID_value'] = id_value
            yield product_id

        review_url = self.extract(response.xpath('//a[text()="Show ALL"]/@href'))
        review_url = get_full_url(response, review_url+'&sort=most_recent')
        request = Request(url=review_url, callback=self.parse_reviews)
        request.meta['product'] = product
        yield request
        
    def parse_reviews(self, response):
        product = response.meta['product']
        reviews = response.xpath('//div[@review-id]')
       
        for review in reviews:
            user_review = ReviewItem()
            user_review['DBaseCategoryName'] = "USER"
            user_review['ProductName'] = product['ProductName']
            user_review['source_internal_id'] = product['source_internal_id']
            test_url = self.extract(review.xpath('.//a[text()="Permalink"]/@href'))
            user_review['TestUrl'] = get_full_url(response, test_url)
            date = self.extract(review.xpath('.//div[contains(@class,"date")]/text()'))
            user_review['TestDateText'] = date_format(date, '')
            rating = self.extract(review.xpath('.//div[@class="fk-stars"]/@title'))
            user_review['SourceTestRating'] = rating.split(' ')[0]
            user_review['Author'] = self.extract(review.xpath('.//a[@profile_name]/text()'))
            if not user_review['Author']:
                user_review['Author'] = self.extract(review.xpath('.//span[contains(@class,"username")]/text()'))
            user_review['TestTitle'] = self.extract(review.xpath('./div/div/strong/text()'))
            user_review['TestSummary'] = self.extract_all(review.xpath('.//span[@class="review-text"]//text()'))
            yield user_review
