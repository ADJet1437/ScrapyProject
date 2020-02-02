__author__ = 'leonardo'

import re
from scrapy.http import Request

from alascrapy.items import CategoryItem
from alascrapy.lib.generic import  get_full_url
from alascrapy.spiders.mediamarkt_nl import MediaMarktNlSpider


class MediaMarktATSpider(MediaMarktNlSpider):
    name = 'mediamarkt_at'
    allowed_domains = ['mediamarkt.at']
    start_urls = ['http://www.mediamarkt.at/de/shop/produkte.html']
    category_id_re = re.compile("-(\d+)\.html")
    locale = 'de_AT'
    kind = 'mediamarkt_at_id'

    def parse(self, response):
        category_urls_xpath = "//ul[@class='top-navigation-items']/li/a[contains(@href,'/category')]/@href"

        category_urls = self.extract_list_xpath(response, category_urls_xpath)
        for category_url in category_urls:
            category_url = get_full_url(response, category_url)
            request = Request(category_url, self.parse_sub_category)
            yield request

    def parse_sub_category(self, response):
        sub_category_xpath = "//div[@id='category']//ul/li//h2/a/@href"
        category_urls = self.extract_list_xpath(response, sub_category_xpath)
        for category_url in category_urls:
            category_url = get_full_url(response, category_url)
            request = Request(category_url, self.parse_category)
            yield request

    def parse_category(self, response):
        subcategories_url_xpath = "//ul[@class='categories-tree-descendants']/li/a/@href"
        category_urls = self.extract_list_xpath(response, subcategories_url_xpath)
        if not category_urls:
            for item in self.parse_category_leaf(response):
                yield item
        else:
            for category_url in category_urls:
                category_url = get_full_url(response, category_url)
                request = Request(category_url, self.parse_category)
                yield request

    def parse_category_leaf(self, response):
        category = response.meta.get('category', None)
        category_path_xpath = "//ul[@class='breadcrumbs']/li[not(@class='home')]//text()"
        product_url_xpath = "//div[@class='product-wrapper']//h2/a/@href"
        next_page_url_xpath = "//a[@rel='next']/@href"

        if not category:
            category_path = self.extract_list_xpath(response, category_path_xpath)
            category_path = ' | '.join(category_path)

            cat_id_match = re.search(self.category_id_re, response.url)
            cat_id = ''
            if cat_id_match:
                cat_id = cat_id_match.group(1)

            category = CategoryItem()
            category['category_path'] = category_path
            category['category_url'] = response.url
            category['category_string'] = cat_id
            yield category

        product_urls = self.extract_list_xpath(response, product_url_xpath)

        for product_url in product_urls:
            product_url = get_full_url(response, product_url)
            request = Request(product_url, self.parse_product)
            request.meta['category'] = category
            yield request

        next_page_url = self.extract_xpath(response, next_page_url_xpath)
        if next_page_url:
            next_page_url = get_full_url(response, next_page_url)
            request = Request(next_page_url, self.parse_category_leaf)
            response.meta['category'] = category
            yield request
