__author__ = 'jim'
# coding:utf-8
import re

from scrapy.http import Request

from alascrapy.items import ProductItem, ReviewItem, CategoryItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format


class CostcoComSpider(AlaSpider):
    name = 'costco_com'
    allowed_domains = ['costco.com', 'bazaarvoice.com']
    start_urls = ['http://www.costco.com/view-more.html']

    bv_key = 'bai25xto36hkl5erybga10t99'
    bv_version = '5.5'
    bv_code = '2070-en_us'

    def parse(self, response):
        sub_category_urls = self.extract_list(response.xpath('//a[@class="viewmore-list"]/@href'))
        for sub_category_url in sub_category_urls:
            sub_category_url = get_full_url(response, sub_category_url)
            request = Request(url=sub_category_url, callback=self.parse_category)
            yield request

    def parse_category(self, response):
        sub_category_urls = self.extract_list(response.xpath(
            '//div[@class="category-tile"]/a[not(contains(@title,"All "))]/@href'))
        for sub_category_url in sub_category_urls:
            yield Request(url=sub_category_url, callback=self.parse_category)

        if sub_category_urls:
            return

        category = CategoryItem()
        category['category_path'] = self.extract_all(response.xpath('//ul[@id="breadcrumbs"]//text()'), ' > ')
        category['category_leaf'] = self.extract(response.xpath('//h1/text()'))
        category['category_url'] = response.url
        yield category

        if not self.should_skip_category(category):
            product_urls = self.extract_list(response.xpath('//span[@itemprop="aggregateRating"]/a/@href'))
            for product_url in product_urls:
                request = Request(url=product_url.split('#')[0], callback=self.parse_product)
                request.meta['category'] = category
                yield request

    def parse_product(self, response):
        sii = self.extract(response.xpath('//input[@class="addedItemInput"]/@value'))
        if sii:
            product = ProductItem()
            product['TestUrl'] = response.url
            product['OriginalCategoryName'] = response.meta['category']['category_path']
            product['ProductName'] = self.extract(response.xpath('//h1[@itemprop="name"]/text()'))
            product['PicURL'] = self.extract(response.xpath('//img[@itemprop="image"]/@src'))
            product['ProductManufacturer'] = self.extract(response.xpath(
                '//span[contains(text(),"Brand")]/following-sibling::text()'))
            product['source_internal_id'] = sii
            yield product

            test_url = 'http://api.bazaarvoice.com/data/batch.json?passkey=%s&apiversion=%s' \
                       '&displaycode=%s&resource.q0=reviews&filter.q0=isratingsonly:eq:false' \
                       '&filter.q0=productid:eq:%s' \
                       '&filter.q0=contentlocale:eq:en_US&sort.q0=submissiontime:desc&limit.q0=100&offset.q0=0' % \
                       (self.bv_key, self.bv_version, self.bv_code, product['source_internal_id'])

            request = Request(url=test_url, callback=self.parse_reviews)
            request.meta['product'] = product
            yield request

    @staticmethod
    def parse_reviews(response):
        reviews = re.findall(r'TagDimensions(((?!(TagDimensions|SyndicationSource)).)+)ModerationStatus', response.body)

        for item in reviews:
            review = item[0]
            sii = re.findall(r'"ProductId":"([\d-]+)', review)
            if response.meta['product']['source_internal_id'] in sii:
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
