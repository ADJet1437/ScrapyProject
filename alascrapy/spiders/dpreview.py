# -*- coding: utf8 -*-
import re

from scrapy.http import Request
from urllib import unquote

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format


class DpreviewSpider(AlaSpider):
    name = 'dpreview'
    allowed_domains = ['dpreview.com']
    start_urls = ['http://www.dpreview.com/reviews?category=cameras']

    def parse(self, response):

        original_url = response.url
        urls_xpath = "//div[@class='name']/a/@href"
        urls = self.extract_list(response.xpath(urls_xpath))
        for single_url in urls:
            single_url = get_full_url(original_url, single_url)
            request = Request(single_url, callback=self.level_2)
            yield request

        urls_xpath = "//ul[@class='otherReviews']/li/a/@href"
        urls = self.extract_list(response.xpath(urls_xpath))
        for single_url in urls:
            single_url = get_full_url(original_url, single_url)
            request = Request(single_url, callback=self.level_2)
            yield request

    def level_2(self, response):
        original_url = response.url
        product_xpaths = {
            "OriginalCategoryName": "//a[@class='mainItem']//span[contains(text(), 'Cameras')]/text()",
            "PicURL": "//meta[@property='og:image']/@content",
        }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        if not product['PicURL']:
            product['PicURL'] = self.extract(response.xpath("(//tbody/tr/td[@class='image']/a/img/@src)"))

        review_xpaths = {
            "TestDateText": "//div[@class='metadata']//span[@class='date' and contains(text(), 'Published')]/text()",
            "TestSummary": "//meta[@property='og:description']/@content",
            "Author": "//div[@class='metadata']/span[@class='authors']//text()",
            "TestTitle": "//div[@class='mainContent']//h1//text()",
        }
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        product_name = self.extract(response.xpath("//tr[@class='productName']/td/div[@class='name']/a/text()"))
        review["ProductName"] = product_name
        product["ProductName"] = product_name
        
        if not product_name:
            if review and review['TestTitle']:
                title = review["TestTitle"].lower()
                if ":" in title:
                    all_title_parts = title.split(":")
                    for part in all_title_parts:
                        productname = part.replace(
                            "review", "") if 'review' in part else title.replace("review", "")
                else:
                    productname = title.replace("review", "")
                
                productname = productname.strip("-: ")            
                review["ProductName"] = productname
                product["ProductName"] = productname

        test_url = response.url
        internal_source_id = unquote(test_url).split('/')[-1]
        review['source_internal_id'] = internal_source_id
        product['source_internal_id'] = internal_source_id

        review["DBaseCategoryName"] = "PRO"

        if review["TestDateText"]:
            review["TestDateText"] = review["TestDateText"].lower().replace(
                'Published'.lower(), "")
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(
                review["TestDateText"], "%d %B %Y", ["en"])

        in_another_page_xpath = "//div[@class='articleTableOfContents']//a[contains(text(), 'Conclusion') or contains(text(), 'Impressions')]/@href"
        pros_xpath = "//ul[@type='square'][1]/li//text()"
        cons_xpath = "//ul[@type='square'][2]/li//text()"
        award_xpath = ""
        award_pic_xpath = "//p[@align='center']/img/@src"

        test_verdict_xpath_1 = '//h2[contains(text(), "conclusion") or contains(text(), "Conclusion")]//following-sibling::p[1]//text()'
        test_verdict_xpath_2 = '//h2[contains(text(), "conclusion") or contains(text(), "Conclusion")]//following-sibling::p[2]//text()'
        test_verdict_xpath_3 = '//*[contains(text(), "First Impressions")]//following-sibling::p[1]//text()'
        test_verdict_xpath_4 = '//*[contains(text(), "First Impressions")]//following-sibling::p[2]//text()'

        review["TestVerdict"] = None
        in_another_page_url = None
        if in_another_page_xpath:
            in_another_page_url = self.extract(
                response.xpath(in_another_page_xpath))
        if in_another_page_url:
            in_another_page_url = get_full_url(response, in_another_page_url)
            request = Request(in_another_page_url,
                              callback=self.parse_fields_page)
            request.meta['review'] = review

            request.meta['test_verdict_xpath_1'] = test_verdict_xpath_1
            request.meta['test_verdict_xpath_2'] = test_verdict_xpath_2
            request.meta['test_verdict_xpath_3'] = test_verdict_xpath_3
            request.meta['test_verdict_xpath_4'] = test_verdict_xpath_4

            request.meta['pros_xpath'] = pros_xpath
            request.meta['cons_xpath'] = cons_xpath
            request.meta['award_xpath'] = award_xpath
            request.meta['award_pic_xpath'] = award_pic_xpath
            yield request
        else:
            if not review["TestVerdict"]:
                review["TestVerdict"] = self.extract(
                    response.xpath(test_verdict_xpath_1))

            if not review["TestVerdict"]:
                review["TestVerdict"] = self.extract(
                    response.xpath(test_verdict_xpath_2))

            if not review["TestVerdict"]:
                review["TestVerdict"] = self.extract(
                    response.xpath(test_verdict_xpath_3))

            if not review["TestVerdict"]:
                review["TestVerdict"] = self.extract(
                    response.xpath(test_verdict_xpath_4))

        yield product

        yield review

    def parse_fields_page(self, response):
        review = response.meta['review']

        test_verdict_xpath_1 = response.meta['test_verdict_xpath_1']
        test_verdict_xpath_2 = response.meta['test_verdict_xpath_2']
        test_verdict_xpath_3 = response.meta['test_verdict_xpath_3']
        test_verdict_xpath_4 = response.meta['test_verdict_xpath_4']

        if not review["TestVerdict"]:
            review["TestVerdict"] = self.extract(
                response.xpath(test_verdict_xpath_1))

        if not review["TestVerdict"]:
            review["TestVerdict"] = self.extract(
                response.xpath(test_verdict_xpath_2))

        if not review["TestVerdict"]:
            review["TestVerdict"] = self.extract(
                response.xpath(test_verdict_xpath_3))

        if not review["TestVerdict"]:
            review["TestVerdict"] = self.extract(
                response.xpath(test_verdict_xpath_4))

        pros_xpath = response.meta['pros_xpath']
        cons_xpath = response.meta['cons_xpath']
        award_xpath = response.meta['award_xpath']
        award_pic_xpath = response.meta['award_pic_xpath']
        if pros_xpath:
            review["TestPros"] = self.extract_all(response.xpath(pros_xpath))
        if cons_xpath:
            review["TestCons"] = self.extract_all(response.xpath(cons_xpath))
        if award_xpath:
            review['award'] = self.extract(response.xpath(award_xpath))
        if award_pic_xpath:
            review['AwardPic'] = self.extract(response.xpath(award_pic_xpath))
        yield review
