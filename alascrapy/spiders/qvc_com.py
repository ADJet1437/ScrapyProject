__author__ = 'jim'

import re

from scrapy.http import Request

from alascrapy.items import ProductItem, CategoryItem, ReviewItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import date_format


class QvcComSpider(AlaSpider):
    name = 'qvc_com'
    allowed_domains = ['qvc.com', 'bazaarvoice.com']
    start_urls = ['http://www.qvc.com/electronics/_/N-lglw/c.html?identifier=0103']

    def parse(self, response):
        category_urls = self.extract_list(response.xpath('//h3[text()="Departments"]/following::ul[1]/li/a/@href'))

        for category_url in category_urls:
            yield Request(url=category_url, callback=self.parse_category)

    def parse_category(self, response):
        category_urls = self.extract_list(response.xpath(
            '//ul[@class="noCheckBox"]/li[contains(@id,"refineN")]/a/@href'))

        for category_url in category_urls:
            yield Request(url=category_url, callback=self.parse_category)

        if category_urls:
            return

        category = CategoryItem()
        category['category_path'] = self.extract_all(response.xpath('//div[@id="breadCrumbs"]//text()'))
        category['category_leaf'] = self.extract(response.xpath('//h1/text()'))
        category['category_url'] = response.url
        yield category

        if not self.should_skip_category(category):
            product_urls = self.extract_list(response.xpath(
                    '//div[@class="productRatings"][descendant::span[@class="productNumberOfReviews"]]/a/@href'))
            for product_url in product_urls:
                request = Request(url=product_url, callback=self.parse_product)
                request.meta['category'] = category
                yield request

    def parse_product(self, response):
        product = ProductItem()

        product['TestUrl'] = response.url.split('?')[0]
        product['OriginalCategoryName'] = response.meta['category']['category_path']
        product['ProductName'] = self.extract(response.xpath('//h1[@class="fn"]/text()'))
        product['PicURL'] = self.extract(response.xpath('//meta[@property="og:image"]/@content'))
        product['ProductManufacturer'] = self.extract(response.xpath('//p[@class="sidebarProductBrand"]/text()'))
        product['source_internal_id'] = self.extract(response.xpath(
            '//span[@id="tabProductDetailNavDe-itemNumber"]/text()'))
        yield product

        review_url = 'http://qvc.ugc.bazaarvoice.com/1689wcs-en_us/%s/reviews.djs?format=embeddedhtml' \
                     % product['source_internal_id']
        request = Request(url=review_url, callback=self.parse_reviews)
        request.meta['product'] = product
        yield request

    @staticmethod
    def parse_reviews(response):
        reviews = re.findall(r'BVRRReviewTitleContainer(((?!(RRBeforeClientResponseContainerSpacer)).)+)',
                             response.body)

        for review_tuple in reviews:
            review = review_tuple[0]
            user_review = ReviewItem()
            user_review['DBaseCategoryName'] = "USER"
            user_review['ProductName'] = response.meta['product']['ProductName']
            user_review['TestUrl'] = response.meta['product']['TestUrl']
            user_review['source_internal_id'] = response.meta['product']['source_internal_id']
            date_match = re.findall(r'content=\\"([\d-]+)', review)
            if date_match:
                user_review['TestDateText'] = date_format(date_match[0], '')
            rate_match = re.findall(r'BVRRRatingNumber\\">([^<>]+)<', review)
            if rate_match:
                user_review['SourceTestRating'] = rate_match[0]
            author_match = re.findall(r'BVRRNickname\\">([^<>]+)<', review)
            if author_match:
                user_review['Author'] = author_match[0]
            title_match = re.findall(r'BVRRReviewTitle\\">([^<>]+)<', review)
            if title_match:
                user_review['TestTitle'] = title_match[0]
            summary_match = re.findall(r'BVRRReviewText\\">([^<>]+)<', review)
            if summary_match:
                user_review['TestSummary'] = summary_match[0]
            yield user_review
