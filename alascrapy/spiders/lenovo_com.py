__author__ = 'jim'

import re

from scrapy.http import Request

from alascrapy.items import ProductItem, ReviewItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format


class LenovoComSpider(AlaSpider):
    name = 'lenovo_com'
    allowed_domains = ['lenovo.com', 'bazaarvoice.com']
    start_urls = ['http://shop.lenovo.com/us/en/laptops/',
                  'http://shop.lenovo.com/us/en/desktops/',
                  'http://shop.lenovo.com/us/en/tablets/']

    bv_key = '2n8eec5syxa0adq5rnt3yc9m6'
    bv_version = '5.5'
    bv_code = '8923-en_us'
    bv_id = '12F0696583E04D86B9B79B0FEC01C087'

    def parse(self, response):
        sub_category_urls = self.extract_list(response.xpath('//span[contains(@class,"seriesPreview-viewLink")]/@href'))
        for sub_category_url in sub_category_urls:
            sub_category_url = get_full_url(response, sub_category_url)
            request = Request(url=sub_category_url, callback=self.parse_category)
            yield request

    def parse_category(self, response):
        products = response.xpath('//li[@class="seriesListings-itemContainer"]')
        for product in products:
            has_reviews = product.xpath('.//div[@class="reviews"][descendant::a[@target="_new"]]')
            if has_reviews:
                product_url = self.extract(product.xpath('.//h3/a/@href'))
                product_url = get_full_url(response, product_url)
                request = Request(url=product_url, callback=self.parse_product)
                yield request

        if not products:
            has_reviews = response.xpath('//span[@class="bvseo-ratingValue"]')
            if has_reviews:
                for item in self.parse_product(response):
                    yield item

    def parse_product(self, response):
        product = ProductItem()
        product['TestUrl'] = response.url
        product['OriginalCategoryName'] = self.extract(response.xpath('//meta[@name="ProductName"]/@content'))
        product['ProductName'] = self.extract(response.xpath(
                '//h1[@class="bar_3-heading"]/text() |'
                '//h1[@itemprop="name"]/text()'))
        pic_url = self.extract_list(response.xpath(
                '(//img[contains(@class,"heroImg")]/@src) |'
                '(//div[@class="productImg"]/img/@src) |'
                '//div[@id="galleria-stage"]//@src'))
        if pic_url:
            pic_url = get_full_url(response, pic_url[0])
            product['PicURL'] = pic_url
        product['ProductManufacturer'] = 'Lenovo'
        yield product

        mpn = self.extract(response.xpath('//meta[@name="PartNumber"]/@content'))
        if mpn:
            product_id = self.product_id(product)
            product_id['ID_kind'] = "MPN"
            product_id['ID_value'] = mpn
            yield product_id

        category_id = self.extract(response.xpath('//meta[@name="metacategoryidentifier"]/@content'))

        test_url = 'http://api.bazaarvoice.com/data/batch.json?passkey=%s&apiversion=%s' \
                   '&displaycode=%s&resource.q0=reviews&filter.q0=isratingsonly:eq:false' \
                   '&filter.q0=productid:eq:%s_%s' \
                   '&filter.q0=contentlocale:eq:en_US&sort.q0=submissiontime:desc&limit.q0=100&offset.q0=0' % \
                   (self.bv_key, self.bv_version, self.bv_code, category_id, self.bv_id)

        request = Request(url=test_url, callback=self.parse_reviews)
        request.meta['product'] = product
        yield request

    @staticmethod
    def parse_reviews(response):
        reviews = re.findall(r'{"TagDimensions":(((?!("TagDimensions")).)+)}', response.body)

        for item in reviews:
            review = item[0]
            user_review = ReviewItem()
            user_review['DBaseCategoryName'] = "USER"
            user_review['ProductName'] = response.meta['product']['ProductName']
            user_review['TestUrl'] = response.meta['product']['TestUrl']
            date = re.findall(r'"SubmissionTime":"([\d-]+)', review)
            user_review['TestDateText'] = date_format(date[0], "%Y-%m-%d")
            rate = re.findall(r'"Rating":([\d])', review)
            user_review['SourceTestRating'] = rate[0]
            author = re.findall(r'"UserNickname":"([^"]+)', review)
            if author:
                user_review['Author'] = author[0]
            title = re.findall(r'"Title":"([^"]+)', review)
            if title:
                user_review['TestTitle'] = title[0]
            summary = re.findall(r'"ReviewText":"([^"]+)', review)
            if summary:
                user_review['TestSummary'] = summary[0]
            yield user_review
