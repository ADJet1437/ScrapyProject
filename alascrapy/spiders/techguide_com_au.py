# -*- coding: utf8 -*-
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider

TEST_SCALE = 100
TEN = 10


class TechGuide_Com_AuSpider(AlaSpider):
    name = 'techguide_com_au'
    allowed_domains = ['techguide.com.au']
    start_urls = ['http://www.techguide.com.au/reviews/']

    def parse(self, response):
        next_page_xpath = "//a[@class='next page-numbers']/@href"
        review_urls_xpath = "//h2[@class='title']/a/@href"
        review_urls = self.extract_list(response.xpath(review_urls_xpath))

        for review_url in review_urls:
            yield response.follow(review_url,
                                  callback=self.parse_review_product)

        next_page = self.extract(response.xpath(next_page_xpath))
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_review_product(self, response):
        product = self.parse_product(response)
        review = self.parse_review(response)
        yield product
        yield review

    def get_product_name(self, response):
        product_name_xpath = '//meta[@property="og:title"]/@content'
        name = self.extract(response.xpath(product_name_xpath))
        name = name.split(' -')[0]
        product_name = name.replace('review', '').replace('Review:', '')
        return product_name

    def parse_product(self, response):
        product_xpaths = {
            'PicURL': '//meta[@property="og:image"]/@content',
            'source_internal_id': "substring-after(//link[@rel='shortlink']"
            "/@href, '=')",
            "OriginalCategoryName": "//div[@class='post-header-title']/div"
            "/span/a[not(contains(text(),'Latest'))]/text()"
        }

        product = self.init_item_by_xpaths(response, 'product', product_xpaths)

        product["ProductName"] = self.get_product_name(response)
        ocn = product["OriginalCategoryName"]

        if ocn:
            product["OriginalCategoryName"] = ocn.replace('Reviews', '').strip()

        return product

    def parse_review(self, response):
        review_xpaths = {
            'TestTitle': "//meta[@property='og:title']/@content",
            'Author': "//span[@class='post-author-name']/b/text()",
            'source_internal_id': "substring-after(//link[@rel='shortlink']"
            "/@href, '=')",
            "SourceTestRating": "//span[@class='rate']/text()|"
            "//div[@class='review-final-score']/h3/text()",
            "TestDateText": "substring-before(//meta"
            "[@property='article:published_time']/@content,'T')",
            'TestSummary': '//meta[@property="og:description"]/@content',
            'TestPros': "//aside[@class='review-pros-section']/ul/li/text()|"
            "//strong[contains(text(),'PROS')]/following-sibling::text()",
            'TestCons': "//aside[@class='review-cons-section']/ul/li/text()|"
            "//strong[contains(text(),'CONS')]/following-sibling::text()",
            'TestVerdict': "//div[@class='review-description']/p/text()|"
            "//strong[contains(text(),'VERDICT')]/following-sibling::text()|"
            "//strong[contains(text(),'VERDICT')]/ancestor::p"
            "/following-sibling::p/text()"
        }

        review = self.init_item_by_xpaths(response, 'review', review_xpaths)
        review["ProductName"] = self.get_product_name(response)
        souce_rating = review["SourceTestRating"]
        title = review["TestTitle"]

        if souce_rating:
            review["SourceTestScale"] = TEST_SCALE

        if souce_rating < TEN:
            review["SourceTestRating"] = souce_rating * TEN

        if title:
            review["TestTitle"] = title.replace('- Tech Guide', '')

        review['DBaseCategoryName'] = 'PRO'

        return review
