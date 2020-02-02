__author__ = 'jim'

import re

from scrapy.http import Request

from alascrapy.items import ProductItem, ReviewItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url


class HpComSpider(AlaSpider):
    name = 'hp_com'
    allowed_domains = ['hp.com']
    start_urls = ['http://store.hp.com/us/en/vwa/CategoryNavigationResultsView?storeId=10151&categoryId=%s' % x
                  for x in range(88337, 88341)]

    def parse(self, response):
        info = self.extract(response.xpath('//div[@id="facetCounts"]/script/text()'))
        numb = re.findall(r"productTotalCount.innerHTML = '([\d]+)'", info)
        for step in range(0, int(numb[0]), 9):
            category_url = response.url+'&beginIndex=%s&visitedItemCount=%s' % (step, step)
            yield Request(url=category_url, callback=self.parse_category)

    def parse_category(self, response):
        product_urls = self.extract_list(response.xpath(
            '//span[@class="ratinghits"]/ancestor::div[@class="prodDetails"]//h3/a/@href'))
        for product_url in product_urls:
            yield Request(url=get_full_url(response, product_url), callback=self.parse_product)

    def parse_product(self, response):
        product = ProductItem()
        product['TestUrl'] = response.url
        ocn = self.extract(response.xpath(
            '//script[@type="text/javascript"][contains(text(),"sectionValue")]/text()'))
        ocn_match = re.findall(r'sectionValue = "([^"]+)"', ocn)
        product['OriginalCategoryName'] = ocn_match[0]
        product['ProductName'] = self.extract(response.xpath('//h1/span[@itemprop="name"]/text()'))
        pic_url = self.extract(response.xpath('//ul/li[1]/img[@itemprop="image"]/@src'))
        if pic_url:
            pic_url = get_full_url(response, pic_url)
            product['PicURL'] = pic_url
        product['ProductManufacturer'] = 'HP'
        yield product

        mpn = self.extract_list(response.xpath('//span[@class="prodNum"]/text()'))
        if mpn:
            product_id = self.product_id(product)
            product_id['ID_kind'] = "MPN"
            product_id['ID_value'] = mpn[0]
            yield product_id

        reviews = response.xpath('//div[@itemprop="review"]')

        for review in reviews:
            user_review = ReviewItem()
            user_review['DBaseCategoryName'] = "USER"
            user_review['ProductName'] = product['ProductName']
            user_review['TestUrl'] = product['TestUrl']
            user_review['TestDateText'] = self.extract(review.xpath('./meta[@itemprop="datePublished"]/@content'))
            user_review['SourceTestRating'] = self.extract(review.xpath('.//span[@itemprop="ratingValue"]/text()'))
            user_review['Author'] = self.extract(review.xpath('.//span[@itemprop="author"]/text()'))
            user_review['TestTitle'] = self.extract(review.xpath('.//span[@itemprop="name"]/text()'))
            user_review['TestSummary'] = self.extract_all(review.xpath('.//span[@itemprop="description"]//text()'))
            yield user_review
