# -*- coding: utf8 -*-
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider

TEST_SCALE = 100

# Note that OriginalCategoryName is hardcoded to electronik.


class TestberichteBlogger_deSpider(AlaSpider):
    name = 'testberichte-blogger_de'
    allowed_domains = ['testberichte-blogger.de']
    start_urls = ['http://www.testberichte-blogger.de/elektronik']

    def parse(self, response):
        sub_category_urls = self.extract_list(response.xpath(
            "//div[@class='randrund']/p/a/@href|//div["
            "@class='content']/p/a/@href"))

        if sub_category_urls:
            for sub_category_url in sub_category_urls:
                yield response.follow(sub_category_url,
                                      callback=self.parse_category)

    def parse_category(self, response):
        date_xpath = self.extract(response.xpath(
            "substring-after(//div/h1, '(')"))
        date = date_xpath.split(')')
        date = date[0]
        category_item_xpath = "//td/a/@href"
        category_item_urls = self.extract_list(response.xpath(
            category_item_xpath))

        for category_item_url in category_item_urls:
            yield response.follow(category_item_url,
                                  callback=self.parse_review_product,
                                  meta={'date': date})

    def get_product_name(self, response):
        name_xpath = self.extract(response.xpath("//h1/text()"))
        name = name_xpath.split(u'–')
        if name[0]:
            productname = name[0].replace('Test', '')
        else:
            productname = name_xpath.replace('Test', '')

        return productname

    def parse_review_product(self, response):
        product_xpaths = {
            'PicURL': '(//div/a/img)[1]/@src',
            'source_internal_id': "substring-after(//link[@rel='shortlink']"
            "/@href, '=')"
        }

        product = self.init_item_by_xpaths(response, 'product', product_xpaths)

        product["ProductName"] = self.get_product_name(response)

        product["OriginalCategoryName"] = "elektronik"

        yield product

        review_xpaths = {
            'TestTitle': '//h1/text()',
            'source_internal_id': "substring-after(//link[@rel='shortlink']"
            "/@href, '=')",
            "SourceTestRating": "substring-before("
            "//td/strong/strong/text(),'%')",
            'TestSummary': '//p/i/text()',
            'TestPros': "//div/span[contains(text(),'+')]/text()|"
            "//div/span/font/font[contains(text(),'+')]/text()",
            'TestCons': "//div/span[contains(text(),' - ')]/text()|"
            "//div/span/font/font[contains(text(),' - ')]/text()|"
            u"//div/span[contains(text(),'– ')]/text()"
        }

        review = self.init_item_by_xpaths(response, 'review', review_xpaths)

        date = response.meta['date']

        if date:
            review["TestDateText"] = date

        if review["SourceTestRating"]:
            review["SourceTestScale"] = TEST_SCALE

        if review["TestCons"]:
            review["TestCons"] = review["TestCons"].replace('-', ''
                                                            ).replace(u'–', '')

        if review["TestPros"]:
            review["TestPros"] = review["TestPros"].replace('+', '')

        review["ProductName"] = self.get_product_name(response)

        review['DBaseCategoryName'] = 'PRO'

        yield review
