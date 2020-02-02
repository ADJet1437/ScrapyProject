__author__ = 'jim, frank'

from scrapy.http import Request

from alascrapy.items import ProductItem, ReviewItem, CategoryItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format, dateparser

from urlparse import urlparse

import alascrapy.lib.extruct_helper as extruct_helper
import alascrapy.lib.dao.incremental_scraping as incremental_utils

# If broken, it might be a good idea to check if the following work or not:
# 1. the method of getting source_internal_id in parse_product()
# 2. review_url_format (with source_internal_id as a part)
# 3. the method to determine if a product has reviews or not in parse_category()
class ReevooComSpider(AlaSpider):
    name = 'reevoo_com'
    allowed_domains = ['reevoo.com']
    start_urls = ['https://www.reevoo.com/categories']

    review_url_format = 'https://mark.reevoo.com/reevoomark/en-GB/product.html?sku={}&tab=reviews&sort_by=recent&trkref=REEVOO_B2C_EN_GB&per_page=30'
    
    def parse(self, response):
        category_xpath = '//div[@class="content"]//a[@class="item"]/@href'
        categories = self.extract_list(response.xpath(category_xpath))
        for category in categories:
            yield Request(url=get_full_url(response, category+'?order=customer_score'), callback=self.parse_category)
            
    def parse_category(self, response):
        has_review_xpath = './/div[contains(@class, "reevoo-shared-score")]'

        category = None
        if "category" in response.meta:
            category = response.meta['category']

        if not category:
            category = CategoryItem()
            category['category_path'] = self.extract_all(
                    response.xpath('//div[@class="shared-breadcrumbs"]/ol/li/a/text()'), " ; ")
            category['category_leaf'] = self.extract(
                    response.xpath('//div[@class="shared-breadcrumbs"]/ol/li[contains(@class,"last")]//text()'))
            category['category_url'] = response.url
            yield category
            
        if not self.should_skip_category(category):
            products = response.xpath('//a[contains(@class,"reviewable-tile")]')
            for product in products:
                has_review = product.xpath(has_review_xpath)
                if not has_review:
                    continue

                product_url = self.extract(product.xpath('./@href'))
                request = Request(url=get_full_url(response, product_url), callback=self.parse_product)
                request.meta['category'] = category
                yield request

            next_page = self.extract(response.xpath('//a[contains(@class,"next")]/@href'))
            if next_page:
                request = Request(get_full_url(response, next_page), callback=self.parse_category)
                request.meta['category'] = category
                yield request
                
    def parse_product(self, response):
        category = response.meta['category']
        product = ProductItem()
        product['TestUrl'] = response.url
        product['OriginalCategoryName'] = category['category_path']

        product['ProductName'] = ''
        product['PicURL'] = ''
        product_json_ld = extruct_helper.extract_json_ld(response.text, 'Product')
        if product_json_ld:
            product['ProductName'] = product_json_ld.get('name', '')
            product['PicURL'] = product_json_ld.get('image', '')
        else:
            # TODO: add fallback plan?
            return

        parsed_url = urlparse(response.url)
        splited = parsed_url.path.split('/')
        if splited:
            product["source_internal_id"] = splited[-1]
        yield product

        internal_id = self.product_id(product, kind='reevoo_internal_id', value=product['source_internal_id'])
        yield internal_id

        # TODO: test if the url is valid or not?
        review_url = self.review_url_format.format(product["source_internal_id"])
        request = Request(review_url, callback=self.parse_review)
        request.meta['product'] = product
        yield request

    def parse_review(self, response):
        next_page_xpath = "(//*[@rel='next']/@href)[1]"
        default_rating_xpath = './/reevoo-score/@data-score'
        
        product = response.meta['product']
        reviews = response.xpath('//article[contains(@id,"review_")]')

        if not reviews:
            return

        # From observation, at least currys.co.uk uses a different format to present review rating
        rating_xpath = response.meta.get('rating_xpath', '')
        if not rating_xpath:
            rating_xpath = default_rating_xpath

        last_user_review = incremental_utils.get_latest_user_review_date_by_sii(
            self.mysql_manager, self.spider_conf['source_id'],
            product["source_internal_id"]
        )

        for review in reviews:
            user_review = ReviewItem()
            date = self.extract(review.xpath('.//span[contains(@class, "date_publish")]/text()'))
            if date:
                user_review['TestDateText'] = date_format(date, '')
                current_user_review = dateparser.parse(user_review['TestDateText'],
                                                       date_formats=['%Y-%m-%d'])
                if current_user_review < last_user_review:
                    return

            user_review['DBaseCategoryName'] = "USER"
            user_review['ProductName'] = product['ProductName']
            user_review['TestUrl'] = product['TestUrl']
            user_review['SourceTestRating'] = self.extract(review.xpath(rating_xpath))
            user_review['Author'] = self.extract(review.xpath('.//h4[@class="attribution-name"]/text()'))
            user_review['TestPros'] = self.extract_all(review.xpath('.//dd[@class="pros"]/text()'))
            user_review['TestCons'] = self.extract_all(review.xpath('.//dd[@class="cons"]/text()'))
            user_review['source_internal_id'] = product['source_internal_id']

            # All reviews after first empty review are empty
            if user_review['TestPros'] or user_review['TestCons']:
                yield user_review
            else:
                return

        next_page_url = self.extract(response.xpath(next_page_xpath))
        if next_page_url:
            next_page_url = get_full_url(response, next_page_url)
            request = Request(next_page_url, callback=self.parse_review, meta=response.meta)
            yield request
