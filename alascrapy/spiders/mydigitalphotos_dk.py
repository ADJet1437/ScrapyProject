# -*- coding: utf8 -*-
import dateparser
import re

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider

TEST_SCALE = 100
MAX_SENTENCES = 2


class myDigitalPhotosSpider(AlaSpider):
    name = 'mydigitalphotos_dk'
    allowed_domains = ['mydigitalphotos.dk']
    start_urls = ['http://www.mydigitalphotos.dk/anmeldelser/']

    def parse(self, response):
        review_urls_xpath = "//div[@class='entry']/ul/li/a/@href"
        review_urls = self.extract_list(response.xpath(review_urls_xpath))

        for review_url in review_urls:
            yield response.follow(review_url,
                                  callback=self.parse_review_product)

    def parse_review_product(self, response):
        product_xpaths = {
            'PicURL': '(//div[@class="entry"]/p/a/img)[1]/@src',
            'ProductName': '//span[@itemprop="name"]/text()'
        }
        product = self.init_item_by_xpaths(response, 'product', product_xpaths)

        ocn_xpath = "//a[@rel='category tag']/text()"
        original_category_name = self.extract_all(
            response.xpath(ocn_xpath), " | ")
        product["OriginalCategoryName"] = original_category_name

        product['TestUrl'] = response.url
        source_int_id = self.extract(response.xpath("//body/@class"))
        source_internal_id = re.findall(r'postid-(\d+)', source_int_id)

        product["source_internal_id"] = source_internal_id[0]
        product['ProductName'] = product['ProductName'].replace(
            'Anmeldelse:', '').replace('Test:', '').strip()
        yield product

        review_xpaths = {
            'Author': '//span[@class="post-meta-author"]/a/text()',
            'TestSummary': '//meta[@name="description"]/@content',
            'TestTitle': '//span[@itemprop="name"]/text()',
            'ProductName': '//span[@itemprop="name"]/text()'
        }

        review = self.init_item_by_xpaths(response, 'review', review_xpaths)

        test_date_xpath = "(//span[@class='tie-date'])[1]/text()"
        test_date = self.extract(response.xpath(test_date_xpath))
        test_date_text = dateparser.parse(test_date)
        if test_date_text:
            review["TestDateText"] = test_date_text.date()

        review['TestUrl'] = response.url

        source_rating_xpath = '//strong[contains(text(), "Karakter")]'\
            '/ancestor::p/text()'
        source_rating = self.extract(response.xpath(source_rating_xpath))
        review['SourceTestRating'] = source_rating.strip('% ')
        if review["SourceTestRating"]:
            review["SourceTestScale"] = TEST_SCALE

        review['DBaseCategoryName'] = 'PRO'
        review['source_internal_id'] = product["source_internal_id"]
        review['ProductName'] = product['ProductName']

        test_pros_xpath = "//p[starts-with(text(), '+')]/text()"
        test_pros = self.extract_all(
            response.xpath(test_pros_xpath), " | ")
        review["TestPros"] = test_pros.strip('+| ')

        test_cons_xpath = u"//p[starts-with(text(), '–')]/text()"
        test_cons = self.extract_all(
            response.xpath(test_cons_xpath), " | ")
        review["TestCons"] = test_cons.strip(u'–| ')

        verdict_xpath = "//strong[contains(text(),'Konklusion')]/"\
            "ancestor::p/text() | //h2[contains(text(),'Konklusion')]/"\
            "following-sibling::p[1]/text() | //h1[contains(text(),"\
            "'Konklusion')]/following-sibling::p[1]/text()"
        test_verdict = self.extract(response.xpath(verdict_xpath))

        if len(test_verdict) > 100:
            test_verdict = '.'.join(
                test_verdict.split('.')[0:MAX_SENTENCES]) + '.'
            review["TestVerdict"] = test_verdict

        yield review
