# -*- coding: utf8 -*-
import dateparser
import re

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider

MAX_SENTENCES = 2


class SlashcamDeSpider(AlaSpider):
    name = 'slashcam_de'
    allowed_domains = ['slashcam.de']
    start_urls = ['http://www.slashcam.de/artikel/Test/index.html']

    def parse(self, response):
        review_urls = self.extract_list(response.xpath(
            '//span[@class="a_inputdate"]/preceding-sibling'
            '::b/a/@href|//span[@class="a_inputdate"]/a/@href'))

        for review_url in review_urls:
            yield response.follow(review_url, callback=self.parse_product)

    def parse_product(self, response):
        product_xpaths = {
            "PicURL": '//meta[@property="og:image"][1]/@content',
            "OriginalCategoryName":
            '//span[@itemprop="child"]//span/text()',
            'ProductName': 'substring-after'
                           '(//h1[@class="a_titel"]/text(), "Test :")'
        }

        review_xpaths = {
            "TestTitle": "//h1[@class='a_titel']/text()",
            "TestSummary": "//meta[@name='Description']/@content",
            "Author": "//p/strong/a/text()|//p/strong/a/font/font/text()",
            'ProductName': 'substring-after'
                           '(//h1[@class="a_titel"]/text(), "Test :")',
            'Author': '//span[@itemprop="author"]/author/text()'
        }

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        source_int_id = self.extract(response.xpath(
            "//head/link[1]/@href"))
        source_internal_id = re.findall(r'post_id=(\d+)',
                                        source_int_id)
        product["source_internal_id"] = source_internal_id[0]
        review["source_internal_id"] = product["source_internal_id"]

        yield product

        test_date_xpath = "(//span[@class = 'a_inputdate'])[2]/text()"
        date = self.extract(response.xpath(test_date_xpath))
        date = date.split(',')[1].strip()
        if date:
            test_date = dateparser.parse(date)
            review["TestDateText"] = test_date.date()

        review["DBaseCategoryName"] = "PRO"

        verdict_page_xpath = "//td[@class='boxre']" \
            "/a[contains(text(), 'Fazit')]/@href"
        verdict_page_url = self.extract(response.xpath(verdict_page_xpath))

        if verdict_page_url:
            yield response.follow(
                verdict_page_url,
                callback=self.get_test_verdict,
                meta={'review': review}
            )
        else:
            yield review

    def get_test_verdict(self, response):
        review = response.meta['review']
        test_verdict_xpath = "//span[@itemprop='articleBody']/text()"
        test_verdict = self.extract(response.xpath(test_verdict_xpath))
        test_verdict = '.'.join(
            test_verdict.split('.')[0:MAX_SENTENCES]) + '.'
        review["TestVerdict"] = test_verdict

        yield review
