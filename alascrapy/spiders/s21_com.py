__author__ = 'jim'

from scrapy.http import Request

from alascrapy.items import ProductItem, ReviewItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import date_format, get_full_url


class S21ComSpider(AlaSpider):
    name = 's21_com'
    allowed_domains = ['s21.com']
    start_urls = ['http://www.s21.com/mobile-phones.htm', 'http://www.s21.com/tablets.htm', 'http://www.s21.com/tv.htm',
                  'http://www.s21.com/appliances.htm']

    def parse(self, response):
        product_urls = self.extract_list(response.xpath('//div[@id="mainnav"]/p/a[@class="nav"]/@href'))

        for product_url in product_urls:
            product_url = get_full_url(response, product_url)
            yield Request(url=product_url, callback=self.parse_product)
        
    def parse_product(self, response):
        product = ProductItem()
        product['TestUrl'] = response.url
        product['OriginalCategoryName'] = self.extract(response.xpath('//div[@id="mainnav"]/p[2]/b/a/text()'))
        if not product['OriginalCategoryName']:
            product['OriginalCategoryName'] = self.extract(response.xpath('//div[@id="mainnav"]/p[1]/b/a/text()'))
        product['ProductName'] = self.extract(response.xpath('//span[@class="fn"]/text()'))
        if not product['ProductName']:
            product['ProductName'] = self.extract(response.xpath('//h1/text()'))
        product['PicURL'] = self.extract(response.xpath('//img[@class="mainimage"]/@src'))
        yield product

        review = ReviewItem()
        review['DBaseCategoryName'] = "PRO"
        review['ProductName'] = product['ProductName']
        review['TestUrl'] = product['TestUrl']
        review['TestDateText'] = self.extract(response.xpath('//span[@class="dtreviewed"]/span/@title'))
        rate = self.extract(response.xpath('//img[@class="rating"]/@alt'))
        review['SourceTestRating'] = rate.split(' ')[0]
        review['Author'] = self.extract(response.xpath('//span[@class="reviewer"]/span/@title'))
        review['TestTitle'] = self.extract_all(response.xpath('//h1//text()'))
        review['TestSummary'] = self.extract_all(response.xpath('//span[@class="summary"]//text()'))
        review['TestVerdict'] = self.extract_all(response.xpath('//h3[last()]/following-sibling::p[1]//text()'))
        yield review

        reviews = response.xpath('//div[contains(@id,"review")]/p[1][b]')
        for review in reviews:
            user_review = ReviewItem()
            user_review['DBaseCategoryName'] = "USER"
            user_review['ProductName'] = product['ProductName']
            user_review['TestUrl'] = product['TestUrl']
            date = self.extract(review.xpath('./b[3]/following-sibling::text()[1]'))
            user_review['TestDateText'] = date_format(date, '')
            rate = self.extract(review.xpath('./img/@src'))
            if rate:
                user_review['SourceTestRating'] = rate.split('/')[1].split('s')[0]
            user_review['Author'] = self.extract(review.xpath('./b[1]/following-sibling::text()[1]'))
            user_review['TestSummary'] = self.extract_all(review.xpath('./br[1]/following-sibling::text()'))
            yield user_review
