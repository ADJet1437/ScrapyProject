__author__ = 'jim'

from scrapy.http import Request

from alascrapy.items import ProductItem, ReviewItem, CategoryItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import date_format


class HeiseDeSpider(AlaSpider):
    name = 'heise_de'
    allowed_domains = ['heise.de']
    base_url = 'http://www.heise.de/preisvergleich/'
    start_urls = [base_url]
    
    def parse(self, response):
        categories = self.extract_list(response.xpath('//h2[contains(@class,"katt")]/a/@href'))
        for category in categories:
            yield Request(url=category.replace('./', self.base_url), callback=self.parse_category)
            
    def parse_category(self, response):
        category_path_xpath = '//p/a[contains(@class,"gh_statline")]/parent::*//text()'
        category_leaf_xpath = '//p/a[contains(@class,"gh_statline")]/parent::*/text()[last()]'

        sub_categories = response.xpath('//li[contains(@class,"gh_cat")]')
        if sub_categories:
            for sub_category in sub_categories:
                sub_category_url = self.extract(sub_category.xpath('./a/@href'))
                yield Request(url=sub_category_url.replace('./', self.base_url), callback=self.parse_category)
                
        if not sub_categories:
            category = None
            
            if "category" in response.meta:
                category = response.meta['category']
            
            if not category:
                category = CategoryItem()
                category['category_path'] = self.extract_all(response.xpath(category_path_xpath))
                category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
                category['category_url'] = response.url
                yield category
            
            if not self.should_skip_category(category):
                sorted_product_url = response.url+'&bl1_id=1000&sort=bew'
                request = Request(url=sorted_product_url, callback=self.parse_product)
                request.meta['category'] = category
                yield request

    def parse_product(self, response):
        category = response.meta['category']
        products = response.xpath('//tr[@class="t1"] | //tr[@class="t2"]')
        
        for product in products:
            review = product.xpath('.//img[contains(@title,"User")]')
            if review:
                product_id = self.extract(product.xpath('.//input/@value'))
                request = Request(url='http://www.heise.de/preisvergleich/?sr='+product_id+',-1',
                                  callback=self.parse_reviews)
                request.meta['category'] = category
                request.meta['product_id'] = product_id
                yield request
                
    def parse_reviews(self, response):
        category = response.meta['category']
        product = ProductItem()
        product['TestUrl'] = response.url
        product['OriginalCategoryName'] = category['category_path']
        product['ProductName'] = self.extract(response.xpath('//span[@class="fn"]/text()'))
        product_id = response.meta['product_id']
        product['PicURL'] = 'http://geizhals.at/p/'+product_id+'.jpg'
        product['source_internal_id'] = product_id
        yield product
        
        reviews = response.xpath('//li[contains(@class,"gh_box")]')
        for review in reviews:
            user_review = ReviewItem()
            user_review['DBaseCategoryName'] = "USER"
            user_review['ProductName'] = product['ProductName']
            user_review['TestUrl'] = product['TestUrl']
            date = self.extract(review.xpath('.//div[@class="userbox"]/text()')).strip('am ')
            user_review['TestDateText'] = date_format(date, "%d.%m.%Y %H:%M")
            user_review['SourceTestRating'] = self.extract(review.xpath('.//span[@itemprop="rating"]/text()'))
            user_review['Author'] = self.extract(review.xpath('.//span[contains(@class,"nick")]/text()'))
            user_review['TestTitle'] = self.extract(review.xpath('.//h3//text()'))
            user_review['TestSummary'] = self.extract_all(review.xpath('.//div[@itemprop="description"]//text()'))
            user_review['source_internal_id'] = product['source_internal_id']
            yield user_review
