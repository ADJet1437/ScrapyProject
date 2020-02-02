                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        # -*- coding: utf8 -*-
from scrapy.http import Request

from alascrapy.lib.generic import get_full_url, date_format
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider


class KitguruSpider(AlaSpider):
    name = 'kitguru'
    allowed_domains = ['kitguru.net']
    start_urls = ['https://www.kitguru.net/reviews/']

    def parse(self, response):
        next_page_xpath = "//div/span[@id='tie-next-page']/a/@href"
        review_url_xpath = "//h2[@class='post-box-title']/a/@href"
        review_urls = self.extract_list(response.xpath(review_url_xpath))

        for review_url in review_urls:
            review_url = get_full_url(response, review_url)
            request = Request(review_url, callback=self.parse_review)
            yield request

        next_page = self.extract(response.xpath(next_page_xpath))
        if next_page:
            next_page = get_full_url(response, next_page)
            request = Request(next_page, callback=self.parse)
            yield request

    def parse_review(self, response):
        product_xpaths = { "PicURL": "//meta[@property='og:image']/@content"
                         }

        review_xpaths = { "TestTitle": "//meta[@property='og:title'][2]/@content",
                          "TestSummary": "//meta[@property='og:description']/@content",
                          "Author": "//p/span[@class='post-meta-author']/a/text()",
                         # sometimes there are two repeated rating for reviews,
                         # using [1] to make sure only get one copy of the review rating
                          "SourceTestRating": "(//div[@class='gdrts-rating-text']/strong)[1]/text()",
                          "TestDateText": "//meta[@property='article:published_time']/@content"
                        }

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        try:
            product_name = ""
            title_xpath = "//meta[@property='og:title'][2]/@content"
            title = self.extract(response.xpath(title_xpath))
            ocn_xpath = "//span/a[@rel='category tag'][not(contains(text(),'Featured Tech Reviews'))]/text()"
            original_category_name = self.extract_all(response.xpath(ocn_xpath), " | ")
            product_name = title.replace('Review', '').replace('review', '').strip()
            source_int_id = self.extract(response.xpath("//link[@rel='shortlink']/@href"))
            source_internal_id = source_int_id.split("=", 1)[1]
            product["source_internal_id"] = source_internal_id
            product["ProductName"] = product_name
            product["OriginalCategoryName"] = original_category_name
            yield product

            TEST_SCALE = 10
            review["TestDateText"] = date_format(review["TestDateText"], "%d %b %Y")
            review["DBaseCategoryName"] = "PRO"
            review["SourceTestScale"] = TEST_SCALE
            review["ProductName"] = product_name
            review["source_internal_id"] = source_internal_id
            verdict_page_xpath = "//div[@class='page-link']/a[last()]/@href"

            test_verdict_xpath = "//strong[contains(text(),'KitGuru says:')]/text() |" \
                                 "//strong/em[contains(text(),'KitGuru says:')]/text() |" \
                                 "//strong/span[contains(text(),'Kitguru says:')]/text()|" \
                                 "//strong/em/span[contains(text(),'KitGuru says:')]/text()|"\
                                 "//strong/span[contains(text(),'KitGuru says:')]/text()|"\
                                 "//span/em/strong[contains(text(),'Kitguru says:')]/text()"

            test_pros_xpath = "//strong[contains(text(),'Pros')]/ancestor::p/following-sibling::ul[1]/li/text() | " \
                              "//strong/span[contains(text(),'Pros')]/ancestor::p/following-sibling::ul[1]/li/text()|" \
                              "//strong/em[contains(text(),'Pros')]/ancestor::p/following-sibling::ul[1]/li/text() |" \
                              "//strong/em/span[contains(text(),'Pros')]/ancestor::p/following-sibling::ul[1]/li/text()|"\
                              "//em[contains(text(),'Pros')]/ancestor::p/following-sibling::ul[1]/li/text()|"\
                              "//strong[contains(text(),'Pros')]/ancestor::p/following-sibling::ul[1]/li/span/text()"

            test_cons_xpath = "//strong[contains(text(),'Cons')]/ancestor::p/following-sibling::ul[1]/li/text() | " \
                              "//strong/span[contains(text(),'Cons')]/ancestor::p/following-sibling::ul[1]/li/text() | " \
                              "//strong/em[contains(text(),'Cons')]/ancestor::p/following-sibling::ul[1]/li/text() |" \
                              "//strong/em/span[contains(text(),'Cons')]/ancestor::p/following-sibling::ul[1]/li/text()|"\
                              "//em[contains(text(),'Cons')]/ancestor::p/following-sibling::ul[1]/li/text()|"\
                              "//strong[contains(text(),'Cons')]/ancestor::p/following-sibling::ul[1]/li/span/text()"

            verdict_page_url = self.extract(response.xpath(verdict_page_xpath))
            if verdict_page_url:
                verdict_page_url = get_full_url(response, verdict_page_url)
                request = Request(verdict_page_url, callback=self.get_test_verdict)
                request.meta['review'] = review
                request.meta['test_verdict_xpath'] = test_verdict_xpath
                request.meta['test_pros_xpath'] = test_pros_xpath
                request.meta['test_cons_xpath'] = test_cons_xpath
                yield request
            else:
                review["TestPros"] = self.extract(response.xpath(test_pros_xpath))
                review["TestCons"] = self.extract(response.xpath(test_cons_xpath))
                review["TestVerdict"] = self.extract(response.xpath(test_verdict_xpath))
                if review["TestVerdict"]:
                    review["TestVerdict"] = review["TestVerdict"].replace('KitGuru says:', '').strip()
                yield review
        except:
            pass

    def get_test_verdict(self, response):
        review = response.meta['review']
        test_verdict_xpath = response.meta['test_verdict_xpath']
        test_pros_xpath = response.meta['test_pros_xpath']
        test_cons_xpath = response.meta['test_cons_xpath']
        review["TestPros"] = self.extract(response.xpath(test_pros_xpath))
        review["TestCons"] = self.extract(response.xpath(test_cons_xpath))
        review["TestVerdict"] = self.extract(response.xpath(test_verdict_xpath))
        if review["TestVerdict"]:
            review["TestVerdict"] = review["TestVerdict"].replace('KitGuru says:', '').strip()
        yield review
