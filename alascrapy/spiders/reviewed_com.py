__author__ = 'jim'

from scrapy.http import Request

from alascrapy.items import ProductItem, ReviewItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import date_format
from alascrapy.lib.selenium_browser import SeleniumBrowser


class ReviewedComSpider(AlaSpider):
    name = 'reviewed_com'
    allowed_domains = ['reviewed.com']
    start_urls = ['http://www.reviewed.com/search/products?sort=review_publish_on,desc&has_review=true']
            
    def parse(self, response):
        with SeleniumBrowser(self, response) as browser:
            seletor = browser.get(response.url)

            product_urls = self.extract_list(seletor.xpath('//div[@class="media-body"]/a/@ng-href'))
            for product_url in product_urls:
                yield Request(url=product_url, callback=self.parse_product)
        
    def parse_product(self, response):
        product = ProductItem()
        product['TestUrl'] = response.url
        product['OriginalCategoryName'] = self.extract(response.xpath('//a[@class="category"]/text()'))
        product['ProductName'] = self.extract(response.xpath('//meta[@itemprop="itemreviewed"]/@content'))
        product['PicURL'] = self.extract(response.xpath('//div[@class="retail-offer-cta"]/img/@src'))
        product['ProductManufacturer'] = self.extract(response.xpath('//meta[@name="brand"]/@content'))
        yield product

        review = ReviewItem()
        review['DBaseCategoryName'] = "PRO"
        review['ProductName'] = product['ProductName']
        review['TestUrl'] = response.url
        date = self.extract(response.xpath('//strong[@itemprop="name"]/parent::p/text()[last()]'))
        review['TestDateText'] = date_format(date, '')
        review['SourceTestRating'] = self.extract(response.xpath('//span[@itemprop="ratingValue"]/text()[1]'))
        review['Author'] = self.extract(response.xpath('//strong[@itemprop="name"]/a/text()'))
        review['TestTitle'] = self.extract(response.xpath('//h1/text()'))
        review['TestSummary'] = self.extract_all(response.xpath('//h2[@itemprop="headline"]/text()'))
        review['TestVerdict'] = self.extract_all(response.xpath(
                '//span[@itemprop="reviewBody"]/div[@class="page_section"][last()]/p[contains(text()," ")][1]//text()'))
        award = response.xpath('//div[@class="header"]//ul[contains(@class,"awards")]/li')
        if award:
            review['award'] = self.extract(award[0].xpath('./img/@alt'))
            review['AwardPic'] = self.extract(award[0].xpath('./img/@src'))
        yield review
