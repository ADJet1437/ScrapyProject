
# -*- coding: utf8 -*-

from datetime import datetime
import dateparser

# we need to set the locale to german in order
# to convert german dates into datetime.
import locale

from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem

import re


class Androidmag_deSpider(AlaSpider):
    name = 'androidmag_de'
    allowed_domains = ['androidmag.de']
    page_number = 1
    base_url = 'https://androidmag.de/tag/test/page/{}'
    start_urls = ['https://androidmag.de/tag/test/']

    def __init__(self, *args, **kwargs):
        super(Androidmag_deSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

        # In order to test another stored_last_date
        # self.stored_last_date = datetime(2018, 2, 3)

        # locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')

    def parse(self, response):
        # print "     ...PARSE: " + response.url

        review_divs_xpath = '//div[contains(@class, "block-item-big")]'
        review_divs = response.xpath(review_divs_xpath)

        for review_div in review_divs:
            # Let's check the date
            date_xpath = './/span[@class="heading-date"]/text()'
            date = review_div.xpath(date_xpath).get()

            # Date looks like this: 15. März 2019
            date = dateparser.parse(date, date_formats=['%d. %m %Y'],
                                    languages=['de', 'es'])

            # If it's a new review.
            if date > self.stored_last_date:

                classes = review_div.xpath('./@class').get()
                classes = classes.split(' ')

                ''' Very tricky to get the categories of the products. The
                    review's page don't have any specific categorization
                    method (smartphones/tablets...). The way we are making
                    sure we get the right products is through some tags they
                    include in the classes attribute of the divs. However,
                    they are not consistent withe the tag classification. Some
                    tablets are tagged as 'tag-smartphone', some are tagged as
                    both. Even worse than that, they have typos in the tags,
                    for example, some smartphones are tagged as
                    'tag-samartphone'. We are trying to include all exceptions.
                    If you find a better way of identifying the categories,
                    that would be very much appreciated. '''

                tags_to_scrape = ['tag-tablet',
                                  'tag-ipad',
                                  'tag-smartphone',
                                  'tag-samartphone',  # They have some typos.
                                  'tag-in-ear',
                                  'tag-kopfhorer']

                tags_to_skip = ['tag-handyhulle',
                                'tag-powerbank',
                                'tag-watch-band']

                for c in classes:
                    if c in tags_to_skip:
                        # print " let's skip this because of: " + c
                        break

                    if c in tags_to_scrape:
                        # print " let's scrape this because of: " + c
                        review_url_xpath = './/div[@class="block-image"]'\
                                           '/a/@href'

                        review_url = review_div.xpath(review_url_xpath).get()

                        # Get author name to pass as meta value
                        author_xpath = './/span[@class="heading-author"]'\
                                       '//text()'
                        author = review_div.xpath(author_xpath).get()

                        # Formating the date to pass to 'parse_review_product'
                        meta_date = date.strftime("%Y-%m-%d")

                        yield Request(url=review_url,
                                      callback=self.parse_review_product,
                                      meta={'author': author,
                                            'date': meta_date})
                        break

        # NEXT PAGE -----------------------------------------------------------
        # Check the date of the last review in the page
        date_xpath = './/span[@class="heading-date"]/text()'
        date = review_divs[-1].xpath(date_xpath).get()
        # Date looks like this: 15. März 2019
        date = dateparser.parse(date, date_formats=['%d. %m %Y'],
                                languages=['de', 'es'])
        # print "     --> Last Review Date: " + str(date)

        # If last review in the page is new
        if date > self.stored_last_date:
            next_page_url_xpath = '//div[@class="pagination"] /'\
                                  'a[text()="Nächste "]/@href'.decode('utf-8')
            next_page_url = response.xpath(next_page_url_xpath).get()

            # In case there's a next page button, it means we have another
            #  page to scrape
            if next_page_url:
                yield Request(url=next_page_url,
                              callback=self.parse)
        # -----------------------------------------------------------------------

    def parse_review_product(self, response):
        # print "     ...PARSE_REVIEW_PRODUCT " + response.url

        review_xpaths = {
            'TestTitle': '//meta[@property="og:title"]/@content',
            'TestSummary': '//meta[@property="og:description"]/@content',
        }

        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        review['Author'] = response.meta.get('author')

        # RATING -------------------------------------------------------------
        # They change quite a lot the way they tag the 'ratings' and add no
        #  clear classes for that.
        rating = ''

        try:
            rating_xpath = '//div[@class="post-entry"]//h2[last()]//text()'
            rating_list = response.xpath(rating_xpath).getall()

            if len(rating_list) > 0:
                last_string = rating_list[-1].encode('utf-8')
                if "%" in last_string:
                    rating = re.sub("[^0-9]", "", last_string)
        except:
            pass

        if not rating:
            try:
                rating_xpath = '//div[@class="post-entry"]//h3//text()'
                rating_list = response.xpath(rating_xpath).getall()

                for r in rating_list:
                    r_e = r.encode('utf-8')
                    if "%" in r_e:
                        rating = re.sub("[^0-9]", "", r_e)
                        break
            except:
                pass

        if not rating:
            try:
                rating_xpath = '//div[@class="post-entry"]//h4//text()'
                rating_list = response.xpath(rating_xpath).getall()

                for r in rating_list:
                    r_e = r.encode('utf-8')
                    if "%" in r_e:
                        rating = re.sub("[^0-9]", "", r_e)
                        break
            except:
                pass

        if rating:
            review['SourceTestRating'] = rating
            review['SourceTestScale'] = 100
        else:
            review['SourceTestRating'] = None
            review['SourceTestScale'] = None
        # --------------------------------------------------------------------

        # PRODUCT NAME -------------------------------------------------------
        product_name = review['TestTitle'].encode('utf-8')

        words_to_remove = ['Das',
                           'Das neue',
                           'im Test',
                           'Im Test:',
                           'Test',
                           'im Check',
                           'Wir haben das neue',
                           ': Mehr sehen, mehr erleben!',
                           'neue'
                           ]

        for word in words_to_remove:
            if word in product_name:
                product_name = product_name.replace(word, "")

        product_name = product_name.replace('  ', ' ')
        product_name = product_name.strip()

        review['ProductName'] = product_name
        # --------------------------------------------------------------------

        # Source Internal ID -----------------------------------
        body_classes_xpath = '//body[1]/@class'
        body_classes = response.xpath(body_classes_xpath).get()
        body_classes = body_classes.split(' ')

        for c in body_classes:
            if c.startswith('postid'):
                id = c.split('-')[1]

                review['source_internal_id'] = id
        # ------------------------------------------------------

        review['DBaseCategoryName'] = 'PRO'
        review['TestDateText'] = response.meta.get('date')

        # PRODUCT ITEM
        product = ProductItem()
        product['source_internal_id'] = review['source_internal_id']

        # The categories in the website don't follow a great logic.
        # They don't have any specific categorization method
        #  (smartphones/tablets...).
        # They are not consistent with the tag classification. Some
        #  tablets are tagged as 'tag-smartphone', some are tagged
        #   as both. Even worse than that, they have typos in the tags,
        #   for example, some smartphones are tagged as 'tag-samartphone'.
        product['OriginalCategoryName'] = None

        product['ProductName'] = review['ProductName']

        product['PicURL'] = response.xpath('//meta[@property="og:image"]'
                                           '/@content').get()
        product['TestUrl'] = response.url

        yield review
        yield product
