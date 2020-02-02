# -*- coding: utf8 -*-

import re
import dateparser
from datetime import datetime
from scrapy.http import Request
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem


class Av_magazin_deSpider(AlaSpider):
    name = 'av-magazin_de'
    allowed_domains = ['av-magazin.de']

    start_urls = ['http://www.av-magazin.de/Testberichte.33.0.html']

    def __init__(self, *args, **kwargs):
        super(Av_magazin_deSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

        # In order to test another stored_last_date
        # self.stored_last_date = datetime(2018, 2, 8)

    def parse(self, response):
        # print "     ...PARSE: " + response.url
        # print " --self.stored_last_date: " + str(self.stored_last_date)

        review_divs_xpath = '(//div[@class="news-header-list-container-box"])'\
                            '[not(ancestor::div[@id="c35856"])]'

        review_divs = response.xpath(review_divs_xpath)

        review_url_xpath = './a[1]/@href'
        for r_div in review_divs[:-1]:

            review_url = r_div.xpath(review_url_xpath).get()
            if review_url:

                pic_url = r_div.xpath('.//img/@src').get()
                pic_url = "http://www.av-magazin.de/" + pic_url

                yield response.follow(url=review_url,
                                      callback=self.parse_product_review,
                                      meta={'check_next_page': False,
                                            'pic_url': pic_url})

        # For the last review of the page
        next_page_url_xpath = u'//a[text()="Nächste >"]/@href'
        next_page_url = response.xpath(next_page_url_xpath).get()

        review_url = review_divs[-1].xpath(review_url_xpath).get()

        next_page = False
        if review_url:
            next_page = True

        pic_url = review_divs[-1].xpath('.//img/@src').get()
        pic_url = "http://www.av-magazin.de/" + pic_url

        yield response.follow(url=review_url,
                              callback=self.parse_product_review,
                              meta={'check_next_page': next_page,
                                    'next_page_url': next_page_url,
                                    'pic_url': pic_url})

    def get_date(self, response):
        date_xpath = '//div[@class="autor"]/h1//text()'
        date = response.xpath(date_xpath).get()
        # date looks like:
        # Testbericht von Volker Strassburg, 29. März 2019, Fotos ...
        # or
        # Testbericht von Philipp Schäfer 11.Januar 2019, Fotos: Hersteller
        # or
        # Testbericht ... Strassburg, 16.3.2019,

        pattern = re.compile(r'[0-9]{1,2}.[0-9]{1,2}.[0-9]{4}')
        matches = pattern.findall(date)
        if matches:
            date = matches[0]
            # date looks like: 16.3.2019
            date = datetime.strptime(date, '%d.%m.%Y')
            print date
        else:
            date = date.split('Fotos')[0]
            date = date.strip()
            date = date.split(' ')[-3:]
            date = "-".join(date)
            if '.' in date:
                date = date.replace('.', '')
            if ',' in date:
                date = date.replace(',', '')

            date = dateparser.parse(date,
                                    date_formats=['%d-%m-%Y'],
                                    languages=['de', 'es'])

        # Testbericht von Philipp Schäfer 11.Januar 2019, Fotos: Hersteller
        if not date:
            date = response.xpath(date_xpath).get()

            date = date.split('Fotos')[0]
            date = date.strip()
            date = date.split(' ')[-2:]
            date = "-".join(date)
            if '.' in date:
                date = date.replace('.', '')
            if ',' in date:
                date = date.replace(',', '')

            date = dateparser.parse(date,
                                    date_formats=['%d-%m-%Y'],
                                    languages=['de', 'es'])

        return date

    def get_product_name_based_on_title(self, title):
        ''' This function will 'clean' the title of the review
            in order to get the product name '''
        p_name = title

        # Spliting title
        get_first_piece = [u' – ', u'im Test']
        get_last_piece = [u'Test:', u'Im Test']

        for g_f in get_first_piece:
            if g_f in p_name:
                p_name = p_name.split(g_f)[0]

        for g_l in get_last_piece:
            if g_l in p_name:
                p_name = p_name.split(g_l)[-1]

        # Removing certain words
        words_to_remove = ['im Test',
                           'zum Top-Preis',
                           'Top-Preis',
                           'Die neue']

        for w in words_to_remove:
            if w in title:
                p_name = p_name.replace(w, '')

        # Removing unnecessary spaces:
        p_name = p_name.replace('  ', ' ')
        p_name = p_name.strip()

        return p_name

    def parse_product_review(self, response):
        print "     ...PARSE_PRODUCT_REVIEW: " + response.url

        date = self.get_date(response)

        if date > self.stored_last_date:

            # REVIEW ITEM ----------------------------------------------------
            review = ReviewItem()

            #  'TestTitle'
            test_title_xpath = '//div[@class="subheadtest"]/h4//text()'
            test_title = response.xpath(test_title_xpath).getall()
            test_title = " ".join(test_title)
            review['TestTitle'] = test_title

            # 'ProductName'
            product_name = \
                self.get_product_name_based_on_title(review['TestTitle'])
            review['ProductName'] = product_name

            # 'TestSummary'
            summary_xpath = '//div[@class="csc-textpic-text"]/*//text()'
            summary = response.xpath(summary_xpath).getall()
            summary = " ".join(summary)
            review['TestSummary'] = summary

            # 'TestDateText'
            review['TestDateText'] = date.strftime("%Y-%m-%d")

            # 'DBaseCategoryName'
            review['DBaseCategoryName'] = 'PRO'

            # 'source_internal_id'
            sid = response.url.split('.0.html')[0]
            sid = sid.split('/')[-1]
            sid = sid.split('.')[-1]
            review['source_internal_id'] = sid

            # 'TestUrl'
            review['TestUrl'] = response.url
            # ----------------------------------------------------------------

            # PRODUCT ITEM ---------------------------------------------------
            product = ProductItem()
            product['source_internal_id'] = review['source_internal_id']
            product['ProductName'] = review['ProductName']
            product['PicURL'] = response.meta.get('pic_url')
            product['TestUrl'] = response.url
            # ----------------------------------------------------------------

            yield review
            yield product

            # In case this is the last review of the page
            if response.meta.get('check_next_page'):
                yield response.follow(url=response.meta.get('next_page_url'),
                                      callback=self.parse)
