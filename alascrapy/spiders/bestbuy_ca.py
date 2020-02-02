__author__ = 'jim'

import re
import datetime

from scrapy.http import Request

from alascrapy.items import ProductItem, CategoryItem, ReviewItem, ProductIdItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format


class BestbuyCaSpider(AlaSpider):
    name = 'bestbuy_ca'
    allowed_domains = ['bestbuy.ca']
    start_urls = ['http://www.bestbuy.ca/en-CA/sitemap-overview.aspx']

    def parse(self, response):
        sub_category_urls = self.extract_list(response.xpath('//a[@class="lnk-more"]/@href'))

        for sub_category_url in sub_category_urls:
            sub_category_url = get_full_url(response, sub_category_url)
            yield Request(url=sub_category_url, callback=self.parse_sub_category)

    def parse_sub_category(self, response):
        category_urls = self.extract_list(response.xpath('//div[@class="sitemap-block"]//a/@href'))

        for category_url in category_urls:
            category_url = get_full_url(response, category_url) + '&pageSize=96'
            yield Request(url=category_url, callback=self.parse_category)

    def parse_category(self, response):
        is_leaf_category = response.xpath('//ul[@class="category-list"]//a[@class="current-node"]')
        if is_leaf_category:
            category = None

            if "category" in response.meta:
                category = response.meta['category']

            if not category:
                category = CategoryItem()
                category['category_path'] = self.extract_all(response.xpath(
                        '//ul[contains(@class,"breadcrumb")]//text()'))
                category['category_leaf'] = self.extract(response.xpath('//li[@data-type="Category"]/span/text()'))
                category['category_url'] = response.url
                yield category

            if not self.should_skip_category(category):
                product_urls = self.extract_list(response.xpath(
                        '//div[@class="prod-rating"]/ancestor::li[contains(@class,"listing-item")]//h4/a/@href'))
                for product_url in product_urls:
                    product_url = get_full_url(response, product_url)
                    request = Request(url=product_url, callback=self.parse_product)
                    request.meta['category'] = category
                    yield request

                next_page_url = self.extract_list(response.xpath('//li[@class="pagi-next"]/a/@href'))
                if next_page_url:
                    request = Request(url=get_full_url(response, next_page_url[0]), callback=self.parse_category)
                    request.meta['category'] = category
                    yield request

    def parse_product(self, response):
        product = ProductItem()

        product['TestUrl'] = response.url
        product['OriginalCategoryName'] = response.meta['category']['category_path']
        product['ProductName'] = self.extract(response.xpath('//h1/span/text()'))
        product['PicURL'] = self.extract(response.xpath('//img[@itemprop="image"]/@src'))
        product['ProductManufacturer'] = self.extract(response.xpath('//span[@class="brand-logo"]/img/@alt'))
        product['source_internal_id'] = self.extract(response.xpath('//span[@itemprop="productid"]/text()'))
        yield product

        id_value = self.extract(response.xpath('//span[@itemprop="model"]/text()'))
        if id_value:
            product_id = ProductIdItem()
            product_id['ProductName'] = product["ProductName"]
            product_id['ID_kind'] = "MPN"
            product_id['ID_value'] = id_value
            product_id['source_internal_id'] = product['source_internal_id']
            yield product_id

        reviews = response.xpath('//div[contains(@class,"customer-review-item")]')
       
        for review in reviews:
            user_review = ReviewItem()
            user_review['DBaseCategoryName'] = "USER"
            user_review['ProductName'] = product['ProductName']
            user_review['TestUrl'] = product['TestUrl']
            user_review['source_internal_id'] = product['source_internal_id']
            date = self.extract(review.xpath('.//li[@class="date"]/text()'))
            date_match = re.findall(r'(\d) day', date)
            if date_match:
                review_date = datetime.date.today() - datetime.timedelta(days=int(date_match[0]))
                user_review['TestDateText'] = review_date.strftime('%Y-%m-%d')
            else:
                user_review['TestDateText'] = date_format(date, '')
            user_review['SourceTestRating'] = self.extract(review.xpath('.//div[@class="rating-score"]/text()'))
            user_review['Author'] = self.extract(review.xpath('.//li[@class="name"]/text()'))
            user_review['TestTitle'] = self.extract(review.xpath('.//h3/text()'))
            user_review['TestSummary'] = self.extract_all(review.xpath('.//p/text()|.//span[@class="hidden"]/text()'))
            yield user_review
