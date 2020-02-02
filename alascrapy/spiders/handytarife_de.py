# -*- coding: utf8 -*-
from alascrapy.items import ProductIdItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider

TEST_SCALE = 5
MAX_SENTENCES = 3


class HandyTarife_deSpider(AlaSpider):
    name = 'handytarife_de'
    allowed_domains = ['handytarife.de']
    start_urls = ['https://www.handytarife.de/?handy-testberichte']

    def parse(self, response):
        review_urls_xpath = "//b[contains(text(),'Weitere')]/ancestor::a/@href"\
            "|//strong[contains(text(),'Weitere')]/ancestor::a/@href"\
            "|//div[@class='tb-header'][last()]/following-sibling::a/@href"
        review_urls = self.extract_list(response.xpath(review_urls_xpath))

        for review_url in review_urls:
            yield response.follow(review_url,
                                  callback=self.parse_phone_category)

    def parse_phone_category(self, response):
        category_item_xpath = "//a[@class='article_teaser_link']/@href"
        category_item_urls = self.extract_list(response.xpath(
            category_item_xpath))

        for category_item_url in category_item_urls:
            yield response.follow(category_item_url,
                                  callback=self.parse_review_product)

    def parse_review_product(self, response):
        product = self.parse_product(response)
        review = self.parse_review(response)
        product_id = self.parse_price(product, response)
        yield product
        yield review
        yield product_id

    def parse_price(self, product, response):
        price_xpath = "(//span[@class='pricelabel'])[2]/text()|"\
            "//span[contains(text(),'Preis ohne Vertrag')]"\
            "/following-sibling::span[2]/text()"
        price_str = self.extract(response.xpath(price_xpath))

        if price_str:
            return ProductIdItem.from_product(
                product,
                kind='price',
                value=price_str
            )

    def source_int_id(self, response):
        sid_xpath = "//input[@name='PR_ID']/@value"
        sid = self.extract(response.xpath(sid_xpath))
        if sid:
            return sid
        else:
            url = response.url
            SID = url.split['='][1]
            return SID

    def parse_product(self, response):
        product_xpaths = {
            'ProductName': "//span[@itemprop='name']//text()",
            'PicURL': '//meta[@property="og:image"]/@content'
        }

        product = self.init_item_by_xpaths(response, 'product', product_xpaths)

        product['source_internal_id'] = self.source_int_id(response)
        product['OriginalCategoryName'] = 'Cell Phones'
        product['ProductManufacturer'] = product['ProductName'].split(' ')[0]

        return product

    def parse_review(self, response):
        review_xpaths = {
            'ProductName': "//span[@itemprop='name']//text()",
            'TestTitle': "//h1[@itemprop='headline']/text()",
            'Author': "//span[@itemprop='author']//text()",
            "SourceTestRating": "//span[@id='rating-value-rating_average_all']"
            "//text()",
            'TestSummary': "//div[@class='articleSummary']/p//text()"
        }

        review = self.init_item_by_xpaths(response, 'review', review_xpaths)
        rating = review["SourceTestRating"]

        if rating:
            review["SourceTestScale"] = TEST_SCALE

        if review['TestSummary']:
            review['TestSummary'] = review['TestSummary'].strip()

        review['DBaseCategoryName'] = 'PRO'

        review['source_internal_id'] = self.source_int_id(response)

        verdict_url_xpath = "//a[@class='cpPaginate'][last()]/@href"
        verdict_page = self.extract(response.xpath(verdict_url_xpath))
        if verdict_page:
            return response.follow(
                verdict_page,
                callback=self.get_test_verdict,
                meta={'review': review}
            )

        else:
            self.extract_test_verdict(response, review)
            return review

    def extract_test_verdict(self, response, review):
        author_xpath = "substring-before(//i[contains(text(),"\
            "'Redaktion handytarife.de')]/text(),'/')"
        author = self.extract(response.xpath(author_xpath))

        if author:
            review['Author'] = author

        test_verdict_xpath = "//h3[contains(text(),'Fazit')]"\
            "/following-sibling::p/text()|//strong[contains(text(),'Fazit')]"\
            "/ancestor::p/following-sibling::p/text()|//b[contains("\
            "text(),'Fazit')]/following-sibling::text()|"\
            "//span[contains(text(),'Fazit')]/following-sibling::text()"
        test_verdict = self.extract(response.xpath(test_verdict_xpath))

        if len(test_verdict) > 100:
            test_verdict = '.'.join(
                test_verdict.split('.')[0:MAX_SENTENCES]) + '.'
            review["TestVerdict"] = test_verdict.strip()

    def get_test_verdict(self, response):
        review = response.meta['review']
        self.extract_test_verdict(response, review)
        yield review
