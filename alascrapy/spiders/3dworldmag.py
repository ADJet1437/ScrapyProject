# -*- coding: utf8 -*-

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider

TEST_SCALE = 10


class ThreeDWorldMagSpider(AlaSpider):
    name = '3dworldmag'
    # Both the start_url and allowed domains are different from the spider name
    # This is because 3dworldmag redirects to creativebloq.com
    allowed_domains = ['creativebloq.com']
    start_urls = ['https://www.creativebloq.com/reviews/archive']

    def parse(self, response):
        review_urls_xpath = "//ul[@class='smaller indented basic-list']"\
            "/li/ul/li/a/@href"
        review_urls = self.extract_list(response.xpath(review_urls_xpath))

        for review_url in review_urls:
            yield response.follow(review_url,
                                  callback=self.parse_archive)

    def parse_archive(self, response):
        category_item_xpath = "//ul[@class='basic-list']/li/ul/li/a/@href"
        category_item_urls = self.extract_list(response.xpath(
            category_item_xpath))

        for category_item_url in category_item_urls:
            yield response.follow(category_item_url,
                                  callback=self.parse_review_product)

    def get_src_internal_id(self, response):
        id_str = self.extract(response.xpath(
                        '//article[@class="review-article"]/@data-id'))
        return id_str

    def parse_review_product(self, response):
        src_internal_id = self.get_src_internal_id(response)

        product = self.parse_product(response)
        review = self.parse_review(response)

        review['source_internal_id'] = src_internal_id
        product['source_internal_id'] = src_internal_id

        yield product
        yield review

    def parse_product(self, response):
        product_xpaths = {
            'PicURL': '//meta[@property="og:image"]/@content',
            'OriginalCategoryName': "//div[@class='tag']/a/text()"
        }

        product = self.init_item_by_xpaths(response, 'product', product_xpaths)
        product['ProductName'] = self.get_productname(response)

        return product

    def get_productname(self, response):
        name = self.extract(response.xpath(
            '//meta[@property="og:title"]/@content'))
        productname = name.replace('review', ''
                                   ).replace('REVIEW: ', ''
                                             ).replace(': review', '').replace(
                                       'Review:', '')
        productname = productname.strip()
        return productname

    def parse_review(self, response):
        review_xpaths = {
            'TestTitle': '//meta[@property="og:title"]/@content',
            'Author': '//span[@itemprop="name"]/text()',
            "SourceTestRating": "//meta[@itemprop='ratingValue']/@content|"
            "//h3[contains(text(),'Score')]/text()|"
            "//p[contains(text(),'Score')]/text()",
            "TestDateText": "substring-before(//time["
            "@itemprop='datePublished']/@datetime,'T')",
            'TestSummary': '//meta[@property="og:description"]/@content',
            'TestPros': "(//h4/following-sibling::ul)[1]/li/text()|"
            "//h3[@id='uppers']/following-sibling::ul[1]/li/text()",
            'TestCons': "(//h4/following-sibling::ul)[2]/li/text()|"
            "//h3[@id='downers']/following-sibling::ul[1]/li/text()",
            'TestVerdict': '//h3[contains(text(),"Our Verdict")]'
            '/following-sibling::p/text()'
        }

        review = self.init_item_by_xpaths(response, 'review', review_xpaths)
        rating = review["SourceTestRating"]

        if rating:
            review["SourceTestRating"] = rating.replace('Score: ', ''
                                                        ).replace('/10', '')
            review["SourceTestScale"] = TEST_SCALE

        review['DBaseCategoryName'] = 'PRO'
        review['ProductName'] = self.get_productname(response)

        return review
