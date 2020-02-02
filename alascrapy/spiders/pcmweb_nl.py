# -*- coding: utf8 -*-
from __future__ import division
from datetime import datetime

import dateparser

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.lib import extruct_helper


class Pcmweb_nlSpider(AlaSpider):
    name = 'pcmweb_nl'
    allowed_domains = ['pcmweb.nl']
    start_urls = ['https://pcmweb.nl/artikelen/review/']

    def __init__(self, *args, **kwargs):
        super(Pcmweb_nlSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):
        review_xpath = "//h3[contains(@class,'title')]/a/@href"
        review_urls = self.extract_list(response.xpath(review_xpath))
        for review_url in review_urls:
            review_url = get_full_url(response, review_url)
            yield response.follow(url=review_url,
                                  callback=self.parse_review)

        latest_date_xpath = "((//p[@class='grey'])[1]/text())[3]"

        # get the date of latest review of the page
        latest_date_text = self.extract(response.xpath(latest_date_xpath))\
            .replace('|', '')
        latest_date = dateparser.parse(latest_date_text)
        if latest_date and latest_date < self.stored_last_date:
            return
                
        next_page_xpath = "//a[contains(@class,'paginator__next')]/@href"

        # Go to Next page
        next_page_url = self.extract(response.xpath(next_page_xpath))
        next_page_url = get_full_url(response, next_page_url)
        if next_page_url:
            yield response.follow(url=next_page_url, callback=self.parse)

    def parse_review(self, response):
        category_json_ld = extruct_helper.extract_json_ld(response.body,
                                                          'BreadcrumbList')
        review_xpaths = {
            "SourceTestRating": "(//span[contains(@class,'rating')]/@title)[1]",
            "TestPros": "(//ul[contains(@class,'plusmin-list')])[1]"
                        "//li[contains(@class,'plusmin-item')]//text()",
            "TestCons": "(//ul[contains(@class,'plusmin-list')])[2]"
                        "//li[contains(@class,'plusmin-item')]//text()"
        }
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        review_json_ld = extruct_helper.extract_json_ld \
            (response.body, 'Review')
        if review_json_ld:
            review = extruct_helper.review_item_from_article_json_ld(
                review_json_ld, review)

        # different scale based rating system
        if not review.get('SourceTestRating', ''):
            rating_xpath = "//span[contains(@class, 'starrating')]/span[contains(@class, 'value-title')]/text()"
            rating_str = self.extract(response.xpath(rating_xpath))
            # new rating scale at 100
            rating_ratio = 100/5
            try:
                if rating_str:
                    rating_unified_str = (float(rating_str))/rating_ratio
                    review["SourceTestRating"] = rating_unified_str
            except ValueError, e:
                print(e)
                print('rating_str is: {}').format(rating_str)
        if review["SourceTestRating"]:
            review["SourceTestScale"] = '5'
        review["DBaseCategoryName"] = "PRO"
        internal_id_xpath = "//div[contains(@data-meta,'id')]/@data-meta"
        internal_id_re = r'"([0-9]+)"'
        review["source_internal_id"] = response.xpath(internal_id_xpath)\
            .re_first(internal_id_re)
        # some pages that are missing TestDateText, 
        # due to the different page structure,
        # i.e. https://pcmweb.nl/artikelen/review/test-wat-is-de-beste-4-bay-nas/
        # The descriptions of these type of pages can be found using the first
        # type of xpath.
        # They are older than 2017-1-26.
        # thus here we use a default value greater than 2017-1-26
        DEFAULT_NEW_DATE = '2020-02-02'
        if dateparser.parse(review.get('TestDateText', DEFAULT_NEW_DATE )) > datetime(2017, 1, 26):
            review["TestSummary"] = self.extract(response.xpath
                                ("//meta[@name='description']/@content"))
        else:
            review["TestSummary"] = self.extract(response.xpath
                                ("//h2[contains(@class,'review-header')]"
                                 "/following-sibling::div//text()"))

        remove_words = ['Test: ','review: ','Review: ','review','Review']
        if review.get('TestTitle', ''):
            ProductName = review['TestTitle']
            for remove_word in remove_words:
                ProductName = ProductName.replace(remove_word, '')
            review["ProductName"] = ProductName
        yield review

        product_xpaths = {
            "PicURL": "//meta[@property='og:image']/@content",
            "ProductName" : "//meta[@property='og:title']/@content"
        }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        if review.get('ProductName', ''):
            product["ProductName"] = review['ProductName']
        product["source_internal_id"] = review["source_internal_id"]
        category_lists = category_json_ld.get('itemListElement', [])
        if category_lists:
            # get rid of itemListElement[0], not category usually
            category_lists.pop() 
            # get the item with the largest position number
            leaf_category = max(category_lists,
                                key=lambda cat: cat.get('position', 0))
        category_name = leaf_category.get('name', '')
        if category_name:
            # some reviews got only 'Review' as category. using tags instead
            if category_name == 'Review':
                tags_xpath = "//a[contains(@href, 'tag')]/@title"
                tags = response.xpath(tags_xpath).extract()
                tags = [tag.lower() for tag in tags]
                tags = ' | '.join(tag for tag in tags 
                                  if tag != 'review' and tag != 'test')
                category_name = tags
            category_name = category_name.replace('CES 2017', '')
        product["OriginalCategoryName"] = category_name

        yield product
