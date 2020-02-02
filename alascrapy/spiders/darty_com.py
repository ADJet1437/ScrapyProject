__author__ = 'jim'

from scrapy.http import Request

from alascrapy.items import ProductItem, CategoryItem, ReviewItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format


class DartyComSpider(AlaSpider):
    name = 'darty_com'
    allowed_domains = ['darty.com']
    start_urls = ['http://darty.com/']

    def parse(self, response):
        sub_category_urls = self.extract_list(response.xpath(
                "//ul[@class='level-2']/li/a[contains(@href,'nav')]/@href"))

        for sub_category_url in sub_category_urls:
            yield Request(url=get_full_url(response, sub_category_url), callback=self.parse_sub_category)

    def parse_sub_category(self, response):
        category_urls = self.extract_list(response.xpath(
                '//li[@class="visible" or @class="supplementaire"]/a[contains(@href,"achat") or contains(@href,"cat=")]/@href'))

        for category_url in category_urls:
            yield Request(url=get_full_url(response, category_url), callback=self.parse_category)

    def parse_category(self, response):
        container_style = response.xpath("//div[contains(@class, 'product_detail')]")

        if container_style:
            category = CategoryItem()
            category['category_path'] = self.extract_all(
                    response.xpath('//div[@id="header-breadcrumb-zone"]//a/text()'), " > ")
            category['category_leaf'] = self.extract(response.xpath(
                    '//div[@id="header-breadcrumb-zone"]//li[last()]/a/text()'))
            category['category_url'] = response.url
            yield category

            if not self.should_skip_category(category):
                filtered_category_url = response.url+'?p=200&avis=100'
                request = Request(url=filtered_category_url, callback=self.parse_filtered_category)
                request.meta['ocn'] = category['category_path']
                yield request

    def parse_filtered_category(self, response):
        next_page_link = self.extract(response.xpath("//div[@id='main_pagination_bottom']//a[contains(text(), 'Page suivante')]/@href"))
        if next_page_link:
            next_page_link = get_full_url(response, next_page_link)
            request = Request(url=next_page_link, callback=self.parse_filtered_category)
            request.meta['ocn'] = response.meta['ocn']
            yield request

        product_urls = self.extract_list(response.xpath('//h2/a/@href'))
        for product_url in product_urls:
            product_url = get_full_url(response, product_url)
            request = Request(url=product_url, callback=self.parse_product)
            request.meta['ocn'] = response.meta['ocn']
            yield request

    def parse_product(self, response):
        product = ProductItem()

        product['TestUrl'] = response.url
        product['OriginalCategoryName'] = response.meta['ocn']
        product['ProductName'] = self.extract_all(response.xpath('//div[@itemprop="name" or contains(@class,"product_name")]/span//text()'))
        if not product['ProductName']:
            product['ProductName'] = self.extract_all(response.xpath('//div[@itemprop="name" or contains(@class,"product_name")]//text()'))
        product['PicURL'] = self.extract(response.xpath('//img[@itemprop="image"]/@src'))
        product['ProductManufacturer'] = self.extract(response.xpath('//a[@id="darty_product_brand"]/text()'))
        product['source_internal_id'] = self.extract(response.xpath('//@data-comparator-codic'))
        yield product

        reviews = response.xpath('//div[contains(@class,"bloc_reviews_item_full")]')
       
        for review in reviews:
            user_review = ReviewItem()
            user_review['DBaseCategoryName'] = "USER"
            user_review['ProductName'] = product['ProductName']
            user_review['TestUrl'] = product['TestUrl']
            user_review['source_internal_id'] = product['source_internal_id']
            date = self.extract(review.xpath('.//span/text()'))
            user_review['TestDateText'] = date_format(date.strip('Avis soumis le '), '%d/%m/%Y')
            user_review['SourceTestRating'] = self.extract(review.xpath('.//div[@class="bloc_reviews_note"]/text()[1]'))
            user_review['Author'] = self.extract(review.xpath('.//b/text()'))
            user_review['TestTitle'] = self.extract(review.xpath('.//h3/text()'))
            user_review['TestSummary'] = self.extract_all(review.xpath('.//p[contains(@class,"text")]//text()'))
            yield user_review
