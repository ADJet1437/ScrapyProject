# -*- coding: utf8 -*-
from alascrapy.items import ProductIdItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider

TEST_SCALE = 100


class PCgamer_comSpider(AlaSpider):
    name = 'pcgamer_com'
    allowed_domains = ['pcgamer.com']
    start_urls = ['https://www.pcgamer.com/hardware/reviews/']

    def parse(self, response):
        next_page_xpath = "//span[@class="\
            "'listings-pagination-button listings-next ']/a/@href"
        review_urls_xpath = "//div[@data-page='1']/a[1]/@href"
        review_urls = self.extract_list(response.xpath(review_urls_xpath))

        for review_url in review_urls:
            yield response.follow(review_url,
                                  callback=self.parse_review_product)

        next_page = self.extract(response.xpath(next_page_xpath))
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def get_src_internal_id(self, response):
        id_str = self.extract(
                response.xpath( '//article[@class="review-article"]/@data-id')
                )
        return id_str

    def parse_review_product(self, response):
        src_internal_id = self.get_src_internal_id(response)

        product = self.parse_product(response)
        product['source_internal_id'] = src_internal_id
        review = self.parse_review(response)
        review['source_internal_id'] = src_internal_id
        product_id = self.parse_price(product, response)
        # prd_id got the source_internal_id from product item

        yield product
        yield review
        yield product_id

    def parse_product(self, response):
        product_xpaths = {
            'PicURL': '//meta[@property="og:image"]/@content',
            "ProductName": "//meta[@property='og:title']/@content"
        }
        product = self.init_item_by_xpaths(response, 'product', product_xpaths)
        product["ProductName"] = product["ProductName"].replace('review', '')\
            .replace('Review', '')

        ocn_xpath = '//meta[@name="news_keywords"]/@content'
        ocn = self.extract(response.xpath(ocn_xpath))
        ocn = ocn.split(',')[-1]
        product["OriginalCategoryName"] = ocn

        return product

    def parse_price(self, product, response):
        price_xpath = "//strong[contains(text(),'Price')]"\
            "/following-sibling::text()[1]"
        price_str = self.extract(response.xpath(price_xpath))

        if price_str:
            return ProductIdItem.from_product(
                product,
                kind='price',
                value=price_str
            )

    def parse_review(self, response):
        review_xpaths = {
            "ProductName": "//meta[@property='og:title']/@content",
            'TestTitle': '//meta[@property="og:title"]/@content',
            'Author': "//span[@itemprop='name']/text()",
            'SourceTestRating': "(//span[@class='score score-long'])[1]/text()",
            'TestDateText': "substring-before(//time/@datetime,'T')",
            'TestSummary': '//meta[@property="og:description"]/@content',
            'TestPros': "(//div[@class='sub-box']/ul)[1]/li/text()",
            'TestCons': "(//div[@class='sub-box']/ul)[2]/li/text()",
            'TestVerdict': "//p[@class='game-verdict']/text()"
        }

        review = self.init_item_by_xpaths(response, 'review', review_xpaths)
        review["ProductName"] = review["ProductName"].replace('review', '')\
            .replace('Review', '')
        if review["SourceTestRating"]:
            review["SourceTestScale"] = TEST_SCALE

        review['DBaseCategoryName'] = 'PRO'
        return review
