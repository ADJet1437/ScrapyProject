from scrapy.http import Request
from alascrapy.spiders.base_spiders.bazaarvoice_spider import BVNoSeleniumSpider
from alascrapy.items import ProductItem, ProductIdItem

class SamsungUkSpider(BVNoSeleniumSpider):
    name = 'samsung_uk'
    allowed_domains = ["samsung.com"]
    start_urls = ['http://reviews.uk.samsung.com/7463-en_gb/allreviews.htm']
    default_kind = 'MPN'

    def parse_product(self, response):
        category = response.meta['category']
        review_url = response.meta['review_url']

        product_name_xpath='//input[@id="display_name"]/@value'
        product_name_alt_xpath='//h1[@itemprop="name"]/text()'
        pic_url_xpath = '//meta[@property="og:image"]/@content'
        source_internal_id_xpath='//input[@id="modelCode"]/@value'
        source_internal_id_alt_xpath='//input[@id="model_code"]/@value'

        product = ProductItem()
        product["source_internal_id"] = self.extract(response.xpath(source_internal_id_xpath))
        product["ProductName"] = self.extract(response.xpath(product_name_xpath))
        product["OriginalCategoryName"] = category['category_path']
        product["PicURL"] = self.extract(response.xpath(pic_url_xpath))
        product["ProductManufacturer"] = "Samsung"
        product["TestUrl"] = response.url
        if not product['source_internal_id']:
            product["source_internal_id"] = self.extract(response.xpath(source_internal_id_alt_xpath))
        if not product['ProductName']:
            product["ProductName"] = self.extract(response.xpath(product_name_alt_xpath))            

        if product["ProductName"]:
            yield product

            product_id = ProductIdItem()
            product_id['source_internal_id'] = product["source_internal_id"]
            product_id['ProductName'] = product["ProductName"]
            product_id['ID_kind'] = "MPN"
            product_id['ID_value'] = product["source_internal_id"]
            yield product_id

            request = Request(url=review_url, callback=self.parse_reviews)
            request.meta['product'] = product
            request.meta['product_id'] = product_id
            yield request
        else:
            request = Request(url=review_url, callback=self.parse_reviews)
            request.meta['category'] = category
            request.meta['product_url'] = response.url
            request.meta['parse_product'] = True
            request.meta['brand'] = "Samsung"
            yield request

