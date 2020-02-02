# -*- coding: utf8 -*-
from alascrapy.items import ProductIdItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider

TEST_SCALE = 5


class MacWorld_comSpider(AlaSpider):
    name = 'macworld_com'
    allowed_domains = ['macworld.com']
    start_urls = ['https://www.macworld.com/reviews/']

    def parse(self, response):
        load_more_xpath = "//a[@id='more-stories-btn']/@href"
        review_urls_xpath = "//div[@class='excerpt-text']/p/a/@href"
        review_urls = self.extract_list(response.xpath(review_urls_xpath))

        for review_url in review_urls:
            yield response.follow(review_url,
                                  callback=self.parse_review_product)

        load_more = self.extract(response.xpath(load_more_xpath))
        if review_urls:
            yield response.follow(load_more, callback=self.parse)

    def parse_review_product(self, response):
        product = self.parse_product(response)
        review = self.parse_review(response)
        product_id = self.parse_price(product, response)
        yield product
        yield review
        yield product_id

    def get_product_name(self, response):
        name_xpath = self.extract(response.xpath("//meta"
                                                 "[@property='og:title']/@content"))
        name = name_xpath.replace('review', '')
        return name

    def parse_product(self, response):
        product_xpaths = {
            'PicURL': '//meta[@property="og:image"]/@content',
            "OriginalCategoryName": "//nav/ul/li[last()]/a/span/text()",
            'source_internal_id': "substring-after(//body/@id,'article')"
        }
        product = self.init_item_by_xpaths(response, 'product', product_xpaths)
        product['ProductName'] = self.get_product_name(response)

        return product

    def parse_price(self, product, response):
        price_xpath = "(//div[@class='price-msrp'])[1]/a/text()"
        price_str = self.extract(response.xpath(price_xpath))

        if price_str:
            return ProductIdItem.from_product(
                product,
                kind='price',
                value=price_str
            )

    def parse_review(self, response):
        review_xpaths = {
            'TestTitle': '//meta[@property="og:title"]/@content',
            'Author': "//a[@rel='author']/span/text()",
            'source_internal_id': "substring-after(//body/@id,'article')",
            'SourceTestRating': "(//meta[@itemprop='ratingValue'])"
            "[1]/@content",
            'TestDateText': "substring-before(//span[@class='pub-date']"
            "/@content,'T')",
            'TestSummary': '//meta[@property="og:description"]/@content',
            'TestPros': "//div[@class='product-pros']/ul/li/text()",
            'TestCons': "//div[@class='product-cons']/ul/li/text()",
            'TestVerdict': "//p[@itemprop='description']/text()"
        }

        review = self.init_item_by_xpaths(response, 'review', review_xpaths)

        if review["SourceTestRating"]:
            review["SourceTestScale"] = TEST_SCALE
        
        review['ProductName'] = self.get_product_name(response)

        review['DBaseCategoryName'] = 'PRO'
        return review
