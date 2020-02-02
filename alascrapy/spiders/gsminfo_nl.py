__author__ = 'jim'

from scrapy.http import Request

from alascrapy.items import ProductItem, ReviewItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format


class GsminfoNlSpider(AlaSpider):
    name = 'gsminfo_nl'
    allowed_domains = ['gsminfo.nl']
    start_urls = ['https://www.gsminfo.nl/mobiele-telefoons']

    def parse(self, response):
        product_urls = self.extract_list(response.xpath('//div[@class="body"]/div/span[1]/a/@href'))
        for product_url in product_urls:
            yield Request(url=get_full_url(response, product_url+'/reviews'), callback=self.parse_product)

        next_page_url = self.extract(response.xpath('//div[@data-name="pagina"]/a[contains(@class,"next")]/@href'))
        if next_page_url:
            yield Request(url=next_page_url, callback=self.parse)

    def parse_product(self, response):
        reviews = response.xpath('//section[article[contains(@class,"review")]]')
        if reviews:
            product = ProductItem()

            product['TestUrl'] = response.url
            product['OriginalCategoryName'] = 'Cell Phones'
            product['ProductName'] = self.extract(response.xpath('//meta[@itemprop="name"]/@content'))
            pic_url = self.extract(response.xpath('//meta[@property="og:image"]/@content'))
            product['PicURL'] = get_full_url(response, pic_url)
            product['ProductManufacturer'] = self.extract(response.xpath('//meta[@itemprop="brand"]/@content'))
            yield product

            user_reviews = reviews.xpath('./article[@itemprop="review"]')

            for review in user_reviews:
                user_review = ReviewItem()
                user_review['DBaseCategoryName'] = "USER"
                user_review['ProductName'] = product['ProductName']
                user_review['TestUrl'] = product['TestUrl']
                date = self.extract(review.xpath('.//span[@class="time"]/text()'))
                user_review['TestDateText'] = date_format(date, '')
                user_review['SourceTestRating'] = self.extract(review.xpath('.//meta[@itemprop="ratingValue"]/@content'))
                user_review['Author'] = self.extract(review.xpath('.//span[@itemprop="author"]/text()'))
                user_review['TestPros'] = self.extract_all(review.xpath(
                    './/div[contains(@class,"positives")]/text()'), '; ')
                user_review['TestCons'] = self.extract_all(review.xpath(
                    './/div[contains(@class,"negatives")]/text()'), '; ')
                yield user_review

            pro_review_url = self.extract(reviews.xpath('./article[contains(@class,"expert")]/div/a/@href'))
            if pro_review_url:
                request = Request(url=get_full_url(response, pro_review_url), callback=self.parse_review)
                request.meta['product'] = product
                yield request
        
    def parse_review(self, response):
        review = ReviewItem()
        review['DBaseCategoryName'] = "PRO"
        review['ProductName'] = response.meta['product']['ProductName']
        review['TestUrl'] = response.url
        date = self.extract(response.xpath('//time/@datetime'))
        review['TestDateText'] = date_format(date, '')
        review['SourceTestRating'] = self.extract(response.xpath('//div[@itemprop="ratingValue"]/text()'))
        review['Author'] = self.extract(response.xpath('//span[@itemprop="author"]//text()'))
        review['TestTitle'] = self.extract(response.xpath('//h1/text()'))
        review['TestSummary'] = self.extract_all(response.xpath('//p[@itemprop="description"]//text()'))
        pro_con = self.extract_list(response.xpath('//p[contains(text(),"+ ") or contains(text(),"- ")]/text()'))
        review['TestPros'] = '; '.join([item for item in pro_con if item and item.strip()[0] == '+'])
        review['TestCons'] = '; '.join([item for item in pro_con if item and item.strip()[0] == '-'])
        review['TestVerdict'] = self.extract_all(response.xpath(
                '//h2[contains(text(),"onclusie")][1]/following::p[1]//text()'))
        if not review['TestVerdict']:
            review['TestVerdict'] = self.extract_all(response.xpath(
                '//h3[contains(text(),"onclusie")][1]/following::p[1]//text()'))
        yield review
