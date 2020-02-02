# -*- coding: utf-8 -*-

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.lib.generic import date_format
from datetime import datetime


class Play3r_netSpider(AlaSpider):
    name = 'play3r_net'
    allowed_domains = ['play3r.net']
    start_urls = ['https://www.play3r.net/reviews/']

    def __init__(self, *args, **kwargs):
        super(Play3r_netSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

    def parse(self, response):
        urls_xpath = '//h3/a/@href'
        urls = self.extract_list(response.xpath(urls_xpath))

        for url in urls:
            yield response.follow(url, callback=self.parse_review)

        # next page
        next_page_xpath = '//div[@class="page-nav td-pb-padding-side"]'\
                          '/a[last()]/@href'
        next_page = self.extract(response.xpath(next_page_xpath))

        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_review(self, response):
        product_xpaths = {
            'OriginalCategoryName': '//div[@class="entry-crumbs"]/'
                                    'span[last()-1]/a/text()',

            'PicURL': '//meta[@property="og:image"]/@content',
            'source_internal_id': 'substring-after(//article/@id, "-")',
            'TestUrl': '//meta[@property="og:url"]/@content',

        }

        review_xpaths = {
            'TestDateText': 'substring-before(//time/@datetime, "T")',

            'TestPros': '//p[contains(., "Pros")]/following-sibling::p[1]'
                        '/text()',

            'TestCons': '//p[contains(., "Cons")]/following-sibling::p[1]'
                        '/text()',

            'TestSummary': '//meta[@property="og:description"]/@content',

            'TestVerdict': '//div[@class="td-review-summary-content"]/text()|'
                           '//h3[last()]/following-sibling::p[1]/text()',

            'Author': '//div[@class="td-post-author-name"]/a/text()',
            'TestTitle': '//meta[@property="og:title"]/@content',
            'source_internal_id': 'substring-after(//article/@id, "-")',
            'TestUrl': '//meta[@property="og:url"]/@content',
            'TestDateText': 'substring-before(//time/@datetime, "T")',
        }

        product = self.init_item_by_xpaths(response, 'product', product_xpaths)
        review = self.init_item_by_xpaths(response, 'review', review_xpaths)

        product_name_xpath = '//h1[@class="entry-title"]/text()'
        p_name = self.extract(response.xpath(product_name_xpath))
        product_name = ''

        if 'Review' in p_name:
            product_name = p_name.split(' Review')[0]

        else:
            product_name = p_name

        product['ProductName'] = product_name
        review['ProductName'] = product_name

        rating_xpath = '//div[@class="td-review-final-score"]/text()'
        rating = self.extract(response.xpath(rating_xpath))
        SCALE = 5

        if rating:
            review['SourceTestRating'] = rating
            review['SourceTestScale'] = SCALE

        review['DBaseCategoryName'] = 'PRO'

        test_day = review['TestDateText']
        date_str = date_format(test_day, '%Y-%m-%d')
        date_time = datetime.strptime(date_str, '%Y-%m-%d')
        if date_time < self.stored_last_date:
            return

        yield product
        yield review
