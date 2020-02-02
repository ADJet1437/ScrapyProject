# -*- coding: utf8 -*-
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider

TEST_SCALE = 100


class Digitalt_tvSpider(AlaSpider):
    name = 'digitalt_tv'
    allowed_domains = ['digitalt.tv']
    start_urls = ['https://digitalt.tv/kategori/anmeldelser/']

    def parse(self, response):
        review_urls_xpath = "//h3[@class='post-title']/a/@href"
        review_urls = self.extract_list(response.xpath(review_urls_xpath))
        next_page_xpath = "//a[@rel='next']/@href"

        for review_url in review_urls:
            yield response.follow(review_url,
                                  callback=self.parse_review_product)

        next_page = self.extract(response.xpath(next_page_xpath))
        if next_page:
            yield response.follow(next_page,
                                  callback=self.parse)

    def parse_review_product(self, response):
        product = self.parse_product(response)
        review = self.parse_review(response)
        yield product
        yield review

    def get_product_name(self, response):
        name_xpath = "//meta[@property='og:title']/@content"
        name_ = self.extract(response.xpath(name_xpath))
        name = name_.split(u'–')
        if name[0]:
            productname = name[0].replace(
                'Test: ', '').replace('Test', '').replace('test', '')
        else:
            productname = name_xpath.replace('Test', '').replace('test', '')

        return productname

    def parse_product(self, response):
        product_xpaths = {
            'PicURL': '//meta[@property="og:image"]/@content',
            'OriginalCategoryName': "//meta[@property='article:section']"
            "/@content",
            'ProductManufacturer': "//meta[@property='article:tag']/@content",
            'source_internal_id': "substring-after("
            "//link[@rel='shortlink']/@href, '=')"
        }

        product = self.init_item_by_xpaths(response, 'product', product_xpaths)
        product["ProductName"] = self.get_product_name(response)

        return product

    def parse_review(self, response):
        review_xpaths = {
            'TestTitle': '//meta[@property="og:title"]/@content',
            'source_internal_id': "substring-after("
            "//link[@rel='shortlink']/@href, '=')",
            'Author': "//a[@rel='author']/text()",
            "SourceTestRating":  "//span[@property='ratingValue']/text()",
            "TestDateText": "substring-before("
            "//meta[@property='article:published_time']/@content,'T')",
            'TestSummary': '//meta[@property="og:description"]/@content',
            'TestPros': "//div[@class='rwp-pros']/li/text()|"
            "//p[@class='plus']/text()|"
            "//div[@class='rwp-pros']/p/text()",
            'TestCons': "//div[@class='rwp-cons']/li/text()|"
            "//p[@class='minus']/text()|//div[@class='rwp-cons']/p/text()"
        }

        review = self.init_item_by_xpaths(response, 'review', review_xpaths)

        if review["SourceTestRating"]:
            review["SourceTestScale"] = TEST_SCALE

        if review["TestPros"]:
            review["TestPros"] = review["TestPros"].replace('+', '')

        if review["TestCons"]:
            review["TestCons"] = review["TestCons"].replace(u'–', '')

        review['DBaseCategoryName'] = 'PRO'
        review["ProductName"] = self.get_product_name(response)

        return review
