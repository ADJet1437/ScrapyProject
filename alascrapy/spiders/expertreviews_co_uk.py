# -*- coding: utf8 -*-

from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format
from alascrapy.items import CategoryItem, ProductIdItem

import alascrapy.lib.extruct_helper as extruct_helper
import alascrapy.lib.dao.incremental_scraping as incremental_utils

import dateparser
import re
from datetime import datetime


class ExpertreviewsCoUkSpider(AlaSpider):
    name = 'expertreviews_co_uk'
    allowed_domains = ['expertreviews.co.uk']
    start_urls = ['http://www.expertreviews.co.uk']

    def __init__(self, *args, **kwargs):
        super(ExpertreviewsCoUkSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf['source_id'])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):
        all_categories_xpath = '//div[@id="block-system-main-menu"]'\
            '//li[@class="leaf" or @class="last leaf"]/a/@href'
        all_cats = response.xpath(all_categories_xpath)
        all_categories_urls = self.extract_list(all_cats)
        for category_url in all_categories_urls:
            category_url = get_full_url(response, category_url)
            request = Request(category_url, callback=self.parse_category)
            yield request

    def parse_category(self, response):
        latest_review_date_xpath = '//div[contains(@class, '\
            '"field-name-field-published-date")]//text()'
        next_page_xpath = '//a[@title="Go to next page"]/@href'
        review_url_xpath = '//div[@id="content"]//p[@class="title"]'\
                           '/span/a/@href'

        review_urls = self.extract_list(response.xpath(review_url_xpath))
        for review_url in review_urls:
            review_url = get_full_url(response, review_url)
            request = Request(review_url, callback=self.parse_review)
            yield request

        # incremental scraping
        latest_review_date_text = self.extract_xpath(response,
                                                     latest_review_date_xpath)
        latest_review_date = dateparser.parse(latest_review_date_text)
        if latest_review_date and latest_review_date < self.stored_last_date:
            return

        next_page = self.extract(response.xpath(next_page_xpath))
        if next_page:
            next_page = get_full_url(response, next_page)
            request = Request(next_page, callback=self.parse_category)
            yield request

    def parse_review(self, response):
        product_xpaths = {
            'PicURL': '//meta[@property="og:image"]/@content',
            'OriginalCategoryName': '//div[@class="dennis-kicker"]/a/text()'
        }

        review_xpaths = {
            'TestSummary': '//meta[@property="og:description"]/@content',

            'TestPros': '//div[contains(@class, "field-name-field-pros")]'
            '/div[@class="field-items"]//text()',

            'TestCons': '//div[contains(@class, "field-name-field-cons")]'
            '/div[@class="field-items"]//text()',

            'TestDateText': '//span[@class="date-display-single"]/text()',

            'Author': '//span[@class="field field-name-field-author '
            'field-type-node-reference field-label-hidden"]/'
            'span[@class="field-item even"]/text() | //div[@class="field '
            'field-name-author-names-combined field-type-text '
            'field-label-hidden"]/div[@class="field-items"]/div'
            '[@class="field-item even"]/a'
        }

        product_name = ''
        product = self.init_item_by_xpaths(response, 'product', product_xpaths)
        review = self.init_item_by_xpaths(response, 'review', review_xpaths)

        title_xpath = '//meta[@property="og:title"]/@content'
        title = self.extract(response.xpath(title_xpath))

        review_json_ld = extruct_helper.extract_json_ld(
            response.text, 'Review')
        if review_json_ld:
            review = extruct_helper.review_item_from_review_json_ld(
                review_json_ld, review)
            product_name = review_json_ld.get(
                'itemReviewed', {}).get('name', '')
            product_name = product_name.split('review')[0].strip()

        # get review date and do incremental scraping
        if review.get('TestDateText', ''):
            review['TestDateText'] = date_format(review['TestDateText'], '')

        if not product_name:
            # title_xpath = '//meta[@property="og:title"]/@content'
            # title = self.extract(response.xpath(title_xpath))
            product_name = title.split('review')[0].strip()

        product['ProductName'] = product_name
        review['ProductName'] = product['ProductName']
        review['TestTitle'] = title
        # product['TestTitle'] = title

        category_url_xpath = '//div[contains(@class, '\
            '"field-category-primary")]//a/@href'

        if product.get('OriginalCategoryName', ''):
            category = CategoryItem()
            category['category_leaf'] = product['OriginalCategoryName']
            category['category_path'] = product['OriginalCategoryName']
            category['category_url'] = get_full_url(
                response, self.extract(response.xpath(category_url_xpath)))
            yield category

        # award_xpath = '//div[contains(@class, "group-media")]//div[contains
        # (@class, "field-name-field-award-image")]//img/@src'
        # award = response.xpath(award_xpath)
        # if award:
        #     award_re = r'(.*)\s+Logo'
        #     award_name = award.xpath('./@title').re_first(award_re)
        #     award_image_url = self.extract_xpath(award, './@src')
        #     if award_name and award_image_url:
        #         review['award'] = award_name
        #         review['AwardPic'] = award_image_url

        internal_id = ''
        internal_id_url_xpath = '//meta[@property="og:url"]/@content'
        internal_id_re = r'go/([0-9]+)'

        internal_id_url = self.extract_xpath(response, internal_id_url_xpath)
        if internal_id_url:
            internal_id_match = re.search(internal_id_re, internal_id_url)
            if internal_id_match:
                internal_id = internal_id_match.group(1)
            else:
                internal_id = internal_id_url.split('/')[-2]

        if not internal_id or not internal_id.isdigit():
            internal_id = response.url.split('/')[-2]

        if internal_id and internal_id.isdigit():
            product_id = ProductIdItem()
            product_id['ProductName'] = product['ProductName']
            product_id['source_internal_id'] = internal_id
            product_id['ID_kind'] = 'expertreviews_internal_id'
            product_id['ID_value'] = internal_id
            yield product_id

        product['source_internal_id'] = internal_id
        yield product

        review['DBaseCategoryName'] = 'PRO'
        review['SourceTestScale'] = '5'
        review['source_internal_id'] = product['source_internal_id']

        verdict_page_xpath = '//section[@class="pagination mn_background"]'\
            '//li[last()]/a/@href'
        verdict_page_url = self.extract(response.xpath(verdict_page_xpath))
        if verdict_page_url:
            verdict_page_url = get_full_url(response, verdict_page_url)
            request = Request(verdict_page_url, callback=self.get_test_verdict)
            request.meta['review'] = review
            yield request
        else:
            test_verdict_xpath = '(//div[contains(@class, "field-name-body")]'\
                '//p[ not(strong) and .//text()[normalize-space()]and'\
                ' .//text()[not(starts-with(., "Buy"))]and '\
                './/text()[not(starts-with(., "BUY"))] ])[last()]//text()'
            review["TestVerdict"] = self.extract_all(response.xpath(
                test_verdict_xpath), separator='', keep_whitespace=True)
            yield review

    def get_test_verdict(self, response):
        test_verdict_xpath = '(//div[contains(@class, "field-name-body")]'\
            '//p[ not(strong) and .//text()[normalize-space()] and '\
            './/text()[not(starts-with(., "Buy"))] and .//text()'\
            '[not(starts-with(., "Buy"))] ])[last()]//text()'
        review = response.meta['review']
        review['TestVerdict'] = self.extract_all(response.xpath(
            test_verdict_xpath), separator='', keep_whitespace=True)
        yield review
