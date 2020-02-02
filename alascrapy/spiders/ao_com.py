__author__ = 'jim, frank'

from scrapy.http import Request

from alascrapy.items import ProductItem, CategoryItem, ReviewItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format, dateparser

import alascrapy.lib.dao.incremental_scraping as incremental_utils


class AoComSpider(AlaSpider):
    name = 'ao_com'
    allowed_domains = ['ao.com']
    start_urls = ['http://ao.com/']

    brand_xpath = '//span[@class="details" and text()="Brand"]/following::span/text()'
    review_url_prefix = 'http://ao.com/p/reviews/'

    def parse(self, response):
        category_urls = self.extract_list(response.xpath('//a[@data-menu-item-type="Lister" or '
                                                         '@data-menu-item-type="lister"]/@href'))

        for category_url in category_urls:
            category_url = get_full_url(response, category_url) + '?sort=reviewage&pagesize=60'
            yield Request(url=category_url, callback=self.parse_category)

    def parse_category(self, response):
        next_page_xpath = "(//*[@rel='next'])[1]/@href"

        category = None
        if "category" in response.meta:
            category = response.meta['category']

        if not category:
            category = CategoryItem()
            category['category_path'] = self.extract_all(response.xpath('//ul[@id="breadcrumb"]//text()'), " > ")
            category['category_leaf'] = self.extract(response.xpath('//h1/text()'))
            category['category_url'] = response.url
            yield category

        if not self.should_skip_category(category):
            review_urls_xpath = '//div[@class="reviewsContainer"]/a[@id="ratingLink"]/@href'
            review_urls = self.extract_list(response.xpath(review_urls_xpath))
            for review_url in review_urls:
                review_url = get_full_url(response, review_url).strip('#reviewsTab')
                request = Request(url=review_url, callback=self.parse_product)
                request.meta['category'] = category
                yield request

        next_page_url = self.extract_all(response.xpath(next_page_xpath))
        if next_page_url:
            next_page_request = Request(url=get_full_url(response, next_page_url), callback=self.parse_category)
            next_page_request.meta['category'] = category
            yield next_page_request

    def parse_product(self, response):
        product = ProductItem()

        product['TestUrl'] = response.url
        product['OriginalCategoryName'] = response.meta['category']['category_path']
        product['ProductName'] = self.extract(response.xpath('//h1[contains(@class, "title")]/text()'))
        product['PicURL'] = self.extract(response.xpath('//meta[@property="og:image"]/@content'))
        product['ProductManufacturer'] = self.extract(
            response.xpath(self.brand_xpath))
        product['source_internal_id'] = self.extract(
            response.xpath('//span[@class="details" and text()="SKU"]/following::span/text()'))
        yield product

        if product['source_internal_id']:
            sku_id = self.product_id(product, kind='sku', value=product['source_internal_id'])
            yield sku_id

        id_value = self.extract(response.xpath('//span[@itemprop="productID"]/text()'))
        if id_value:
            product_id = self.product_id(product, kind='MPN', value=id_value)
            yield product_id

        splitted = response.url.split('/')
        if splitted:
            review_url = self.review_url_prefix + splitted[-1].rstrip('.aspx')
            request = Request(url=get_full_url(response, review_url), callback=self.parse_reviews)
            request.meta['product'] = product
            yield request
        
    def parse_reviews(self, response):
        next_page_xpath = '//a[@class="next-arrow"]/@href'

        product = response.meta['product']
        last_user_review = incremental_utils.get_latest_user_review_date_by_sii(
            self.mysql_manager, self.spider_conf['source_id'],
            product["source_internal_id"]
        )

        reviews = response.xpath('//div[contains(@class,"reviewWidget")]')
        for review in reviews:
            user_review = ReviewItem()
            date = self.extract(review.xpath('.//span[@class="reviewDate"]/text()'))
            if date:
                user_review['TestDateText'] = date_format(date, '')
                current_user_review = dateparser.parse(user_review['TestDateText'],
                                                       date_formats=['%Y-%m-%d'])
                if current_user_review < last_user_review:
                    return

            user_review['DBaseCategoryName'] = "USER"
            user_review['SourceTestScale'] = 5
            user_review['ProductName'] = product['ProductName']
            user_review['TestUrl'] = product['TestUrl']
            user_review['source_internal_id'] = product['source_internal_id']
            rating = self.extract(review.xpath('.//span[contains(@class,"ratingSpriteUnder")]/@class'))
            rating = rating.strip('ratingSpriteUnder ratingSprite_').replace('-', '.')
            user_review['SourceTestRating'] = rating
            user_review['Author'] = self.extract(review.xpath('.//p[@class="name"]/text()'))
            user_review['TestTitle'] = self.extract(review.xpath('.//h2/text()'))
            user_review['TestSummary'] = self.extract_all(review.xpath('.//div[@class="reviewContainer"]/p/text()'))
            user_review['TestPros'] = self.extract_all(review.xpath('.//ul[@class="pros"]/li/text()'), '; ')
            user_review['TestCons'] = self.extract_all(review.xpath('.//ul[@class="cons"]/li/text()'), '; ')
            yield user_review

        next_page_url = self.extract_xpath(response, next_page_xpath)
        if next_page_url:
            next_page_url = get_full_url(response, next_page_url)
            request = Request(next_page_url, callback=self.parse_reviews)
            request.meta['product'] = product
            yield request
