# -*- coding: utf-8 -*-
import scrapy

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider

# This spider is banned by Arie on 2018-08-29
# due to the poor quality of the review from the source.
class WiredItSpider(AlaSpider):
    name = 'wired_it'
    allowed_domains = ['wired.it']
    start_urls = ['https://www.wired.it/mobile/',
                  'https://www.wired.it/gadget/']

    def parse(self, response):
        links_xpath = '//p[@class="article-title"]/a/@href'
        links = self.extract_list(response.xpath(links_xpath))

        for link in links:
            yield response.follow(link, callback=self.parse_page)

        # next page
        next_page_xpath = '//li[@class="next"]/a/@href'
        next_page = response.xpath(next_page_xpath).extract_first()

        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def get_product_name(self, response):
        name_xpath = self.extract(response.xpath('//meta[@property="og:url"]/@content'))
        name = name_xpath.split('/')
        # after spliting by '/' the eighth_item on the list is the name
        eighth_item = 8
        productname = name[eighth_item]
        return productname.replace('-', ' ').replace('review', '')

    def parse_page(self, response):
        product_xpaths = {
            'PicURL': '//meta[@property="og:image"]/@content',

            'OriginalCategoryName': '//nav[@class="breadcrumbs"]'
            '/p/span/span/a[@class="current"]/span/text()',

            'source_internal_id': '//div/@data-tid'
        }

        review_xpaths = {
            'TestSummary': '//meta[@property="og:description"]/@content',

            'Author': '//div[@class="row hidden-lg"]//div[@class="author"]/a/'
            '@title',

            'source_internal_id': '//div/@data-tid',

            'TestDateText': 'substring-before(//meta'
            '[@property="article:published_time"]/@content, "T")'

        }

        product = self.init_item_by_xpaths(response, 'product', product_xpaths)
        review = self.init_item_by_xpaths(response, 'review', review_xpaths)

        title_xpath = 'substring-before(//meta[@property="og:title"]/@content, "- Wired")'
        title = self.extract(response.xpath(title_xpath))

        product['ProductName'] = self.get_product_name(response)
        review['ProductName'] = self.get_product_name(response)
        review['TestTitle'] = title
        review['DBaseCategoryName'] = 'PRO'

        yield product
        yield review
