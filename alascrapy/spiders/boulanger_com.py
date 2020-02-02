__author__ = 'jim'

import re

from scrapy.http import Request

from alascrapy.items import ProductItem, CategoryItem, ReviewItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format


class BoulangerComSpider(AlaSpider):
    name = 'boulanger_com'
    allowed_domains = ['boulanger.com', 'bazaarvoice.com']
    start_urls = ['http://www.boulanger.com/plan']

    def parse(self, response):
        category_0_urls = self.extract_list(response.xpath('//li[not(ul)]/h2/a/@href'))
        category_1_urls = self.extract_list(response.xpath('//li/ul/li/h3/a/@href'))

        for category_url in (category_0_urls+category_1_urls):
            yield Request(url=category_url+'?viewSize=100', callback=self.parse_category)

    def parse_category(self, response):
        category = None

        if "category" in response.meta:
            category = response.meta['category']

        if not category:
            category = CategoryItem()
            category['category_path'] = self.extract_all(response.xpath('//div[@id="filAriane"]/ul//text()'), ' > ')
            category['category_leaf'] = self.extract(response.xpath('//div[@id="filAriane"]/ul/li/span/text()'))
            category['category_url'] = response.url
            yield category

        if not self.should_skip_category(category):
            product_urls = self.extract_list(response.xpath(
                    '//div[@class="designations"][p[contains(@class,"rating")]]/h2/a/@href'))
            for product_url in product_urls:
                product_url = get_full_url(response, product_url)
                request = Request(url=product_url, callback=self.parse_product)
                request.meta['category'] = category
                yield request

            next_page_url = self.extract(response.xpath('//a[contains(text(),"Page suivante")]/@onclick'))
            if next_page_url:
                request = Request(url=get_full_url(response, next_page_url.split("'")[1]), callback=self.parse_category)
                request.meta['category'] = category
                yield request

    def parse_product(self, response):
        product = ProductItem()

        product['TestUrl'] = response.url
        product['OriginalCategoryName'] = response.meta['category']['category_path']
        name = self.extract(response.xpath('//title/text()'))
        product['ProductName'] = name.strip(' chez Boulanger')
        product['PicURL'] = self.extract(response.xpath('//meta[@property="og:image"]/@content'))
        product['ProductManufacturer'] = self.extract(response.xpath('//span[@itemprop="brand"]/span/text()'))
        product['source_internal_id'] = self.extract(response.xpath('//span[@itemprop="sku"]/text()'))
        yield product

        review_url = 'http://boulanger.ugc.bazaarvoice.com/2786-fr_fr/%s/reviews.djs?format=embeddedhtml' \
                     % product['source_internal_id']
        request = Request(url=review_url, callback=self.parse_reviews)
        request.meta['product'] = product
        yield request

    @staticmethod
    def parse_reviews(response):
        reviews = re.findall(r'ReviewID_[\d](((?!(RRBeforeClientResponseContainerSpacer)).)+)', response.body)

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
            pro_match = re.findall(r'ProTags\\"><span class=\\"BVRRTag\\">([^<>]+)<', review)
            if pro_match:
                user_review['TestPros'] = pro_match[0]
            con_match = re.findall(r'ConTags\\"><span class=\\"BVRRTag\\">([^<>]+)<', review)
            if con_match:
                user_review['TestCons'] = con_match[0]
            yield user_review
