
# -*- coding: utf8 -*-

from datetime import datetime
import dateparser

from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem


class Gizmodo_uol_com_br(AlaSpider):
    name = 'gizmodo_uol_com_br'
    allowed_domains = ['gizmodo.uol.com.br']

    def __init__(self, *args, **kwargs):
        super(Gizmodo_uol_com_br, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

        # In order to test another stored_last_date
        # self.stored_last_date = datetime(2000, 2, 8)

    def start_requests(self):
        # print "     ...START_REQUESTS"

        base_url = 'https://gizmodo.uol.com.br/tag/'

        tags_to_scrape = ['smartwatch',
                          'smartphone',
                          'iphone',
                          'fone-de-ouvido',
                          'notebook',
                          'ipad',
                          'cameras',
                          'camera']

        for category in tags_to_scrape:
            yield Request(url=base_url+category,
                          callback=self.parse,
                          meta={'category': category})

    def parse(self, response):
        # print "     ...PARSE: " + response.url

        reviews_div_xpath = '//div[@id="mdContent"]//div[@class="grid-item '\
                            'col-xs-12 col-sm-6"]'
        reviews_div = response.xpath(reviews_div_xpath)

        for r_div in reviews_div:
            # Check whether it's a review
            type_of_post_xpath = './/div[@class="postHeader"]//a//text()'

            type_of_post = r_div.xpath(type_of_post_xpath).get()

            if type_of_post == 'review':
                # Pick the date
                date_xpath = './/span[@class="metaText '\
                             'metaDate"]/abbr/@title'

                date = r_div.xpath(date_xpath).get()

                date = date.split('@')[0]
                date = date.strip()
                date = dateparser.parse(date, date_formats=['%d de %m de %Y'],
                                        languages=['pt', 'en'])

                if date > self.stored_last_date:
                    url_xpath = './/div[@class="postFeaturedImg u-ratio2to1 '\
                                'o-imageCropper"]/a/@href'

                    url = r_div.xpath(url_xpath).get()

                    category = response.meta.get('category')
                    yield Request(url=url,
                                  callback=self.parse_product_review,
                                  meta={'category': category})

            # Checking whether we should head to next page
            # Check whether there's a next page
            next_page_url_xpath = '//a[@class="next page-numbers"]/@href'
            next_page_url = response.xpath(next_page_url_xpath).get()

        if next_page_url:
            # Get the last date
            date_xpath = './/span[@class="metaText '\
                            'metaDate"]/abbr/@title'

            date = reviews_div[-1].xpath(date_xpath).get()

            date = date.split('@')[0]
            date = date.strip()
            date = dateparser.parse(date, date_formats=['%d de %m de %Y'],
                                    languages=['pt', 'en'])

            if date > self.stored_last_date:
                category = response.meta.get('category')
                yield Request(url=next_page_url,
                              callback=self.parse,
                              meta={'category': category})

    def parse_product_review(self, response):
        # print "     ...PARSE_PRODUCT_REVIEW: " + response.url

        review_xpaths = {
            'TestTitle': '//meta[@property="og:title"][1]/@content',
            'Author': '//meta[@name="author"]/@content',
            'TestSummary': '//meta[@name="description"]/@content',
        }

        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        # Source internal ID
        short_link_xpath = '//link[@rel="shortlink"]/@href'
        short_link = response.xpath(short_link_xpath).get()
        short_link = short_link.split('=')[1]
        review['source_internal_id'] = short_link

        if not review['TestSummary']:
            summary_xpath = '//meta[@property="og:description"][last()]'\
                            '/@content'
            summary = response.xpath(summary_xpath).get()
            review['TestSummary'] = summary

        date_xpath = '//abbr[@itemprop="datePublished"]/@content'
        date = response.xpath(date_xpath).get().split(' ')[0]
        review['TestDateText'] = date

        # This website doesn't put the name of the products anywhere.
        # It's always inside some big texts, for example the 'TestTitle'.
        product_name = review['TestTitle']
        words_to_remove = ['[Review]',
                           'Review',
                           ]
        for word in words_to_remove:
            product_name = product_name.replace(word, '')

        if ":" in product_name:
            product_name = product_name.split(":")[0]

        product_name = product_name.strip()
        review['ProductName'] = product_name

        review['DBaseCategoryName'] = 'PRO'

        # PRODUCT -----------------------------------------------------
        product = ProductItem()
        product['source_internal_id'] = review['source_internal_id']
        product['OriginalCategoryName'] = response.meta.get('category')
        product['ProductName'] = review['ProductName']

        pic_url_xpath = '//meta[@property="og:image:url"]/@content'
        pic_url = response.xpath(pic_url_xpath).get()
        product['PicURL'] = pic_url
        product['TestUrl'] = response.url

        yield product
        yield review
