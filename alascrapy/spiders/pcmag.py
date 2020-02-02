# -*- coding: utf8 -*-
from datetime import datetime

from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format
from alascrapy.items import CategoryItem, ProductItem

import alascrapy.lib.extruct_helper as extruct_helper
import alascrapy.lib.dao.incremental_scraping as incremental_utils

import dateparser
import json

class PcmagSpider(AlaSpider):
    name = 'pcmag'
    allowed_domains = ['pcmag.com']
    start_url = 'http://www.pcmag.com/filter.aspx/seemore?Page={}&ExcludeArticleIds=296955,256052,342537&RiverType=Single%20Article%20River&SectionId=27961&ArticleTypeIds=12,6'

    review_url_suffix = '?setccpref=US'
    start_page = 1

    def __init__(self, *args, **kwargs):
        super(PcmagSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def start_requests(self):
        first_page_url = self.start_url.format(self.start_page)
        request = Request(first_page_url, callback=self.parse)
        request.meta['current_page'] = self.start_page
        yield request

    def parse(self, response):
        json_response = json.loads(response.text)
        has_more_articles = json_response.get('HasMoreArticles', False)
        if not has_more_articles:
            return

        reviews = json_response.get('Links', [])
        if not reviews:
            return

        for review in reviews:
            product = ProductItem()
            product['PicURL'] = review.get('ImageUrl', '')

            try:
                # fail-safe incremental scraping
                review_date_text = review.get('ArticleDate', '1/1/1970')
                review_date = dateparser.parse(review_date_text)
                if review_date < self.stored_last_date:
                    return
            except:
                pass

            review_url = review.get('Url', '')
            if review_url:
                review_url += self.review_url_suffix
                request = Request(review_url, callback=self.parse_review)
                request.meta['product'] = product
                yield request

        curr_page = response.meta['current_page']
        next_page = curr_page + 1
        next_page_url = self.start_url.format(next_page)
        next_page_request = Request(next_page_url, callback=self.parse)
        next_page_request.meta['current_page'] = next_page
        yield next_page_request

    def parse_review(self, response):
        review_xpaths = { "TestTitle": "//*[@property='og:title']/@content",
                          "TestSummary": "//*[@property='og:description']/@content",
                          "TestVerdict": "//section[@class='review-body']//*[contains(text(),'Conclusion')]/ancestor::p//text()",
                          "TestPros":"//div[@class='pros-cons-bl']//*[contains(text(),'Pros')]//parent::li//p[@class='summary']//text()", 
                          "TestCons":"//div[@class='pros-cons-bl']//*[contains(text(),'Cons')]//parent::li//p[@class='summary']//text()",
                        }

        product_name_xpath = "//h1[contains(@class,'item')]/text()"
        internal_id_xpath = "//meta[@name='article-id']/@content"
        award_xpath = "//div[@class='editors-logo']/img/@src"

        product = response.meta['product']
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        # get category
        category = CategoryItem()
        breadcrumbs_json_ld = extruct_helper.extract_json_ld(response.text, 'BreadcrumbList')
        if breadcrumbs_json_ld:
            category = extruct_helper.leaf_category_item_from_breadcrumbs_json_ld(breadcrumbs_json_ld, category)
            yield category
            if self.should_skip_category(category):
                return

            category_name = category['category_path']
            product["OriginalCategoryName"] = category_name

        product['TestUrl'] = response.url
        review['TestUrl'] = product['TestUrl']

        review_json_ld = extruct_helper.extract_json_ld(response.text, 'Review')
        if review_json_ld:
            review = extruct_helper.review_item_from_review_json_ld(review_json_ld, _review=review)
            product['ProductName'] = review['ProductName']
        else:
            product['ProductName'] = self.extract(response.xpath(product_name_xpath))
            review['ProductName'] = product['ProductName']

        if review.get("TestDateText", ''):
            review["TestDateText"] = date_format(review["TestDateText"],
                                                 "%Y-%m-%dT%H:%M:%S")

        alt_verdict_xpath = "string(//section[@class='review-body']//*[contains(text(),'Conclusion')]/following::p[ string-length(.//text()) > 0 ][1])"
        alt_verdict_xpath2 = "string(//div[contains(@class, 'article-footer')]/preceding::p[ string-length(.//text()) > 0 ][1])"
        if not review['TestVerdict']:
            review['TestVerdict'] = self.extract_all(response.xpath(alt_verdict_xpath))
        if not review['TestVerdict']:
            review['TestVerdict'] = self.extract_all(response.xpath(alt_verdict_xpath2))

        internal_id = self.extract(response.xpath(internal_id_xpath))
        if internal_id:
            product['source_internal_id'] = internal_id
            review['source_internal_id'] = internal_id
            product_id_item = self.product_id(product, kind='pcmag_internal_id', value=internal_id)
            yield product_id_item

        ec_award_url = self.extract(response.xpath(award_xpath))
        if ec_award_url:
            review['AwardPic'] = get_full_url(response, ec_award_url)
            review['award'] = "Editor's Choice"

        review["DBaseCategoryName"] = "PRO"
        review["SourceTestScale"] = "5"

        yield product
        yield review
