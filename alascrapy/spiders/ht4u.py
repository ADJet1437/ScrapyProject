# -*- coding: utf8 -*-

from datetime import datetime
from scrapy.http import Request
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem


class Ht4u_netSpider(AlaSpider):
    name = 'ht4u'
    allowed_domains = ['ht4u.net']

    start_urls = ['https://www.ht4u.net/reviews/']

    def __init__(self, *args, **kwargs):
        super(Ht4u_netSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

        # In order to test another stored_last_date
        self.stored_last_date = datetime(2015, 2, 8)

    def parse(self, response):
        # print " 	...PARSE: " + response.url
        # print " --self.stored_last_date: " + str(self.stored_last_date)

        review_urls_xpath = '//ul[@class="newslist"]/li/a/@href'
        review_urls = response.xpath(review_urls_xpath).getall()

        for r_url in review_urls:
            yield response.follow(url=r_url,
                                  callback=self.parse_product_review)

    def get_product_name_based_on_title(self, title):
        ''' This function will 'clean' the title of the review
            in order to get the product name '''
        p_name = title

        # Removing certain words
        words_to_remove = ['The New Order im Test', 'im Test', 'Guide:',
                           'Sparsamer:', 'Frischware:', 'Produktvorstellung:',
                           'Effizienter:', 'Hochadel:', 'Kurz und knapp:',
                           'Unvernunft im Quadrat:', u'Designerstück:',
                           'Take 2:', 'Roundup:']

        for w in words_to_remove:
            if w in title:
                p_name = p_name.replace(w, '')

        # Removing unnecessary spaces:
        p_name = p_name.replace('  ', ' ')
        p_name = p_name.strip()

        return p_name

    def parse_product_review(self, response):
        # print "     ...PARSE_PRODUCT_REVIEW: " + response.url

        # Checking date
        date_xpath = '//span[@itemprop="datePublished"]/@content'
        date = response.xpath(date_xpath).get()
        date = datetime.strptime(date, '%Y-%m-%d')

        if date > self.stored_last_date:

            # REVIEW ITEM ------------------------------------------
            review_xpaths = {
                'TestTitle': '//title[1]//text()'
            }

            # Create the review
            review = self.init_item_by_xpaths(response,
                                              "review",
                                              review_xpaths)

            # 'TestTitle'
            if '- HT4U.net' in review['TestTitle']:
                review['TestTitle'] = \
                    review['TestTitle'].replace('- HT4U.net', '')
                review['TestTitle'] = review['TestTitle'].strip()

            # 'ProductName'
            title = review['TestTitle']
            review['ProductName'] = self.get_product_name_based_on_title(title)

            # 'Author'
            review['Author'] = None

            # 'TestSummary'
            summary_xpath = '//div[@itemprop="articleBody"]/b[1]//text()'
            summary = response.xpath(summary_xpath).get()
            review['TestSummary'] = summary

            # 'TestDateText'
            review['TestDateText'] = date.strftime("%Y-%m-%d")

            # 'DBaseCategoryName'
            review['DBaseCategoryName'] = 'PRO'

            # 'source_internal_id'
            sid = response.url
            # sid looks like:
            #   www.../reviews/2018/msi_z370_gaming_pro_carbon_im_test/
            review['source_internal_id'] = sid.split('/')[-2]
            # ------------------------------------------------------

            # PRODUCT ITEM -----------------------------------------
            product = ProductItem()
            product['source_internal_id'] = review['source_internal_id']

            cats_xpath = '//div[@class="date"]/a//text()'
            cats = response.xpath(cats_xpath).getall()

            cat = None
            if u'Prozessoren' in cats:
                cat = 'Processor'
            elif u'Storage & Speicher' in cats:
                cat = 'Storage'
            elif u'Peripherie' in cats:
                cat = 'Peripheral Device'
            elif u'Mainboards' in cats:
                cat = 'Motherboard'
            elif u'Grafikkarten' in cats:
                cat = 'Graphics Card'
            elif u'Geh\xe4use & K\xfchlung' in cats:
                cat = 'Housing and Cooling'
            product['OriginalCategoryName'] = cat

            product['ProductName'] = review['ProductName']

            pic_url_xpath = '//div[@id="container"]//img[1]/@src'
            pic_url = response.xpath(pic_url_xpath).get()
            product['PicURL'] = pic_url

            product['TestUrl'] = response.url
            # ------------------------------------------------------

            yield review
            yield product
