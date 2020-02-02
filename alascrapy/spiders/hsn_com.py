__author__ = 'jim'

from scrapy.http import Request

from alascrapy.items import ProductItem, CategoryItem, ReviewItem, ProductIdItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format


class HsnComSpider(AlaSpider):
    name = 'hsn_com'
    allowed_domains = ['hsn.com']
    start_urls = ['http://www.hsn.com/article/site-map/4315']

    def parse(self, response):
        category_urls = self.extract_list(response.xpath('//a[@class="asitelink" and contains(@href,"shop")]/@href'))

        for category_url in category_urls:
            category_url = get_full_url(response, category_url)
            yield Request(url=category_url, callback=self.parse_category)

    def parse_category(self, response):
        category_path_xpath = '//nav/ol/li//span[@itemprop="title"]/text()'
        category_leaf_xpath = '//nav/ol/li[last()]//span[@itemprop="title"]/text()'

        category = None

        if "category" in response.meta:
            category = response.meta['category']

        if not category:
            category = CategoryItem()
            category['category_path'] = self.extract_all(response.xpath(category_path_xpath), " > ")
            category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
            category['category_url'] = response.url
            yield category

        if not self.should_skip_category(category):
            products = response.xpath('//div[@data-product-id]')
            for product in products:
                review = product.xpath('.//div[@class="rateit"]')
                if review:
                    product_url = self.extract(product.xpath('.//h3/a/@href'))
                    product_url = get_full_url(response, product_url)
                    request = Request(url=product_url, callback=self.parse_product)
                    request.meta['category'] = category
                    yield request
                    
            next_page_url = self.extract(response.xpath('//a[contains(@class,"page-prev-next")]/@href'))
            if next_page_url:
                next_page_url = get_full_url(response, next_page_url)
                request = Request(url=next_page_url, callback=self.parse_category)
                request.meta['category'] = category
                yield request

    def parse_product(self, response):
        id_values_xpath = '//td[contains(text(),"Model")]/parent::tr/td[@class="values"]/span/text()'
        product = ProductItem()
        
        product['TestUrl'] = response.url
        product['OriginalCategoryName'] = response.meta['category']['category_path']
        product['ProductName'] = self.extract(response.xpath('//h1/span/text()'))
        pic_url = self.extract(response.xpath('//div/a[contains(@class,"product-image")]/img/@src'))
        if pic_url:
            product['PicURL'] = get_full_url(response, pic_url)
        product['ProductManufacturer'] = self.extract(response.xpath('//span[@itemprop="brand"]/text()'))
        product['source_internal_id'] = self.extract(response.xpath('//input[@id="webp_id"]/@value'))
        yield product

        id_values = self.extract(response.xpath(id_values_xpath))
        if id_values:
            id_values = id_values.split(',')
            for id_value in id_values:
                product_id = ProductIdItem()
                product_id['ProductName'] = product["ProductName"]
                product_id['source_internal_id'] = product['source_internal_id']
                product_id['ID_kind'] = "MPN"
                product_id['ID_value'] = id_value.strip(' ')
                yield product_id
            
        review_url = 'http://www.hsn.com/products/productreviews/get-product-reviews?id=' + \
                     product['source_internal_id'] + '&recordsPerPage=500'
        request = Request(url=review_url, callback=self.parse_reviews)
        request.meta['product'] = product
        yield request
        
    def parse_reviews(self, response):
        product = response.meta['product']
        reviews = response.xpath('//ul[@class="reviews-list"]/li')
       
        for review in reviews:
            user_review = ReviewItem()
            user_review['DBaseCategoryName'] = "USER"
            user_review['ProductName'] = product['ProductName']
            user_review['TestUrl'] = product['TestUrl']
            user_review['source_internal_id'] = product['source_internal_id']
            date = self.extract(review.xpath('.//time/@datetime'))
            if date:
                user_review['TestDateText'] = date_format(date, "%Y %m %d")
            rating = self.extract(review.xpath('.//div[contains(@class,"rateit-selected")]/@style'))
            rating = rating.strip('width:').strip('.00%')
            user_review['SourceTestRating'] = rating
            user_review['Author'] = self.extract(review.xpath('.//div[@class="customer"]/span/text()'))
            user_review['TestTitle'] = self.extract(review.xpath('.//div[@class="title"]/text()'))
            user_review['TestSummary'] = self.extract_all(review.xpath('.//div[@class="copy"]/p/text()'))
            yield user_review
