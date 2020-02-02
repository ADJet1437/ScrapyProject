# -*- coding: utf8 -*-

import re

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider

from alascrapy.items import ProductIdItem

__author__ = 'ebrima'


class SweclockersComSpider(AlaSpider):
    name = 'sweclockers_com'
    allowed_domains = ['sweclockers.com']
    start_urls = ['https://www.sweclockers.com/arkiv/typ/test']

    def parse(self, response):
        # the wrapper
        products = response.xpath('//div[@class="listItem"]')

        for product in products:
            link = self.extract(product.xpath('h3/a/@href'))
            yield response.follow(link, callback=self.parse_page)

        # next page
        next_page_xpath = '//a[@class="next-page"]/@href'
        next_page = self.extract(response.xpath(next_page_xpath))
        if next_page:
            yield response.follow(next_page)

    def get_product_name(self, response):
        p_name_xpath = '//div[@class="inner"]/h1[@itemprop="headline"]/text()'
        product_name = self.extract(response.xpath(p_name_xpath))
        product_name = product_name.replace('Snabbtest: ', '')
        if ' - ' in product_name:
            name = product_name.split(' - ')[0]
        elif ':' in product_name:
            name = product_name.split(':')[0]
        else:
            name = product_name.split(u'–')[0]

        return name.strip('""')

    def parse_page(self, response):
        product_xpaths = {'PicURL': '//meta[@property="og:image"]/@content',
                          'OriginalCategoryName': '//ul[@class="meta"]'
                          '/li[@class="category"]/a/text()'
                          }

        review_xpaths = {'TestSummary':
                         '//meta[@property ="og:description"]/@content',
                         'Author': '//meta[@name="author"]/@content',
                         'TestTitle': 'substring-before(//meta[@property="og:title"]/@content," - T")',
                         'TestDateText': 'substring-before(//ul[@class="meta"]'
                         '/li/time/text(), " ")'

                         }

        product = self.init_item_by_xpaths(response, 'product', product_xpaths)
        review = self.init_item_by_xpaths(response, 'review', review_xpaths)

        source__int_id_xpath = '//meta[@property="og:url"]/@content'
        source__int_id = self.extract(response.xpath(source__int_id_xpath))
        source_int_id = re.findall(r'test/(\d+)', source__int_id)
        # the number zero(0) is to get the first index in the list
        source_internal_id = source_int_id[0]

        product['source_internal_id'] = source_internal_id
        product['ProductName'] = self.get_product_name(response)

        yield product

        review['ProductName'] = self.get_product_name(response)
        review['source_internal_id'] = source_internal_id
        review['DBaseCategoryName'] = 'PRO'

        summary_page_xpath = '//div[@class="pageList"]/ul/li[last()]/a/@href'
        summary_page = self.extract(response.xpath(summary_page_xpath))

        if summary_page:
            yield response.follow(summary_page, callback=self.parse_summary,
                                  meta={'review': review,
                                        'product': product})
        else:
            yield review

    def parse_price(self, product, response):
        price_xpath = '//div[@class="bbcode"]/p/br[1]'\
            '/preceding-sibling::text()'
        price_str = self.extract(response.xpath(price_xpath))

        if price_str:
            return ProductIdItem.from_product(
                product,
                kind='price',
                value=price_str
            )

    def parse_summary(self, response):
        review = response.meta['review']
        product = response.meta['product']
        pros_xpath = '//ul[@class="bbList bbUl"][1]/li/p/text()'
        test_pros = self.extract(response.xpath(pros_xpath))
        cons_xpath = '//ul[@class="bbList bbUl"][2]/li/p/text()'
        test_cons = self.extract(response.xpath(cons_xpath))
        product_id = self.parse_price(product, response)

        review['TestPros'] = test_pros
        review['TestCons'] = test_cons

        yield review
        yield product_id
