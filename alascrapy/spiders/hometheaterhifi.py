# -*- coding: utf8 -*-
from datetime import datetime

import js2xml

from alascrapy.lib.dao import incremental_scraping as incremental_utils
from alascrapy.spiders.base_spiders import ala_spider as spiders


class HomeTheaterHiFiSpider(spiders.AlaSpider):
    name = 'hometheaterhifi_com'
    allowed_domains = ['hometheaterhifi.com']
    start_urls = ['https://www.hometheaterhifi.com/reviews']

    def __init__(self, *args, **kwargs):
        super(HomeTheaterHiFiSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf['source_id'])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):
        next_page_xpath = '//nav[@id="cb-blog-infinite-load"]/a/@href'
        next_page_link = response.xpath(next_page_xpath).extract()
        if len(next_page_link) > 0:
            print('Next:', next_page_link[0])
            yield response.follow(url=next_page_link[0], callback=self.parse)

        reviews_xpath = '//h2[@class="cb-post-title"]/a/@href'
        review_links = response.xpath(reviews_xpath).extract()
        for link in review_links:
            yield response.follow(url=link, callback=self.parse_review_page)

    def parse_review_page(self, response):
        print('Parsing:', response.url)
        product = self.parse_product(response)
        review = self.parse_review(response)
        yield product
        yield review

    def get_sii_from_js(self, response):
        id_data_xpath = '//script[@type="text/javascript" and ' \
            'contains(text(), "embedVars")]/text()'
        post_id_xpath = '//property[@name="postId"]/string/text()'

        js_text = self.extract_xpath(response, id_data_xpath)
        parsed = js2xml.parse(js_text)
        sii = parsed.xpath(post_id_xpath)

        if sii and len(sii) > 0:
            return sii[0]

        return None

    def parse_product(self, response):
        product_xpaths = {
            'PicURL': '//meta[@property="og:image"]/@content',
            'ProductName': '//h1[@itemprop="headline"]/text()',
            'ProductManufacturer': '//div[@class="review-spec"]'
            '[./h6[contains(text(), "Company")]]/p/a/text()',
            'OriginalCategoryName': '//meta[@property="article:section"]'
            '/@content',
        }
        product = self.init_item_by_xpaths(response, 'product', product_xpaths)

        product['TestUrl'] = response.url
        product['source_id'] = self.spider_conf['source_id']
        product['source_internal_id'] = self.get_sii_from_js(response)
        product['ProductName'] = product['ProductName'].replace('Review', '')
        return product

    def parse_review(self, response):
        review_xpaths = {
            'Author': '//div[@itemprop="author"]/a/span/text()',
            'TestSummary': '//meta[@property="og:description"]/@content',
            'TestTitle': '//h1[@itemprop="headline"]/text()',
            'ProductName': '//h1[@itemprop="headline"]/text()',
            'TestDateText': 'substring-before('
            '//meta[@property="article:published_time"]/@content, "T")',
            'TestPros': '//div[@class="article-conclusion-heading" and '
            'contains(text(), "Likes")]/following-sibling::ul/li/text()',
            'TestVerdict': '//div[@class="article-heading" and '
            'contains(text(), "Conclusions")]/following-sibling::h2/text()',
        }

        review = self.init_item_by_xpaths(response, 'review', review_xpaths)

        review['TestUrl'] = response.url
        review['source_id'] = self.spider_conf['source_id']
        review['DBaseCategoryName'] = 'PRO'  # 'USER'
        review['source_internal_id'] = self.get_sii_from_js(response)
        review['ProductName'] = review['ProductName'].replace('Review', '')

        return review
