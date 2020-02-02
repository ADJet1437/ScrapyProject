# -*- coding: utf8 -*-

from datetime import datetime
from scrapy.http import Request
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem


class Mobiltest_dkSpider(AlaSpider):
    name = 'mobiltest_dk'
    allowed_domains = ['mobiltest.dk']

    def __init__(self, *args, **kwargs):
        super(Mobiltest_dkSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

    def start_requests(self):
        # print " 	...START_REQUESTS: "

        base_url = 'https://www.mobiltest.dk/'
        url_cat_dict = {'Smartphone': base_url + 'c/1/mobiltelefoner',
                        'Tablet': base_url + 'c/65/tablets',
                        'Headphones': base_url +
                        'c/159/tilbehoerbluetooth-headsets'
                        }

        for cat in url_cat_dict:
            yield Request(url=url_cat_dict[cat],
                          callback=self.parse,
                          meta={'cat': cat})

    def parse(self, response):
        # print " 	...PARSE: " + response.url
        # print " --self.stored_last_date: " + str(self.stored_last_date)

        review_tds_xpath = '//div[@id="contentMain"]/table[2]/tr'
        review_tds = response.xpath(review_tds_xpath)

        for r_td in review_tds[1:]:

            date_xpath = './td[3]//text()'
            date = r_td.xpath(date_xpath).get()
            # date looks like: d. 28-06-2013
            date = date.replace('d.', '')
            date = date.strip()
            date = datetime.strptime(date, '%d-%m-%Y')

            if date > self.stored_last_date:
                review_link_xpath = './td[1]/a/@href'
                review_link = r_td.xpath(review_link_xpath).get()

                author_xpath = './td[2]//text()'
                author = r_td.xpath(author_xpath).get()

                test_title_xpath = './td[1]/a//text()'
                test_title = r_td.xpath(test_title_xpath).get()

                yield Request(url=review_link,
                              callback=self.parse_product_review,
                              meta={'author': author,
                                    'date': date.strftime("%Y-%m-%d"),
                                    'test_title': test_title,
                                    'cat': response.meta.get('cat')})

    def get_product_name_based_on_title(self, title):
        ''' This function will 'clean' the title of the review
            in order to get the product name '''
        p_name = title

        # Removing certain words
        words_to_remove = ['test', 'minitest']
        for w in words_to_remove:
            if w in title:
                p_name = p_name.replace(w, '')

        # Removing unnecessary spaces:
        p_name = p_name.replace('  ', ' ')
        p_name = p_name.strip()

        return p_name

    def parse_product_review(self, response):
        # print " ...PARSE_PRODUCT_REVIEW: " + response.url

        # REVIEW ITEM ------------------------------------------------------
        review_xpaths = {
            'TestSummary': '//meta[@name="description"]/@content',
        }

        # Create the review
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        # 'TestTitle'
        review['TestTitle'] = response.meta.get('test_title')

        # 'ProductName'
        title = review['TestTitle']
        review['ProductName'] = self.get_product_name_based_on_title(title)

        # 'Author'
        review['Author'] = response.meta.get('author')

        # 'TestDateText'
        review['TestDateText'] = response.meta.get('date')

        # 'SourceTestScale' and 'SourceTestRating'
        # get all texts inside <strong>
        strong = response.xpath('//strong')
        rating = None
        for s in strong:
            if not rating:
                strong_text = s.xpath('.//text()').get()
                # print strong_text

                key_words = ['Score i alt', 'Karakter', 'I alt']
                if strong_text:
                    for w in key_words:
                        if w in strong_text:
                            rating = strong_text.replace(w, '')
                            if '%' in rating:
                                rating = rating.replace('%', '')
                                rating = rating.strip()
                            break
            else:
                break

        if rating and rating.isdigit():
            review['SourceTestRating'] = rating
            review['SourceTestScale'] = '100'

        # 'DBaseCategoryName'
        review['DBaseCategoryName'] = 'PRO'

        # 'TestPros' and 'TestCons'
        pros_xpath = '//strong[text()="Ting vi er glade for:"]' \
                     '/following::text()'
        pros = response.xpath(pros_xpath).getall()
        pros_list = []
        for p in pros:
            p = p.strip()
            p = unicode(p)
            if p == u'Ting vi er mindre glade for:' or \
               p == u'Ting vi er mindre glade for' or \
               p == u'Tinge vi er mindre glade for:' or \
               p == u'Ting vi ikke er så glade for:' or \
               p == u'Konklusion:':
                break
            else:
                pros_list.append(p)
        pros_list = ";".join(pros_list)

        cons_xpath = '//strong[text()="Ting vi er glade for:"]' \
                     '/following::text()'
        cons = response.xpath(cons_xpath).getall()
        cons_list = []
        for c in cons:
            c = c.strip()
            c = unicode(c)
            if c == u'Konklusion:' or \
               c == u'Konklusion' or \
               c == u'Konklusion.':
                break
            else:
                cons_list.append(c)
        cons_list = ";".join(cons_list)

        review['TestPros'] = pros_list
        review['TestCons'] = cons_list

        # 'source_internal_id': ''
        # URL looks like: mobiltest.dk/anmeldelse/501/apple-iphone-x-test
        sid = response.url.split('anmeldelse/')[-1]
        sid = sid.split('/')[0]
        review['source_internal_id'] = sid

        # PRODUCT ITEM -----------------------------------------------------
        product = ProductItem()
        product['source_internal_id'] = review['source_internal_id']
        product['OriginalCategoryName'] = response.meta.get('cat')
        product['ProductName'] = review['ProductName']

        pic_url_xpath = '//div[@id="contentMain"]//img[1]/@src'
        pic_url = response.xpath(pic_url_xpath).get()
        product['PicURL'] = pic_url

        product['TestUrl'] = response.url
        # ------------------------------------------------------------------

        yield review
        yield product
