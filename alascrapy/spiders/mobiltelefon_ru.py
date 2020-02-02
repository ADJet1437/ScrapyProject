
# -*- coding: utf8 -*-

import dateparser
from datetime import datetime
from scrapy.http import Request
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem


class Mobiltelefon_ruSpider(AlaSpider):
    name = 'mobiltelefon_ru'
    allowed_domains = ['mobiltelefon.ru']

    base_url = 'https://mobiltelefon.ru/contents_obzor_{}.html'

    start_urls = ['https://mobiltelefon.ru/contents_obzor_0.html']

    page = 0

    def __init__(self, *args, **kwargs):
        super(Mobiltelefon_ruSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

        # In order to test another stored_last_date
        # self.stored_last_date = datetime(2018, 2, 8)

    def parse(self, response):
        # print " 	...PARSE: " + response.url
        # print " --self.stored_last_date: " + str(self.stored_last_date)

        review_sections_xpath = '//section[@class="block_news"]'
        review_sections = response.xpath(review_sections_xpath)

        date = None
        for r_sec in review_sections:
            date_xpath = './/p[@class="line2"]/a[1]/following-'\
                         'sibling::text()[1]'
            date = r_sec.xpath(date_xpath).get()
            # date looks like: | 10 февраля 2019, 14:29 |
            date = date.split(', ')[0]
            date = date.replace('|', '')
            date = date.strip()
            date = dateparser.parse(date,
                                    date_formats=['%d %B %Y'],
                                    languages=['ru', 'es'])

            if date > self.stored_last_date:
                url_xpath = './@onclick'
                url = r_sec.xpath(url_xpath).get()
                # url looks like:
                #   "url_loc='https://mobiltelefon.ru/post_1555664522.html'"
                url = url.split("loc='")[-1]
                url = url.split("';")[0]

                yield Request(url=url,
                              callback=self.parse_product_review,
                              meta={'date': date.strftime("%Y-%m-%d")})

        # Checking whether we should scrape the next page
        if date > self.stored_last_date:
            self.page += 1
            yield Request(url=self.base_url.format(self.page),
                          callback=self.parse)

    def get_product_name_based_on_title(self, title):
        ''' This function will 'clean' the title of the review
            in order to get the product name '''
        p_name = title

        # Spliting title
        if u':' in p_name:
            p_name = p_name.split(u':')[0]

        # Removing certain words
        words_to_remove = [u'Тест',
                           u'Распаковка и обзор',
                           u'Распаковка',
                           u'Обзор',
                           u'обзор',
                           u'Распаковка, игровой тест и первые впечатления от',
                           u'Знакомимся с',
                           u'Тест камеры',
                           u'Как снимает камера',
                           u'Быстрый']

        for w in words_to_remove:
            if w in title:
                p_name = p_name.replace(w, '')

        # Removing unnecessary spaces:
        p_name = p_name.replace('  ', ' ')
        p_name = p_name.strip()

        return p_name

    def parse_product_review(self, response):
        # print "     ...PARSE_PRODUCT_REVIEW: " + response.url

        title = response.xpath('//meta[@property="og:title"]/@content').get()

        drop_review_words = ['PS4',
                             u'Сравнение',
                             'PocketBook']
        for word in drop_review_words:
            if word in title:
                return

        cat = None
        if ("Watch" in title) or ("watch" in title):
            cat = "Smartwatch"
        elif u'планшет' in title:
            cat = "Tablet"
        else:
            cat = "Smartphone"

        # REVIEW ITEM -------------------------------------------------------
        review_xpaths = {
            'TestTitle': '//meta[@property="og:title"]/@content',
            'TestSummary': '//meta[@name="description"]/@content',
        }

        # Create the review
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        # 'ProductName'
        title = review['TestTitle']
        review['ProductName'] = self.get_product_name_based_on_title(title)

        # 'Author'
        author_xpath = '//a[text()="Mobiltelefon"]/preceding-sibling::text()'
        author = response.xpath(author_xpath).get()
        # author looks like: © Артур Лучкин.
        author = author.replace(u'©', '')
        author = author.replace('.', '')
        author = author.strip()
        review['Author'] = author

        # 'TestDateText'
        review['TestDateText'] = response.meta.get('date')

        # 'DBaseCategoryName'
        review['DBaseCategoryName'] = 'PRO'

        # 'source_internal_id'
        sid = response.url.split('post_')[-1]
        sid = sid.split('.html')[0]
        review['source_internal_id'] = sid
        # -------------------------------------------------------------------

        # PRODUCT ITEM ------------------------------------------------------
        product = ProductItem()
        product['source_internal_id'] = review['source_internal_id']
        product['OriginalCategoryName'] = cat
        product['ProductName'] = review['ProductName']

        pic_url_xpath = '//meta[@property="og:image"]/@content'
        pic_url = response.xpath(pic_url_xpath).get()
        product['PicURL'] = pic_url

        product['TestUrl'] = response.url
        # -------------------------------------------------------------------

        yield review
        yield product
