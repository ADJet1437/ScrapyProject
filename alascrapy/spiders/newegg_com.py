__author__ = 'jim'

import re

from scrapy.http import Request

from alascrapy.items import ProductItem, ReviewItem, CategoryItem, ProductIdItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import date_format


class NeweggComSpider(AlaSpider):
    name = 'newegg_com'
    allowed_domains = ['newegg.com']
    start_urls = ['http://www.newegg.com/Feedback/Reviews.aspx']
    
    def parse(self, response):
        category_xpath = '//form[@name="SearchPanel"]/select/option[@value>0]/@value'
        categories = self.extract_list(response.xpath(category_xpath))
        for category in categories:
            category_url = 'http://www.newegg.com/FeedBack/CustratingAllReview.aspx?Order=0&Pagesize=100&N='
            category_url = category_url+category
            yield Request(url=category_url, callback=self.parse_category)

    def parse_category(self, response):
        category = CategoryItem()
        category['category_path'] = self.extract(
                response.xpath('//div[@id="bcaCustratingAllReview"]/div[contains(@class,"listRow")][1]/a[2]/text()'))
        category['category_leaf'] = category['category_path']
        category['category_url'] = response.url
        yield category
        
        if not self.should_skip_category(category):
            products = self.extract_list(response.xpath('//div[contains(@class,"listRow")]/div[1]/a/@href'))
            for product in products:
                request = Request(url=product, callback=self.parse_product)
                request.meta['category'] = category
                yield request
                
    def parse_product(self, response):
        category = response.meta['category']
        product = ProductItem()
        product['TestUrl'] = response.url
        product['OriginalCategoryName'] = category['category_path']
        product['ProductName'] = self.extract(response.xpath('//h1/span/text()'))
        product['source_internal_id'] = self.extract(response.xpath('//div[@id="baBreadcrumbTop"]//em/text()'))
        product['PicURL'] = self.extract(response.xpath('//a[@id="A2"]//img/@src'))
        brand = self.extract(response.xpath('//dl/dt[contains(text(),"Brand")]/parent::*/dd/text()'))
        if brand:
            product["ProductManufacturer"] = brand
        model = self.extract(response.xpath('//dl/dt[contains(text(),"Model")]/parent::*/dd/text()'))
        if brand and model:
            product['ProductName'] = brand + ' ' + model
        yield product
        
        if model:
            product_id = ProductIdItem()
            product_id['source_internal_id'] = product["source_internal_id"]
            product_id['ProductName'] = product["ProductName"]
            product_id['ID_kind'] = "MPN"
            product_id['ID_value'] = model
            yield product_id
        
        reviews = response.xpath('//table[@class="grpReviews"]/tbody/tr')
        for review in reviews:
            user_review = ReviewItem()
            user_review['DBaseCategoryName'] = "USER"
            user_review['ProductName'] = product['ProductName']
            user_review['TestUrl'] = product['TestUrl']
            date = self.extract(review.xpath('.//li[2]/text()'))
            if date:
                date = date[0:-2]
                user_review['TestDateText'] = date_format(date, "%m/%d/%Y %H:%M:%S")
            rating = self.extract(review.xpath('.//span[@class="itmRating"]//text()'))
            rate = re.findall(r'Rating:\s*(\d+)/5', rating)
            if rate:
                user_review['SourceTestRating'] = rate[0]
            user_review['Author'] = self.extract(review.xpath('.//li[1]//text()'))
            user_review['TestTitle'] = self.extract(review.xpath('.//h3/text()'))
            user_review['TestSummary'] = self.extract_all(
                    review.xpath('.//p/em[contains(text(),"Other Thoughts")]/parent::*/text()'))
            user_review['TestPros'] = self.extract_all(
                    review.xpath('.//p/em[contains(text(),"Pros")]/parent::*/text()'))
            user_review['TestCons'] = self.extract_all(
                    review.xpath('.//p/em[contains(text(),"Cons")]/parent::*/text()'))
            user_review['source_internal_id'] = product['source_internal_id']
            yield user_review
