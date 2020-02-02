# -*- coding: utf8 -*-
from datetime import datetime

from alascrapy.lib.dao import incremental_scraping as incremental_utils
from alascrapy.spiders.base_spiders import ala_spider as spiders


class MonWindowsComSpider(spiders.AlaSpider):
    name = 'monwindows_com'
    allowed_domains = ['monwindows.com']
    start_urls = ['https://www.monwindows.com/tag/test/']

    def __init__(self, *args, **kwargs):
        super(MonWindowsComSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf['source_id'])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):
        next_page_xpath = '//a[@title="Page suivante"]/@href'
        next_page_link = response.xpath(next_page_xpath).extract()
        if len(next_page_link) > 0:
            yield response.follow(url=next_page_link[0], callback=self.parse)

        reviews_xpath = '//article/div[1]/a/@href'
        review_links = response.xpath(reviews_xpath).extract()
        for link in review_links:
            yield response.follow(url=link, callback=self.parse_review_page)

    def parse_review_page(self, response):
        product = self.parse_product(response)
        review = self.parse_review(response)
        yield product
        yield review

    def get_product_name(self, response):
        product_name_xpath = '//meta[@property="og:title"]/@content'
        product_name = response.xpath(product_name_xpath).extract()

        if len(product_name) == 0:
            return ''

        # Example: J'ai testé le Samsung 960 EVO : mon retour...
        product_name = product_name[0]
        product_name = product_name.split(':')[0]  # gets string before ':'
        product_name = product_name.split(',')[0]  # gets string before ','
        # Removes common text in the titles
        product_name = product_name.replace(
            u'J\'ai testé', '').replace(u'Test du', '').replace(u'[Test]', '')

        return product_name.strip()

    def parse_product(self, response):
        product_xpaths = {
            'PicURL': '//meta[@property="og:image"]/@content',
            'source_internal_id': '//input[@name="page_id"]/@value',

            'OriginalCategoryName': '//div[@class="blog-category"]'
            '//li/a/text()',
        }
        product = self.init_item_by_xpaths(response, 'product', product_xpaths)

        product['TestUrl'] = response.url
        product['ProductName'] = self.get_product_name(response)
        product['source_id'] = self.spider_conf['source_id']

        return product

    def parse_review(self, response):
        review_xpaths = {
            'Author': '//*[@itemprop="author"]/*[@itemprop="name"]//text()',
            'source_internal_id': '//input[@name="page_id"]/@value',
            'TestSummary': '//div[@class="blog-post-body"]//p[1]//text()',
            'TestTitle': '//meta[@property="og:title"]/@content',

            'TestDateText': 'substring-before('
            '//li[@itemprop="datePublished"]/@content, "T")',
        }

        review = self.init_item_by_xpaths(response, 'review', review_xpaths)

        review['TestUrl'] = response.url
        review['ProductName'] = self.get_product_name(response)
        review['source_id'] = self.spider_conf['source_id']
        review['DBaseCategoryName'] = 'PRO'  # 'USER'

        if not review['TestSummary'] or review['TestSummary'].startswith(
                'Source :'):
            test_summary_alt_xpath = '//div[@class="blog-post-body"]' \
                '//p[2]//text()'
            test_summary_alt = self.extract(
                response.xpath(test_summary_alt_xpath))
            if test_summary_alt:
                review['TestSummary'] = test_summary_alt

        return review
