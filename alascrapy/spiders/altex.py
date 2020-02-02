"""gsmarena Spider: """

__author__ = 'leonardo'

import re

from scrapy.spiders import Rule
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy.http import Request

from alascrapy.items import ProductItem, CategoryItem
from alascrapy.spiders.base_spiders.ala_crawl import AlaCrawlSpider


class AltexSpider(AlaCrawlSpider):
    name = 'altex'
    allowed_domains = ['altex.com']
    start_urls = ['http://www.altex.com/site_map.aspx']
    category_url_re = re.compile('http://www.altex.com/[\w\-]+-C\d+.aspx$')
    rules = [Rule(LxmlLinkExtractor(allow=category_url_re,
                                    unique=True,
                                    restrict_xpaths='//*[@id="webpagePage"]'),
                  callback='parse_categories')]

    def parse_categories(self, response):
        base_url = get_base_url(response)
        category_list = response.xpath('//*[@class="categoryItemDisplay"]')
        category_url_xpath = './/*[@class="itemName"]/a/@href'
        category_leaf_xpath = './/*[@class="itemName"]/a/text()'
        for category_xpath in category_list:
            category = CategoryItem()
            category['category_url'] = \
                self.extract(category_xpath.xpath(category_url_xpath))
            category['category_url'] = \
                urljoin_rfc(base_url, category['category_url'])
            category['category_leaf'] = \
                self.extract(category_xpath.xpath(category_leaf_xpath))

            request = Request(category['category_url'],
                              callback=self.parse_product_list)
            request.meta['category'] = category
            yield request

    def parse_product_list(self, response):
        base_url = get_base_url(response)
        category = response.meta['category']

        category_path_xpath = \
            '//*[@class="breadCrumbs categoryBreadCrumbs"]//text()[normalize-space()]'
        product_list_xpath = \
            '//*[@class="categoryListListing"]//*/tr'
        product_relative_url_xpath = \
            './/td[@class="itemName"]/a/@href'
        product_name_xpath = \
            './/td[@class="itemName"]/a/text()'
        source_internal_id_xpath = \
            './/td[@class="sku"]/span/text()'
        product_manufacturer_xpath = \
            './/td[@class="manufacturer"]/a/text()'

        category['category_path'] = \
            response.xpath(category_path_xpath).extract()
        category['category_path'] = \
            "".join([cat.strip() for cat in category['category_path']])

        product_list = response.xpath(product_list_xpath)[1:]
        for product_row in product_list:
            product_relative_url = \
                self.extract(product_row.xpath(product_relative_url_xpath))

            product = ProductItem()
            product['ProductName'] = \
                self.extract(product_row.xpath(product_name_xpath))

            product['TestUrl'] = urljoin_rfc(base_url, product_relative_url)
            product['source_internal_id'] = \
                self.extract(product_row.xpath(source_internal_id_xpath))
            product['ProductManufacturer'] = \
                self.extract(product_row.xpath(product_manufacturer_xpath))
            product['OriginalCategoryName'] = category['category_leaf']

            request = Request(product['testurl'], callback=self.parse_product)
            request.meta['category'] = category
            request.meta['product'] = product
            yield request

    def parse_product(self, response):
        base_url = get_base_url(response)

        category = response.meta['category']
        product = response.meta['product']

        relative_pic_url_xpath = '//*[@class="mainImage"]/a/@href'
        relative_pic_url = self.extract(response.xpath(relative_pic_url_xpath))
        product['PicURL'] = urljoin_rfc(base_url, relative_pic_url)

        yield category
        yield product
