# -*- coding: utf8 -*-
from datetime import datetime
import re

from alascrapy.lib.dao import incremental_scraping as incremental_utils
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import date_format


class TestDeSpider(AlaSpider):
    name = 'test_de'
    allowed_domains = ['test.de']
    start_urls = ['https://www.test.de/multimedia/schnelltests/']

    def __init__(self, *args, **kwargs):
        super(TestDeSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf['source_id'])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):
        reviews_xpath = '//div[@class="themenliste-alle__list"]/ul/li/a/@href'
        review_links = response.xpath(reviews_xpath).extract()
        for link in review_links:
            yield response.follow(url=link, callback=self.parse_product)

        next_page_xpath = '//a[./i[@class="svgicon pager__forwards"]]/@href'
        next_page_link = response.xpath(next_page_xpath).extract()
        if len(next_page_link) > 0:
            oldest_review_day_xpath = "(//em[@class='date'])[last()]/text()"
            date_time_to_compare = self._get_date_to_compare(
                response, oldest_review_day_xpath)
            if date_time_to_compare < self.stored_last_date:
                return
            yield response.follow(url=next_page_link[0], callback=self.parse)

    def get_product_name(self, response):
        product_name_xpath1 = '//span[@class="pageTitle__headline"]/text() '
        product_name_xpath2 = '//span[@class="page-title__headline"]/text()'
        if product_name_xpath1:
            product_name = self.extract(response.xpath(product_name_xpath1))
        if product_name_xpath2:
            product_name = self.extract(response.xpath(product_name_xpath2))
        # Removes the ": " from the end of the title (eg. = "Apple iPhone X: ")
        spaces_colon_regex = '[: ]+$'
        return re.sub(spaces_colon_regex, '', product_name)

    def get_sii(self, response):
        id_url_regex = '-(\\d{7})-.*/$'
        match = re.search(id_url_regex, response.url)
        if match:
            # re.search(regex, 'http../Title-5079271-0/').group(1) -> 5079271
            id_matching_group = 1
            return match.group(id_matching_group)
        return None

    def parse_product(self, response):
        product_xpaths = {
            'OriginalCategoryName': '(//div[@class="page__body__intro"]'
            '/ul/li[2]/a/text())[last()]',
            'PicURL': '//picture//img[1]/@src|'
            '//a[@class="js-media-object-zoom-image"]/@href',  # for old pages
        }
        product = self.init_item_by_xpaths(response, 'product', product_xpaths)
        product['TestUrl'] = response.url
        product['source_id'] = self.spider_conf['source_id']
        product['source_internal_id'] = self.get_sii(response)
        product['ProductName'] = self.get_product_name(response)

        review_xpaths = {
            'Author': '//meta[@name="author"]/@content',
            'TestSummary': '//meta[@name="description"]/@content',
            'TestTitle': '//title/text()',
        }

        review = self.init_item_by_xpaths(response, 'review', review_xpaths)

        date_time_xpath = '//span[@class="page-title__contentdate"]/text()'
        date_time_to_compare = self._get_date_to_compare(
            response, date_time_xpath)
        if date_time_to_compare < self.stored_last_date:
            return
        date_time_str = self.extract(response.xpath(date_time_xpath))
        date_str = date_time_str.replace('.', '-')
        date_time = date_format(date_str, '%d-%m-%Y')
        review['TestDateText'] = date_time

        review['TestUrl'] = response.url
        review['DBaseCategoryName'] = 'PRO'
        review['source_id'] = self.spider_conf['source_id']
        review['source_internal_id'] = self.get_sii(response)
        review['ProductName'] = self.get_product_name(response)
        
        yield review
        yield product

    def _get_date_to_compare(self, response, xpath):
        date_xpath = xpath
        date_str = self.extract(response.xpath(date_xpath))
        _date = date_str.replace('.', '-')
        date_time_to_compare = datetime.strptime(_date, '%d-%m-%Y')
        return date_time_to_compare
