# -*- coding: utf8 -*-

import json
import re
from datetime import datetime

from alascrapy.items import ReviewItem, ProductItem
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider


class ComputerbildDeSpider(AlaSpider):
    name = 'computerbild_de'
    allowed_domains = ['computerbild.de']
    start_urls = ['http://www.computerbild.de/technik/mobil/tests/']

    def __init__(self, *args, **kwargs):
        super(ComputerbildDeSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):
        xpaths = {
            'review_links': '//div[@class="articleList"]'
            '//h3[@class="headLine"]/a/@href',
            'next_page': '//div[contains(concat(" ", normalize-space(@class)'
            ', " "), " paging ")]/div[@class="next"]/a/@href'
        }
        review_links = self.extract_list(
            response.xpath(xpaths['review_links']))
        next_page_link = self.extract(response.xpath(xpaths['next_page']))

        for link in review_links:
            yield response.follow(url=link, callback=self.parse_product)
        # Checks if there is a "next_page" to extract more review links
        if next_page_link:
            last_review_content = review_links[-1]
            yield response.follow(url=last_review_content,
                                  callback=self._should_go_to_next_page)
            if self._should_go_to_next_page:
                yield response.follow(url=next_page_link[0],
                                      callback=self.parse)

    def _should_go_to_next_page(self, response):
        date = self._get_date_time_to_compare
        return date > self.stored_last_date

    def _get_date_time_to_compare(self, response):
        date_xpath = 'substring-before(//meta[@itemprop="dateModified"]/@content, "T")'
        date_time_to_compare = datetime.strptime(date, '%Y-%m-%d')
        return date_time_to_compare

    def retrieve_ssi(self, url):
        # Extract the source_internal_id from the URL
        sii_search = re.search('(\\d+)\\.html$', url)
        return sii_search.group(1)

    def parse_product(self, response):
        product_xpaths = {
            'PicURL': '//meta[@property="og:image"]/@content',
            'ProductName':
                'substring-before(//meta[@property="og:title"]/@content, ":")',
        }

        ocn_xpath = '//nav[@id="breadcrumb"]//span[@itemprop="name"]/text()'

        product = self.init_item_by_xpaths(response, "product", product_xpaths)

        ocn = response.xpath(ocn_xpath).extract()
        # Original Category name: ['Home','Technik','Mobil','Handy','Tests']
        # Remove edges
        product['OriginalCategoryName'] = ' | '.join(ocn[2:-1])
        product['source_internal_id'] = self.retrieve_ssi(response.url)
        product['TestUrl'] = response.url
        product['source_id'] = self.spider_conf["source_id"]

        review_xpaths = {
            'TestDateText': 'substring-before(//meta[@itemprop="dateModified"]/@content, "T")',
            'TestSummary': '//meta[@property="og:description"]/@content',
            'ProductName':
            'substring-before(//meta[@property="og:title"]/@content, ":")',
            'TestTitle': '//meta[@property="og:title"]/@content',
            'Author':
            '//span[@itemprop="author"]/meta[@itemprop="name"]/@content',
            'TestPros': '//div[@class="pro"]/ul//li/text()',
            'TestCons': '//div[@class="contra"]/ul//li/text()',
        }

        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        if not review.get('TestDateText', ''):
            return
        date = review['TestDateText']
        date_time_to_compare = datetime.strptime(date, '%Y-%m-%d')
        if date_time_to_compare < self.stored_last_date:
            return
        review['source_internal_id'] = self.retrieve_ssi(response.url)
        review['TestUrl'] = response.url
        review['source_id'] = self.spider_conf["source_id"]
        review['DBaseCategoryName'] = 'PRO'

        if review.get('TestPros', ''):
            yield product
            yield review
