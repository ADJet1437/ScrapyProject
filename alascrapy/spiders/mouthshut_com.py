__author__ = 'jim'

from scrapy.http import Request

from alascrapy.items import ProductItem, ReviewItem, CategoryItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import date_format, get_full_url


class MouthshutComSpider(AlaSpider):
    name = 'mouthshut_com'
    allowed_domains = ['mouthshut.com']
    start_urls = ['http://www.mouthshut.com/computers.php',
                  'http://www.mouthshut.com/electronics.php',
                  'http://www.mouthshut.com/mobile-internet.php']

    def parse(self, response):
        category_urls = self.extract_list(response.xpath('//div[contains(@class,"categories-type2")]/a[1]/@href'))
        for category_url in category_urls:
            yield Request(url=category_url, callback=self.parse_category)
            
    def parse_category(self, response):
        category = None

        if 'category' in response.meta:
            category = response.meta['category']

        if not category:
            category = CategoryItem()
            category['category_path'] = self.extract_all(response.xpath('//div[contains(@id,"dvhierarchy")]//text()'))
            category['category_leaf'] = self.extract(response.xpath(
                    '//div[contains(@id,"dvhierarchy")]//strong/text()'))
            category['category_url'] = response.url
            yield category

        if not self.should_skip_category(category):
            product_urls = self.extract_list(response.xpath(
                    '//a[contains(@id,"litProdName")][contains(@id,"repFilterList")]/@href'))
            for product_url in product_urls:
                request = Request(url=product_url, callback=self.parse_product)
                request.meta['category'] = category
                yield request

            next_page_url = self.extract(response.xpath('//a[@class="Next"]/@href'))
            if next_page_url:
                next_page_url = get_full_url(response, next_page_url)
                request = Request(url=next_page_url, callback=self.parse_category)
                request.meta['category'] = category
                yield request
        
    def parse_product(self, response):
        product = ProductItem()
        product['TestUrl'] = response.url
        product['OriginalCategoryName'] = response.meta['category']['category_path']
        product['ProductName'] = self.extract(response.xpath('//span[@itemprop="name"]/text()'))
        product['PicURL'] = self.extract(response.xpath(
                '//img[contains(@id,"imgproduct")][not(contains(@src,"comingsoon"))]/@src'))
        product['ProductManufacturer'] = self.extract(response.xpath(
                '//span[@class="addressfont"][not(@itemprop)]/text()'))
        yield product

        review_urls = self.extract_list(response.xpath('//a[contains(@id,"completereview")]/@href'))
        for review_url in review_urls:
            request = Request(url=review_url, callback=self.parse_review)
            request.meta['product'] = product
            yield request

    def parse_review(self, response):
        user_review = ReviewItem()
        user_review['DBaseCategoryName'] = "USER"
        user_review['ProductName'] = response.meta['product']['ProductName']
        user_review['TestUrl'] = response.url
        date = self.extract(response.xpath('//meta[@itemprop="datePublished"]/@content'))
        user_review['TestDateText'] = date_format(date, "%Y-%m-%d")
        user_review['SourceTestRating'] = self.extract(response.xpath(
                '//span[@itemprop="reviewRating"]/meta[@itemprop="ratingValue"]/@content'))
        user_review['Author'] = self.extract(response.xpath('//span[@itemprop="author"]/text()'))
        user_review['TestTitle'] = self.extract(response.xpath('//span[@itemprop="name"]/text()'))
        user_review['TestSummary'] = self.extract_all(response.xpath('//div[@itemprop="description"]/p//text()'))
        yield user_review
