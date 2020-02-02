__author__ = 'jim'

from scrapy.http import Request

from alascrapy.items import ProductItem, ReviewItem, CategoryItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import date_format, get_full_url


class BilligerDeSpider(AlaSpider):
    name = 'billiger_de'
    allowed_domains = ['billiger.de']
    start_urls = ['http://www.billiger.de/show/kategorie/0-Alle-Kategorien.htm']

    def parse(self, response):
        category_urls = self.extract_list(response.xpath('//div[@class="ac_subitem"]/a/@href'))
        for category_url in category_urls:
            category_url = get_full_url(response, category_url)+'?size=50'
            yield Request(url=category_url, callback=self.parse_category)
            
    def parse_category(self, response):
        category = None

        if 'category' in response.meta:
            category = response.meta['category']

        if not category:
            category = CategoryItem()
            category['category_path'] = self.extract_all(response.xpath(
                    '(//div[@class="path"]/div/a|//h1)/text()'), ' > ')
            category['category_leaf'] = self.extract(response.xpath('//h1/text()'))
            category['category_url'] = response.url
            yield category

        if not self.should_skip_category(category):
            product_urls = self.extract_list(response.xpath(
                    '//span[@class="rating_product_small"][descendant::span]/parent::a/@href'))
            for product_url in product_urls:
                product_url = get_full_url(response, product_url).strip('#userreviews')
                request = Request(url=product_url, callback=self.parse_product)
                request.meta['category'] = category
                yield request

            next_page_url = self.extract(response.xpath('//span[@class="active"]/following-sibling::a[1]/@href'))
            if next_page_url:
                next_page_url = get_full_url(response, next_page_url)
                request = Request(url=next_page_url, callback=self.parse_category)
                request.meta['category'] = category
                yield request
        
    def parse_product(self, response):
        product = ProductItem()
        product['TestUrl'] = response.url
        product['OriginalCategoryName'] = response.meta['category']['category_path']
        product['ProductName'] = self.extract(response.xpath(
                '(//div[@id="community_icons"]|//div[contains(@class,"product-title")])/h1/text()'))
        pic_url = self.extract(response.xpath('//a[@class="zoom"]/@rel|//div[@id="sync_main"]/img[1]/@data-src'))
        product['PicURL'] = get_full_url(response, pic_url)
        product['ProductManufacturer'] = self.extract(response.xpath(
                '//meta[@itemprop="brand"]/@content|//h3/a/text()'))
        product['source_internal_id'] = self.extract(response.xpath(
                '//div[@data-gm_pagemode="product_info"]/@data-gm_pageid|'
                '//div[contains(@class,"product-comparison")]/@data-product-id'))
        yield product

        reviews = response.xpath('//div[@itemprop="reviews"]|//div[contains(@class,"review-item")]')
        for review in reviews:
            user_review = ReviewItem()
            user_review['DBaseCategoryName'] = "USER"
            user_review['ProductName'] = product['ProductName']
            user_review['source_internal_id'] = product['source_internal_id']
            user_review['TestUrl'] = response.url
            date = self.extract(review.xpath('.//@datetime|.//div[@class="review-date"]/text()'))
            if 'am' in date:
                user_review['TestDateText'] = date_format(date, "am %d.%m.%Y")
            else:
                user_review['TestDateText'] = date_format(date, "%Y-%m-%d")
            user_review['SourceTestRating'] = self.extract(review.xpath(
                    './/meta[@itemprop="rating"]/@content|.//@data-rating'))
            user_review['Author'] = self.extract(review.xpath(
                    './/span[@itemprop="reviewer"]/text()|.//span[@class="click"]/text()'))
            user_review['TestTitle'] = self.extract(review.xpath(
                    './/span[@itemprop="summary"]/text()|.//div[contains(@class,"review-title")]/text()'))
            user_review['TestSummary'] = self.extract_all(review.xpath(
                    './/p[@itemprop="description"]/span//text()|.//div[contains(@class,"review-content")]//text()'))
            yield user_review
