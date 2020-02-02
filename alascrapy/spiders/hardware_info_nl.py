# -*- coding: utf8 -*-
from datetime import datetime
import dateparser
import re

from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format
from alascrapy.items import CategoryItem, ProductItem, ReviewItem, ProductIdItem

import alascrapy.lib.dao.incremental_scraping as incremental_utils
import alascrapy.lib.extruct_helper as extruct_helper


class HardwareInfo_nlSpider(AlaSpider):
    name = 'hardware_info_nl'
    allowed_domains = ['nl.hardware.info']
    start_urls = ['https://nl.hardware.info/reviews']

    custom_settings = {'COOKIES_ENABLED': True}

    def __init__(self, *args, **kwargs):
        super(HardwareInfo_nlSpider, self).__init__(self, *args, **kwargs)
        #self.stored_last_date = incremental_utils.get_latest_pro_review_date(
        #    self.mysql_manager, self.spider_conf["source_id"])
        self.stored_last_date = datetime(2013, 1, 1)
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):
        original_url = response.url
        print response.text

        latest_date_xpath = "(//p[@class='tagline'])[1]//text()"
        latest_review_date = ''
        latest_date_text = self.extract(response.xpath(latest_date_xpath))
        if latest_date_text:
            latest_review_date = dateparser.parse(latest_date_text)

        if (not latest_review_date) or (latest_review_date < self.stored_last_date):
            return

        urls_xpath = "//div[@class='image']//a[1]/@href"
        next_page_xpath = "(//*[@rel='next'])[1]/@href"

        urls = self.extract_list(response.xpath(urls_xpath))
        for single_url in urls:
            url = get_full_url(original_url, single_url)
            request = Request(url, callback=self.parse_review)
            yield request

        next_page_url = self.extract(response.xpath(next_page_xpath))
        if next_page_url:
            next_page_request = Request(next_page_url, callback=self.parse, meta=response.meta)
            yield next_page_request

    def parse_review(self, response):
        category_path_xpath = "(//div[@class='popular_groups']//li/a)[1]/text()"
        category = CategoryItem()
        category['category_path'] = self.extract(response.xpath(category_path_xpath))

        if self.should_skip_category(category):
            return

        yield category

        microdata_items = extruct_helper.get_microdata_extruct_items(response.text)
        if not microdata_items:
            return

        source_internal_id_re = r'/review/[^/]+/'
        source_internal_id = ''
        match = re.search(source_internal_id_re, response.url)
        if match:
            source_internal_id = match.group(1)

        product = ProductItem.from_response(response, category,
                                            source_internal_id=source_internal_id)
        review = list(extruct_helper.get_reviews_microdata_extruct(microdata_items, product, review_type='PRO'))

        if len(review) > 1:
            self.logger.error('Found more than 1 reviews in {0} through microdata'.format(response.url))
            return

        review = review[0]
        print product
        print review

        return

        product_xpaths = {
            "ProductName": "//h1[@itemprop='headline']/text()",
            "PicURL": "//meta[@property='og:image']/@content",
        }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['TestUrl'] = response.url
        picurl = product.get("PicURL", "")
        if picurl and picurl[:2] == "//":
            product["PicURL"] = "https:" + product["PicURL"]
        if picurl and picurl[:1] == "/":
            product["PicURL"] = get_full_url(response.url, picurl)

        product['OriginalCategoryName'] = category['category_path']

        review_xpaths = {
            "TestTitle": "//*[@property='og:title']/@content",
            "TestPros": "//div[div[text()='The good'] or span[text()='The good']]//li/text()",
            "TestCons": "//div[div[text()='The bad'] or span[text()='The bad']]//li/text()",
            "TestSummary": "//h3[.//text() = 'Bottom Line' or .//text() = 'Bottom line' or .//text = 'Verdict']/"
                           "following-sibling::*[ .//text()[normalize-space()] ][1]//text()",
            "TestVerdict": "//div[div[text()='Verdict'] or span[text()='Verdict']]//p/text()",
        }
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        review['TestUrl'] = response.url

        review_json_ld = extruct_helper.extract_json_ld(response.text, 'Review')
        if review_json_ld:
            review = extruct_helper.review_item_from_review_json_ld(review_json_ld, review)

        if not review.get('TestDateText'):
            review['TestDateText'] = self.extract(response.xpath("//meta[@itemprop='datePublished']/@content"))

        if review["TestDateText"]:
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(review["TestDateText"], "%Y-%m-%d")

        if review.get('ProductName', ''):
            product['ProductName'] = review['ProductName']
        else:
            title = review["TestTitle"].lower()
            if ":" in title:
                all_title_parts = title.split(":")
                for part in all_title_parts:
                    review["ProductName"] = part.replace("review", "") if 'review' in part else title.replace("review",
                                                                                                              "")
            else:
                review["ProductName"] = title.replace("review", "")
                review["ProductName"] = review["ProductName"].strip("-: ")
                product["ProductName"] = review["ProductName"]

        internal_id_re = r',review-(.*)\.html'
        match = re.search(internal_id_re, response.url)
        if match:
            internal_id = match.group(1)
            product['source_internal_id'] = internal_id
            review['source_internal_id'] = internal_id

            product_id = self.product_id(product, kind='tomsguide_en_internal_id', value=internal_id)
            yield product_id

        alt_summary_xpath = "//div[@class='sbbl-content-text']/p//text()"
        if not review['TestSummary']:
            review['TestSummary'] = self.extract(response.xpath(alt_summary_xpath))

        alt_verdict_xpath = "//div[div[text()='Verdict'] or span[text()='Verdict']]//div/text()"
        if not review['TestVerdict']:
            review['TestVerdict'] = self.extract(response.xpath(alt_verdict_xpath))

        # only get summary from article description if both verdict and summary are empty,
        # or else summary and verdict may end up to be the same
        if not review['TestSummary'] and not review['TestVerdict']:
            review['TestSummary'] = self.extract(response.xpath("//meta[@name='description']/@content"))

        review["DBaseCategoryName"] = "PRO"

        ec_award_xpath = "//section[contains(@class, 'page-content-leftcol')]//div[@class='editor-pick']"
        ec_award = response.xpath(ec_award_xpath)
        if ec_award:
            review['award'] = "Editor's Choice"
            review['AwardPic'] = "http://qa901.office.alatest.se/omt-award-images/tomsguide_en_editor_pick.png"

        yield product
        yield review

    def parse_review_summary_page(self, response):
        pass
