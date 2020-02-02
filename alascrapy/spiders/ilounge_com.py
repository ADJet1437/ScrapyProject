# -*- coding: utf8 -*-
import datetime
import re

from alascrapy.items import ProductIdItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider


class Ilounge_comSpider(AlaSpider):
    name = 'ilounge_com'
    allowed_domains = ['ilounge.com']
    start_urls = ['http://www.ilounge.com/index.php/reviews']

    def parse(self, response):
        next_page_xpath = "(//div[@class='next_on']/a)[1]/@href"
        review_urls_xpath = '//span[@class="rrcaption"]/a/@href'
        review_urls = self.extract_list(response.xpath(review_urls_xpath))

        for review_url in review_urls:
            yield response.follow(review_url,
                                  callback=self.parse_review_product)
        
        next_page = self.extract(response.xpath(next_page_xpath))
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_review_product(self, response):
        product = self.parse_product(response)
        review = self.parse_review(response)
        product_id = self.parse_price(product, response)
        yield product
        yield review
        yield product_id

    def get_sid(self, response):
        sid_xpath = "//script[contains(text(), 'disqus_identifier')]/text()"
        sid = self.extract(response.xpath(sid_xpath))
        source_int_id = re.findall(r'identifier = "(\d+)', sid)
        source_internal_id = source_int_id[0]
        return source_internal_id

    def parse_product(self, response):
        product_xpaths = {
            'PicURL': '//meta[@property="og:image"]/@content',
            "ProductName": '//h3/span/following-sibling::text()|'
            '//span[@itemprop="itemreviewed"]/text()',
            "ProductManufacturer": "//p/b[contains(text(), 'Company')]"
            "/following-sibling::a/text()",
            'source_internal_id': "substring-after(//div[@id='articlePage-1']"
            "/@data-article-id, '.')"
        }
        product = self.init_item_by_xpaths(response, 'product', product_xpaths)

        get_ocn = response.url.split('/')[-1]
        ocn = ' '.join(get_ocn.split('-')[-2:])
        product['OriginalCategoryName'] = ocn
        product["source_internal_id"] = self.get_sid(response)

        return product

    def parse_price(self, product, response):
        price_xpath = "//b[contains(text(),'Price')]/following-sibling::text()"
        price_str = self.extract(response.xpath(price_xpath))

        if price_str:
            return ProductIdItem.from_product(
                product,
                kind='price',
                value=price_str
            )

    def get_date(self, response):
        date_xpath = "//div[@class='byline']/span/following-sibling::text()"
        test_date = self.extract(response.xpath(date_xpath))
        test_date_text = datetime.datetime.strptime(
            test_date, '%A, %B %d, %Y').strftime('%Y-%m-%d')

        if test_date_text:
            return test_date_text

    def parse_review(self, response):
        review_xpaths = {
            "ProductName": '//h3/span/following-sibling::text()|'
            '//span[@itemprop="itemreviewed"]/text()',
            'TestTitle': '//meta[@property="og:title"]/@content',
            'Author': "substring-after(//div[@class='byline']"
            "/span/preceding-sibling::text(),'By ')",
            'source_internal_id': "substring-after(//div[@id='articlePage-1']"
            "/@data-article-id, '.')",
            'TestSummary': '//meta[@property="og:description"]/@content'
        }

        review = self.init_item_by_xpaths(response, 'review', review_xpaths)

        review["TestDateText"] = self.get_date(response)
        review["source_internal_id"] = self.get_sid(response)
        review['DBaseCategoryName'] = 'PRO'
        return review
