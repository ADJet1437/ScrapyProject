__author__ = 'jim'

from scrapy.http import Request

from alascrapy.items import ProductItem, CategoryItem, ReviewItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format


class PrisjaktNuSpider(AlaSpider):
    name = 'prisjakt_nu'
    allowed_domains = ['prisjakt.nu']
    start_urls = ['http://www.prisjakt.nu/']

    def parse(self, response):
        category_urls = self.extract_list(
                response.xpath('//ul[contains(@class,"list-cat-images")]/li/a[contains(@href,"kategori")]/@href'))

        for category_url in category_urls:
            category_url = get_full_url(response, category_url)
            yield Request(url=category_url, callback=self.parse_category)
            
    def parse_category(self, response):
        sub_category_urls = self.extract_list(
                response.xpath('//div[@class="category-matrix"]/ul/li/a[contains(@href,"kategori")]/@href'))

        for sub_category_url in sub_category_urls:
            sub_category_url = get_full_url(response, sub_category_url)
            yield Request(url=sub_category_url, callback=self.parse_category)
            
        if not sub_category_urls:
            category = None

            if "category" in response.meta:
                category = response.meta['category']

            if not category:
                category = CategoryItem()
                category_path = self.extract_all(response.xpath('//div[@id="true_path"]//span/text()'), " > ")
                category['category_leaf'] = self.extract(response.xpath('//h1/text()'))
                category['category_path'] = category_path + ' > ' + category['category_leaf']
                category['category_url'] = response.url
                yield category

                if not self.should_skip_category(category):
                    review_urls = self.extract_list(response.xpath(
                            '//tr[contains(@id,"erow_prod-")]//img[contains(@class,"stars10")]/parent::a/@href'))
                    for review_url in review_urls:                        
                            review_url = get_full_url(response, review_url)
                            request = Request(url=review_url, callback=self.parse_reviews)
                            request.meta['category'] = category
                            yield request
                        
                    next_page_url = self.extract(response.xpath('//a[@rel="next"]/@href'))
                    if next_page_url:
                        next_page_url = get_full_url(response, next_page_url)
                        request = Request(url=next_page_url, callback=self.parse_category)
                        request.meta['category'] = category
                        yield request
        
    def parse_reviews(self, response):
        product = ProductItem()

        product['TestUrl'] = response.url
        product['OriginalCategoryName'] = response.meta['category']['category_path']
        product['ProductName'] = self.extract(response.xpath('//h1/a/text()'))
        product['PicURL'] = self.extract(response.xpath('//meta[@property="og:image"]/@content'))
        product['ProductManufacturer'] = self.extract(response.xpath('//meta[@itemprop="brand"]/@content'))
        product['source_internal_id'] = self.extract(response.xpath('//@data-product-id'))
        yield product
        
        reviews = response.xpath('//li[@class="opinion-row"]')
        for review in reviews:
            user_review = ReviewItem()
            user_review['DBaseCategoryName'] = "USER"
            user_review['ProductName'] = product['ProductName']
            user_review['TestUrl'] = product['TestUrl']
            user_review['source_internal_id'] = product['source_internal_id']
            date = self.extract(review.xpath('.//meta[@itemprop="datePublished"]/@content'))
            user_review['TestDateText'] = date_format(date, "%Y %m %d")
            user_review['SourceTestRating'] = self.extract(review.xpath('.//meta[@itemprop="ratingValue"]/@content'))
            user_review['Author'] = self.extract(review.xpath('.//h4/text()'))
            user_review['TestTitle'] = self.extract(review.xpath('.//div[contains(@class,"grade-text")]/text()'))
            user_review['TestSummary'] = self.extract_all(review.xpath('.//div[@itemprop="description"]/text()'))
            yield user_review
