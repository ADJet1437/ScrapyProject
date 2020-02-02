# -*- coding: utf8 -*-
import re
from scrapy.http import Request
from alascrapy.items import ReviewItem, ProductItem
from alascrapy.lib.generic import get_full_url, date_format
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider

MAX_SENTENCES = 2


class DigitalKameraSpider(AlaSpider):
    name = 'digitalkamera_de'
    allowed_domains = ['digitalkamera.de']
    start_urls = ['https://www.digitalkamera.de/Testbericht/',
                  'https://www.digitalkamera.de/Objektiv-Test/',
                  'https://www.digitalkamera.de/Stativ-Test/',
                  'https://www.digitalkamera.de/Rucksack-Test/',
                  'https://www.digitalkamera.de/Zubeh%C3%B6r-Test/',
                  'https://www.digitalkamera.de/Software/']

    def parse(self, response):
        next_page_xpath = "(//div[@class='paging-elements']/a)[1]/@href"
        review_urls_xpath = "//h2/a/@href"
        review_urls = self.extract_list(response.xpath(review_urls_xpath))

        for review_url in review_urls:
            yield response.follow(
                review_url, callback=self.parse_review_products)

        next_page = self.extract(response.xpath(next_page_xpath))
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_review_products(self, response):
        product_xpaths = {
            "PicURL": "//meta[@property='og:image']/@content|"
                      "(//tr/td/img/@src)[1]",
            "ProductManufacturer":
                "(//div/select/option[@selected='selected'])[1]/text()",
            "OriginalCategoryName":
            "//ul[@class='nav subnav']/li/a[@class='selected']/text()"
        }

        review_xpaths = {"TestTitle": "//meta[@property='og:title']/@content",
                         "TestSummary": "//meta[@name='description']/@content",
                         "Author": "//p/strong/a/text()|"
                                   "//p/strong/a/font/font/text()"
                         }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        title_xpath = "//meta[@property='og:title']/@content"
        title = self.extract(response.xpath(title_xpath))
        if title:
            product_name = title.replace('Testbericht:', '').replace(
                'Praxistest:', '').strip()
            product["ProductName"] = product_name
            review["ProductName"] = product_name
        source_int_id = self.extract(
            response.xpath("//meta[@property='og:url']/@content"))
        source_internal_id = re.findall(r'/(\d+)', source_int_id)
        source_internal_id = " ".join(source_internal_id)
        product["source_internal_id"] = source_internal_id.strip("['u]")

        yield product

        test_date = "//span[@class='dkDate']/font/font/text()|"\
                    "//span[@class='dkDate']/text()"
        test_date_text = self.extract(response.xpath(test_date))
        if test_date_text:
            review["TestDateText"] = date_format(test_date_text, "%d %b %Y")
        review["DBaseCategoryName"] = "PRO"
        review["source_internal_id"] = source_internal_id.strip("['u]")
        verdict_page_xpath = "//span[@class='inArticleNavigation']/a/@href"
        verdict_page_url = self.extract(response.xpath(verdict_page_xpath))
        if verdict_page_url:
            response.follow(verdict_page_url,
                            callback=self.get_test_verdict,
                            meta={'review': review})
        else:
            self.extract_test_verdict(response, review)
            yield review

    def extract_test_verdict(self, response, review):
        test_verdict_xpath = "//h3[contains("\
            "text(), 'Fazit')]/following-sibling::p/text()|"\
            "//strong[contains(text(), 'Fazit')]/ancestor::p/text()|"\
            "//b[contains(text(), 'Fazit')]/ancestor::p/text()|"\
            "//p[contains(text(), 'Fazit')]/text()"
        test_pros_xpath = "//ul[@class='kurzbew-vorteil']/li/text()"
        test_cons_xpath = "//ul[@class='kurzbew-nachteil']/li/text()"

        review["TestPros"] = self.extract(response.xpath(test_pros_xpath))
        review["TestCons"] = self.extract(response.xpath(test_cons_xpath))
        test_verdict = self.extract(response.xpath(test_verdict_xpath))
        # The condition below is to get first 2 sentence of the conclusion ,
        # because it most atimes contains multiple paragraphs.
        if len(test_verdict) > 100:
            test_verdict = '.'.join(
                test_verdict.split('.')[0:MAX_SENTENCES]) + '.'
            review["TestVerdict"] = test_verdict

    def get_test_verdict(self, response):
        review = response.meta['review']
        self.extract_test_verdict(response, review)
        yield review
