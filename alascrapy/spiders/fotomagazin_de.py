# -*- coding: utf8 -*-
from alascrapy.lib.generic import date_format
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider

MAX_SENTENCES = 2


class FotoMagazin_deSpider(AlaSpider):
    name = 'fotomagazin_de'
    allowed_domains = ['fotomagazin.de']
    start_urls = ['https://www.fotomagazin.de/technik/tests']

    def parse(self, response):
        next_page_xpath = "//li[@class='pager-next']/a/@href"
        review_urls_xpath = "//div[@class='content']/h2/a/@href"
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

    def parse_product(self, response):
        product_xpaths = {
            'ProductName': '//meta[@property="og:title"]/@content',
            'PicURL': '//meta[@property="og:image"]/@content'

        }

        product = self.init_item_by_xpaths(response, 'product', product_xpaths)

        product["ProductName"] = product["ProductName"].replace("Test:", '')

        ocn_xpath = 'substring-after(//div[@class="field-category"]'\
            '/a/text(),"Test")'
        original_category_name = self.extract(response.xpath(ocn_xpath))
        product["OriginalCategoryName"] = original_category_name.strip('()')\
            .replace('s', '')

        product["source_internal_id"] = self.get_source_internal_id(response)

        return product

    def get_source_internal_id(self, response):
        SI_id_xpath = "//link[@rel='shortlink']/@href"
        source_int_id = self.extract(response.xpath(SI_id_xpath))
        source_internal_id = source_int_id.split('/')[-1]

        return source_internal_id

    def parse_review(self, response):
        review_xpaths = {
            'ProductName': '//meta[@property="og:title"]/@content',
            'TestTitle': '//meta[@property="og:title"]/@content',
            'Author': '(//a[@class="username"])[1]/text()',
            "TestDateText": '(//div[@class="pane-content"])[2]/text()',
            'TestSummary': '//meta[@property="og:description"]/@content'
        }

        review = self.init_item_by_xpaths(response, 'review', review_xpaths)

        review["ProductName"] = review["ProductName"].replace("Test:", '')
        review["source_internal_id"] = self.get_source_internal_id(response)

        review["TestDateText"] = date_format(
            review["TestDateText"], "%d %b %Y")

        review['DBaseCategoryName'] = 'PRO'

        verdict_url_xpath = "//a[contains(text(),'Fazit')]/@href"
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
        test_verdict_xpath = "//strong[contains(text(),'FAZIT')]"\
            "/ancestor::h2/following-sibling::p/text()|//h2"\
            "[contains(text(),'Fazit')]/following-sibling::p/text()|"\
            "//strong[contains(text(),'FAZIT')]/ancestor::p"\
            "/following-sibling::p/text()"
        test_verdict = self.extract(response.xpath(test_verdict_xpath))
        if len(test_verdict) > 100:
            test_verdict = '.'.join(
                test_verdict.split('.')[0:MAX_SENTENCES]) + '.'
            review["TestVerdict"] = test_verdict

    def get_test_verdict(self, response):
        review = response.meta['review']
        self.extract_test_verdict(response, review)
        yield review
