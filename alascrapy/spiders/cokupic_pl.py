__author__ = 'jim'

from scrapy.http import Request

from alascrapy.items import ProductItem, CategoryItem, ReviewItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format


class CokupicPlSpider(AlaSpider):
    name = 'cokupic_pl'
    allowed_domains = ['cokupic.pl']
    start_urls = ['http://cokupic.pl/opinie']

    def parse(self, response):
        sub_category_urls = self.extract_list(response.xpath('//h3[@class="title"]/a/@href'))

        for sub_category_url in sub_category_urls:
            sub_category_url = get_full_url(response, sub_category_url)
            yield Request(url=sub_category_url, callback=self.parse_sub_category)

    def parse_sub_category(self, response):
        category_urls = self.extract_list(response.xpath(
                '(//div[@class="categoryHead"][following-sibling::div[not(descendant::li)]]//h4|//h5)/a/@href'))

        for category_url in category_urls:
            category_url = get_full_url(response, category_url)
            yield Request(url=category_url, callback=self.parse_category)

    def parse_category(self, response):
        category = None

        if 'category' in response.meta:
            category = response.meta['category']

        if not category:
            category = CategoryItem()
            category['category_path'] = self.extract_all(response.xpath('//div[contains(@class,"localizer")]/*/text()'))
            category['category_leaf'] = self.extract(response.xpath(
                    '//div[contains(@class,"localizer")]/span[last()]/text()'))
            category['category_url'] = response.url
            yield category

        if not self.should_skip_category(category):
            product_urls = self.extract_list(response.xpath(
                    '//div[contains(@class,"ckPoints")]/ancestor::div[@class="infoWrapper"]'
                    '//p[@class="title"]/a/@href'))

            for product_url in product_urls:
                product_url = get_full_url(response, product_url)+'/1/data_dodania/malejaco'
                request = Request(url=product_url, callback=self.parse_product)
                request.meta['category'] = category
                yield request

            next_page_urls = self.extract_list(response.xpath('//a[contains(@class,"right")]/@href'))
            if next_page_urls:
                next_page_url = next_page_urls[0]
                next_page_url = get_full_url(response, next_page_url)
                request = Request(url=next_page_url, callback=self.parse_category)
                request.meta['category'] = category
                yield request

    def parse_product(self, response):
        product = ProductItem()
        product['TestUrl'] = response.url
        product['OriginalCategoryName'] = response.meta['category']['category_path']
        product['ProductName'] = self.extract(response.xpath('//h1[@itemprop="itemreviewed"]/text()'))
        product['PicURL'] = self.extract(response.xpath('//div[@class="productPhotoGallery"]/div/img/@src'))
        product['ProductManufacturer'] = self.extract(response.xpath(
                '//div[@class="manufacturer"]//span[not(text()="brak")]/text()'))
        yield product

        reviews = response.xpath(
                '//div[@class="opinion"][not(descendant::a[contains(text(),"Opinia z serwisu Ceneo.pl")])]')
        for review in reviews:
            user_review = ReviewItem()
            user_review['DBaseCategoryName'] = "USER"
            user_review['ProductName'] = product['ProductName']
            user_review['TestUrl'] = product['TestUrl']
            date = self.extract(review.xpath('.//span[@class="date"]/text()'))
            user_review['TestDateText'] = date_format(date, "%Y-%m-%d")
            user_review['SourceTestRating'] = self.extract(review.xpath('.//span[@class="points"]/text()'))
            user_review['Author'] = self.extract_all(review.xpath('.//*[@class="profileName"]//text()'))
            user_review['TestSummary'] = self.extract_all(review.xpath('.//div[@class="text"]//text()'))
            user_review['TestPros'] = self.extract_all(review.xpath('.//ul[@class="pluses"]//span/text()'), '; ')
            user_review['TestCons'] = self.extract_all(review.xpath('.//ul[@class="minuses"]//span/text()'), '; ')
            yield user_review
