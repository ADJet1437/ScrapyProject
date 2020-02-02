# -*- coding: utf8 -*-
import dateparser
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider


class Lydogbillede_dkSpider(AlaSpider):
    name = 'lydogbillede_dk'
    allowed_domains = ['lydogbillede.dk']
    start_urls = ['http://lydogbillede.dk/test/']

    def parse(self, response):
        next_page_xpath = "//a[@class='next']/@href"
        review_urls_xpath = "//h2[@class='test-title']/a/@href"
        review_urls = self.extract_list(response.xpath(review_urls_xpath))

        for review_url in review_urls:
            yield response.follow(review_url,
                                  callback=self.parse_review_product)

        next_page = self.extract(response.xpath(next_page_xpath))
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_review_product(self, response):

        product_xpaths = {
            "source_internal_id": "substring-after(//link"
            "[@rel='shortlink']/@href, '=')",
            "ProductName": "substring-after(//div"
            "[@class='smalltesttitle']/h2, 'af:')",
            "PicURL": "//meta[@property='og:image']/@content",
            "ProductManufacturer": "//div[@class='grid@tl+']//"
            "a[@class='th-topic']/text()"
        }
        product = self.init_item_by_xpaths(response, 'product', product_xpaths)

        # http://lydogbillede.dk/test/mobil-tablet/aarets-bedste-mobiler/samsung-galaxy-s9-2/
        # i am taking the 5th item on the list which commonly the OCN
        ocn = response.url.split('/')[4]
        if not ocn.isdigit():
            product["OriginalCategoryName"] = ocn.replace('-', ' ')

        review_xpaths = {
            "source_internal_id": "substring-after(//link"
            "[@rel='shortlink']/@href, '=')",
            "SourceTestRating": "//h4[contains (.,'Engadget Score')]/following"
            "-sibling::div[1]//div[contains (@class,'t-rating')]/text()",
            "ProductName":  "substring-after(//div"
            "[@class='smalltesttitle']/h2, 'af:')",
            "Author": "substring-before(//a[@itemprop='author']/text(),'|')",
            "TestPros": "//div[@class = 'adv'][1]//text()",
            "TestCons": "//div[@class = 'adv'][2]//text()",
            "TestSummary": "//meta[@name='description']/@content",
            "TestTitle": "//div[@class='thetitle']/h1/text()"
        }
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        review["DBaseCategoryName"] = "PRO"

        # example of Author name "Af Jonas Ekelund"
        review["Author"] = review["Author"].replace('Af', '').strip()

        date_xpath = "substring-after(//a[@itemprop='author']/text(),'|')"
        date = self.extract(response.xpath(date_xpath))
        test_date = dateparser.parse(date).date()
        if test_date:
            review["TestDateText"] = test_date

        yield product
        yield review
