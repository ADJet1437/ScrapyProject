__author__ = 'jim'

import re

from scrapy.http import Request

from alascrapy.items import ProductItem, ReviewItem, ProductIdItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format


class CrateandbarrelComSpider(AlaSpider):
    name = 'crateandbarrel_com'
    allowed_domains = ['crateandbarrel.com', 'bazaarvoice.com']
    start_urls = ['http://www.crateandbarrel.com/kitchen-and-food/appliances-electrics/',
                  'http://www.crateandbarrel.com/kitchen-and-food/coffee-and-tea/']

    bv_key = '3nrh8am0ufbc174ibar6c3jkj'
    bv_version = '5.4'

    def parse(self, response):
        category_urls = self.extract_list(response.xpath('//ul[@class="SuperCatNav"]/li/a/@href'))

        for category_url in category_urls:
            category_url = get_full_url(response, category_url)
            yield Request(url=category_url, callback=self.parse_category)

    def parse_category(self, response):
        ocn = self.extract_all(response.xpath('//div[@id="SiteMapPath"]/span//text()'))
        product_urls = self.extract_list(response.xpath(
                '//span[@class="product-thumb"][following-sibling::div[@class="hwBottomHitArea"]]/a/@href'))
        for product_url in product_urls:
            product_url = get_full_url(response, product_url)
            request = Request(url=product_url, callback=self.parse_product)
            request.meta['ocn'] = ocn
            yield request

    def parse_product(self, response):
        product = ProductItem()

        product['TestUrl'] = response.url
        product['OriginalCategoryName'] = response.meta['ocn']
        name = self.extract(response.xpath('//h1[@id="productNameHeader"]/text()'))
        product['PicURL'] = self.extract(response.xpath('//img[@id="_imgLarge"]/@src'))
        product['source_internal_id'] = self.extract(response.xpath('//span[@class="jsSwatchSku"]/text()'))

        mpn = self.extract(response.xpath('//p[contains(text(),"Item Number")]/span/text()'))
        if mpn:
            product_id = ProductIdItem()
            product["ProductName"] = name+' '+mpn
            product_id['ProductName'] = product["ProductName"]
            product_id['source_internal_id'] = product['source_internal_id']
            product_id['ID_kind'] = "MPN"
            product_id['ID_value'] = mpn
            yield product
            yield product_id
        else:
            product["ProductName"] = name
            yield product

        test_url = 'http://api.bazaarvoice.com/data/reviews.json?apiversion=%s&passkey=%s&Filter=ProductId:s%s' \
                   '&Sort=SubmissionTime:desc&Limit=100' % (self.bv_version, self.bv_key, product['source_internal_id'])

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
            user_review['source_internal_id'] = response.meta['product']['source_internal_id']
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
