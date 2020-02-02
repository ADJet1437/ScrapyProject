# -*- coding: utf8 -*-
import re

from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import CategoryItem, ProductItem, ReviewItem, ProductIdItem

class WintechSpider(AlaSpider):
    name = 'wintech_pt'
    allowed_domains = ['wintech.pt']
    start_urls = ['http://wintech.pt/analises/']

    def parse(self, response):

        product_xpath = "//div[@itemprop='blogPost']"
        product_url_xpath = "./div[@class='page-header']//a/@href"
        product_name_xpath = "./div[@class='page-header']//a/text()"
        review_author_date_xpath = "./div[@class='nomeautor']/text()"
        next_page_xpath = "//ul[@class='pagination-list']//a[@title='Seguinte']/@href"

        review_author_and_date_regex = r'^Escrito\s+por\s+(.*)\s+a\s+(.*)$'
        original_category_and_internal_id_regex = r'wintech\.pt/(?:analises/)?([^/]*)/([0-9]+)'

        original_url = response.url
        product_elements = response.xpath(product_xpath)

        if not product_elements:
            return

        for product_element in product_elements:
            product_id = ProductIdItem()
            product = ProductItem()
            review = ReviewItem()

            product_url = self.extract(product_element.xpath(product_url_xpath))
            product_url = get_full_url(original_url, product_url)

            product_name = self.extract(product_element.xpath(product_name_xpath))
            author_and_date = self.extract(product_element.xpath(review_author_date_xpath))
            if author_and_date:
                matches = re.match(review_author_and_date_regex,
                                                 author_and_date, re.I)
                if matches:
                    review['Author'] = matches.group(1).strip()
                    review['TestDateText'] = matches.group(2).strip()
                    review['TestDateText'] = date_format(review['TestDateText'], '%d %B %Y')

            oc_ii_matches = re.search(original_category_and_internal_id_regex, product_url)
            if not oc_ii_matches:
                continue

            original_category = oc_ii_matches.group(1)
            internal_id = oc_ii_matches.group(2)

            category = CategoryItem()
            category['category_leaf'] = original_category
            category['category_path'] = original_category
            if 'wintech.pt/analises' in product_url and original_category != 'analises':
                category['category_url'] = 'http://wintech.pt/analises/' + original_category
            elif 'wintech.pt/' in product_url:
                category['category_url'] = 'http://wintech.pt/' + original_category

            yield category

            product_id['ProductName'] = product_name
            product_id['source_internal_id'] = internal_id
            product_id['ID_kind'] = 'wintech_pt_internal_id'
            product_id['ID_value'] = internal_id
            yield product_id

            product['ProductName'] = product_name
            product['TestUrl'] = product_url
            product['OriginalCategoryName'] = original_category
            product['source_internal_id'] = internal_id

            self.set_product(review, product)
            review['TestTitle'] = product_name

            request = Request(product_url, callback=self.level_2)
            request.meta['product'] = product
            request.meta['review'] = review
            yield request

        next_page_url = self.extract(response.xpath(next_page_xpath))
        if next_page_url:
            next_page_url = get_full_url(original_url, next_page_url)
            next_page_request = Request(next_page_url, callback=self.parse)
            yield next_page_request

    def level_2(self, response):

        original_url = response.url

        product = response.meta['product']
        review = response.meta['review']

        # TODO: find a way to extract image url
        pic_xpath = "//span[@class='review_image']/img/@src"
        pic_url = self.extract(response.xpath(pic_xpath))
        if not pic_url:
            product['PicURL'] = ''
        else:
            product['PicURL'] = get_full_url(original_url, pic_url)

        # TODO: see if we can download svg award images
        #award_pic_xpath = ""
        rating_xpath = "//input[@id='scoreboard']/@value"
        verdict_xpath = "//div[@class='scoreboard-quote']/text()"

        summary_xpath = u"//h1[contains(., 'Conclusão')]/following::p[1]//text()"
        alt_summary_xpath = u"//h1[contains(., 'Conclusão')]/following::p[2]//text()"
        alt_summary_xpath_2 = u"//h1[contains(., 'Conclusão')]/following-sibling::text()[1]"

        # xpath for verdict of a brief review
        #alt_verdict_xpath = "(//div[@class='csc-textpic-text']/p[@class='bodytext'])[1]/text()"
        # fail-safe approaches
        #alt_verdict_xpath2 = "//div[@class='csc-textpic-text']/blockquote/p[@class='bodytext']/text()"
        #alt_verdict_xpath3 = "//div[@class='csc-textpic-text']/p[@class='bodytext']/i/text()"

        review['SourceTestRating'] = self.extract(response.xpath(rating_xpath))
        review['TestVerdict'] = self.extract(response.xpath(verdict_xpath))
        extracted_summary = self.extract_all(response.xpath(summary_xpath), '', None, keep_whitespace=True).strip()

        #awpic_link = review.get("AwardPic", "")
        #if awpic_link and awpic_link[:2] == "//":
        #    review["AwardPic"] = "https:" + review["AwardPic"]
        #if awpic_link and awpic_link[:1] == "/":
        #    review["AwardPic"] = get_full_url(original_url, awpic_link)

        if not extracted_summary:
            extracted_summary = self.extract_all(response.xpath(alt_summary_xpath), '', None, keep_whitespace=True).strip()
        if not extracted_summary:
            # we only extract 1 'text' node from alt_summary_xpath_2
            extracted_summary = self.extract(response.xpath(alt_summary_xpath_2)).strip()

        review['TestSummary'] = extracted_summary

        #if not review["TestVerdict"]:
        #    review["TestVerdict"] = self.extract(response.xpath(alt_verdict_xpath))
        #if not review["TestVerdict"]:
        #    review["TestVerdict"] = self.extract(response.xpath(alt_verdict_xpath2))
        #if not review["TestVerdict"]:
        #    review["TestVerdict"] = self.extract(response.xpath(alt_verdict_xpath3))

        review["SourceTestScale"] = "10"
        review["DBaseCategoryName"] = "PRO"

        yield product
        yield review
