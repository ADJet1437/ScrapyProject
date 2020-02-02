# -*- coding: utf8 -*-
import re

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import date_format

MAX_SENTENCES = 2


class Avguide_chSpider(AlaSpider):
    name = 'avguide_ch'
    allowed_domains = ['avguide.ch']
    start_urls = ['https://www.avguide.ch/testberichte']
    main_url = 'https://www.avguide.ch/testberichte'
    GOT_LAST_PAGE_NUM = False
    next_page = 2
    last_page = 0
    page_pattern = '[0-9]+$'

    def parse(self, response):
        review_urls_xpath = "//div[@class='teaserlistbox']/h3/span/a/@href"
        review_urls = self.extract_list(response.xpath(review_urls_xpath))
        last_page_xpath = "//div[contains(@class, 'pagingcarousel')]"\
            "/div[last()-1]//text()"

        for review_url in review_urls:
            yield response.follow(review_url,
                                  callback=self.level_2)

        if not self.GOT_LAST_PAGE_NUM:
            last_page = self.extract(response.xpath(last_page_xpath))
            match = re.findall(self.page_pattern, last_page)
            if match:
                last_page = match[0]
            if last_page:
                self.last_page = last_page
                self.last_page = int(self.last_page)
                self.GOT_LAST_PAGE_NUM = True

        if self.next_page and self.last_page \
                and self.next_page <= self.last_page:

            next_page_url = self.main_url + '/?page=' + str(self.next_page)
            self.next_page += 1
            yield response.follow(next_page_url,
                                  callback=self.parse)
        else:
            return

    def get_product_name(self, response):
        name_xpath = self.extract(response.xpath("//head/title/text()"))
        name = name_xpath.split(' - ')[0]
        productname = name.replace('Test', '').replace(':', '')

        return productname.strip()

    def get_source_internal_id(self, response):
        name_xpath = self.extract(
            response.xpath("substring-after(//script["
                           "@type='text/javascript']/text(),'print/')"))
        name = name_xpath.split('"')[0]
        return name

    def level_2(self, response):

        product_xpaths = {
            "PicURL": '//meta[@property="og:image"]/@content'
        }

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['ProductName'] = self.get_product_name(response)
        product['source_internal_id'] = self.get_source_internal_id(response)

        original_category_name_xpath = "(//img[@alt='Themen']/ancestor::div/"\
            "following-sibling::div)[1]/a/text()"
        original_category_name = self.extract_all(
            response.xpath(original_category_name_xpath), " | ")
        if original_category_name:
            product["OriginalCategoryName"] = original_category_name

        review_xpaths = {
            'source_internal_id': "substring-after(//script["
            "@type='text/javascript']/text(),'print/')",
            "TestDateText": "//div[@class='articlebox-content']/div[5]/text()",
            "TestSummary": '//meta[@property="og:description"]/@content',
            "Author": "//meta[@itemprop='creator accountablePerson']/@content",
            "TestTitle": '//meta[@property="og:title"]/@content',
            "TestDateText": "(//img[@alt='Publikationsdatum']/ancestor::div"
            "/following-sibling::div)[1]/text()"
        }
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        review['ProductName'] = self.get_product_name(response)
        review['source_internal_id'] = self.get_source_internal_id(response)
        yield product

        test_date = review["TestDateText"]

        if test_date:
            test_date = test_date.strip()
            review["TestDateText"] = date_format(
                test_date, "%d. %B %Y", ["de"])

        review["DBaseCategoryName"] = "PRO"

        verdict_url_xpath = "//div[@class='kapitel '][last()]/a/@href"
        verdict_page = self.extract(response.xpath(verdict_url_xpath))
        if verdict_page:
            yield response.follow(
                verdict_page,
                callback=self.get_test_verdict,
                meta={'review': review}
            )

        else:
            self.extract_test_verdict(response, review)
            yield review

    def extract_test_verdict(self, response, review):
        pros_xpath = "//div[contains (text(),'Pro:')][1]/"\
            "following-sibling::div[1]/text()"
        test_pros = self.extract(response.xpath(pros_xpath))
        review['TestPros'] = test_pros

        cons_xpath = "//div[contains (text(),'Contra:')][1]/"\
            "following-sibling::div[1]/text()"
        test_cons = self.extract(response.xpath(cons_xpath))
        review['TestCons'] = test_cons

        test_verdict_xpath = "//h1[contains(text(),'Fazit')]"\
            "/following-sibling::text()|//b[contains(text(),'Fazit')]"\
            "/following-sibling::text()|//h1[contains(text(),'Fazit')]"\
            "/following-sibling::p[1]/text()"

        test_verdict = self.extract(response.xpath(test_verdict_xpath))

        if len(test_verdict) > 100:
            test_verdict = '.'.join(
                test_verdict.split('.')[0:MAX_SENTENCES]) + '.'
            review["TestVerdict"] = test_verdict

    def get_test_verdict(self, response):
        review = response.meta['review']
        self.extract_test_verdict(response, review)
        yield review
