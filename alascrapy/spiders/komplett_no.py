import re
from scrapy.http import Request

from alascrapy.items import ProductItem, ReviewItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url

#More reviews and products showed on click, scrape only the reviews that are already showing
class KomplettNoSpider(AlaSpider):
    name = 'komplett_no'
    allowed_domains = ['komplett.no']
    start_urls = ['https://www.komplett.no/department/10306/komplett-pc',
                  'https://www.komplett.no/department/10723/pc-nettbrett',
                  'https://www.komplett.no/department/10719/tv-lyd-bilde',
                  'https://www.komplett.no/department/10190/foto-video',
                  'https://www.komplett.no/department/10444/mobil',
                  'https://www.komplett.no/department/10560/hjem-fritid',
                  'https://www.komplett.no/department/10639/hvitevarer',
                  'https://www.komplett.no/department/17000/trening-velvaere']

    def parse(self, response):
        category_urls = self.extract_list(response.xpath(
            "//ul[@class='category-list']/li/a/@href"))
        for category_url in category_urls:
            yield Request(url=get_full_url(response, category_url), callback=self.parse_category)

    def parse_category(self, response):

        product_list_xpath = "//div[@class='product-list-item ']/a/@href"
        product_urls = self.extract_list(response.xpath(product_list_xpath))
        for product_url in product_urls:
            product_url = get_full_url(response, product_url)
            yield Request(url=product_url, callback=self.parse_review)


    def parse_review(self, response):

        product = ProductItem()

        productname_xpath = "//section[@class='product-main-info']//h1[@itemprop='name']/text()"
        ocn_xpath = "//script[@id='breadcrumbsScript']/@data-model"
        picurl_xpath = "//meta[@itemprop='image']/@content"
        productid_xpath = "//div[@class='product-main-info-partnumber-store']/span[@itemprop='sku']//text()"

        product['TestUrl'] = response.url
        product['OriginalCategoryName'] = re.search('(?<=:").*(?="})', self.extract(response.xpath(ocn_xpath))).group(0)
        product['ProductName'] = self.extract(response.xpath(productname_xpath))
        product['PicURL'] = get_full_url(response, self.extract(response.xpath(picurl_xpath)))
        product['source_internal_id'] = self.extract(response.xpath(productid_xpath))
        yield product

        reviews_xpath = "//div[@class='review-page']//div[@itemprop='review']"
        testTitle_xpath = ".//h3[@class='review-title']/text()"
        testSummary_xpath = ".//div[@itemprop='reviewBody']/text()"
        testRating_xpath = ".//meta[@itemprop='ratingValue']/@content"
        testAuthor_xpath = ".//span[@itemprop='author']/text()"
        testDate_xpath = ".//p[@itemprop='datePublished']/text()"


        reviews = response.xpath(reviews_xpath)

        for review_div in reviews:
            review = ReviewItem()
            review['DBaseCategoryName'] = "USER"
            review['ProductName'] = product['ProductName']
            review['TestUrl'] = product['TestUrl']
            review['source_internal_id'] = product['source_internal_id']
            review['SourceTestRating'] = self.extract(review_div.xpath(testRating_xpath))
            review['Author'] = self.extract(review_div.xpath(testAuthor_xpath))
            review['TestTitle'] = self.extract(review_div.xpath(testTitle_xpath))
            review['TestSummary'] = self.extract(review_div.xpath(testSummary_xpath))
            review['TestDateText'] = self.extract(review_div.xpath(testDate_xpath))
            yield review


