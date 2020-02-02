# -*- coding: utf8 -*-
from datetime import datetime

from scrapy.http import Request
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem


class D_pixx_deSpider(AlaSpider):
    name = 'd_pixx_de'
    allowed_domains = ['d-pixx.de']
    start_urls = ['http://www.d-pixx.de/category/test/']

    def __init__(self, *args, **kwargs):
        super(D_pixx_deSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

        # In order to test another stored_last_date
        # self.stored_last_date = datetime(2017, 2, 8)

    def parse(self, response):
        print "     ...PARSE: " + response.url

        review_divs_xpath = '//div[@class="td-block-row"]//'\
                            'div[@class="td-block-span6"]'
        review_divs = response.xpath(review_divs_xpath)

        for r_div in review_divs:
            date_xpath = './/div[@class="td-module-meta-info"]//time/@datetime'
            date = r_div.xpath(date_xpath).get()
            date = date.split('T')[0]

            date = datetime.strptime(date, "%Y-%m-%d")

            if date > self.stored_last_date:
                review_url_xpath = './/div[@class="td-module-thumb"]//a/@href'
                review_url = r_div.xpath(review_url_xpath).get()

                yield Request(url=review_url,
                              callback=self.parse_product_review,
                              meta={'date': date.strftime("%Y-%m-%d")})

        # Checking whether we should scrape the next page
        is_there_next_page_xpath = '//div[@class="page-nav '\
                                   'td-pb-padding-side"]/a/i'
        is_there_next_page = response.xpath(is_there_next_page_xpath)

        if is_there_next_page and (date > self.stored_last_date):
            next_page_url_xpath = '//div[@class="page-nav td-pb-padding-'\
                                  'side"]/a[last()]/@href'
            next_page_url = response.xpath(next_page_url_xpath).get()

            yield Request(url=next_page_url,
                          callback=self.parse)

    def parse_product_review(self, response):
        print "     ....PARSE_PRODUCT_REVIREW: " + response.url

        # REVIEW ITEM -------------------------------------------------------
        review_xpaths = {
            'TestTitle': '//meta[@property="og:title"]/@content',
            'TestSummary': '//meta[@property="og:description"]/@content',
            'Author': '//div[@class="td-author-by"]/following-sibling'
                      '::text()[1]'
        }

        # Create the review
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        # 'TestDateText'
        review['TestDateText'] = response.meta.get('date')

        # 'ProductName': '//meta[@property="og:image:alt"]/@content',
        product_name = review['TestTitle']
        product_name = product_name.lower()
        if "|" in product_name:
            product_name = product_name.split('|')[0]

        if '- hands-on mit' in product_name:
            product_name = product_name.split('- hands-on mit')[0]

        words_to_remove = ['im Test',
                           'im Praxistest',
                           '- Test mit Bildern in voller '
                           'Größe'.decode('utf-8'),
                           'in der praxis:',
                           'die spezialistin',
                           '- erster test',
                           'erster test',
                           '-',
                           'test']

        for word in words_to_remove:
            if word.lower() in product_name:
                product_name = product_name.replace(word.lower(), '')

        product_name = product_name.strip()
        review['ProductName'] = product_name

        # 'DBaseCategoryName'
        review['DBaseCategoryName'] = 'PRO'

        # 'source_internal_id'
        sid = response.url.split('/')[-2]
        review['source_internal_id'] = sid
        # -------------------------------------------------------------------

        # PRODUCT ITEM ------------------------------------------------------
        product = ProductItem()
        product['source_internal_id'] = review['source_internal_id']
        product['OriginalCategoryName'] = "Camera"
        product['ProductName'] = review['ProductName']

        pic_url_xpath = '//meta[@property="og:image"]/@content'
        pic_url = response.xpath(pic_url_xpath).get()
        product['PicURL'] = pic_url

        product['TestUrl'] = response.url
        # -------------------------------------------------------------------

        yield review
        yield product
