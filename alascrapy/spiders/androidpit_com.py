# -*- coding: utf8 -*-

from datetime import datetime
import json
from scrapy.http import Request
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem


class Androidpit_comSpider(AlaSpider):
    name = 'androidpit_com'
    allowed_domains = ['androidpit.com']

    def __init__(self, *args, **kwargs):
        super(Androidpit_comSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

        # In order to test another stored_last_date
        # self.stored_last_date = datetime(2018, 1, 8)

    def start_requests(self):
        # print "     ...START_REQUESTS"

        base_url = 'https://www.androidpit.com/hardware-reviews'
        category_url_dict = {'Smartphone': base_url + '/smartphones',
                             'Tablet': base_url + '/tablets',
                             'other': base_url + '/other-devices'
                             }

        for category in category_url_dict:
            yield Request(url=category_url_dict[category],
                          callback=self.parse,
                          meta={'category': category})

    def parse(self, response):
        # print "     ...PARSE: " + response.url

        review_divs_xpath = '//div[@class="articleTeaserContent"]'
        review_divs = response.xpath(review_divs_xpath)

        date = None
        for r_div in review_divs:
            date_xpath = './/span[@class="articleTeaserTimestamp"]//@title'
            date = r_div.xpath(date_xpath).get()
            # date looks like this: Nov 15, 2014, 9:00:00 PM
            date = datetime.strptime(date, '%b %d, %Y, %H:%M:%S %p')

            if date > self.stored_last_date:
                review_url_xpath = './h2/a/@href'
                review_url = r_div.xpath(review_url_xpath).get()

                product_name_xpath = './/a[@class="ameta__label '\
                                     'ameta__label--link"]//text()'

                category = response.meta.get('category')
                yield response.follow(url=review_url,
                                      callback=self.parse_product_review,
                                      meta={'category': category,
                                            'date': date.strftime("%Y-%m-%d")})

        # Checking whether we should scrape the next page.
        next_button_xpath = '//a[@class="arrow"][text()="»"]/'\
                            '@href'.decode('utf-8')
        next_button = response.xpath(next_button_xpath).get()

        # In case we have a 'next page' button
        if next_button:
            # date already contains the last date of the last review.
            if date > self.stored_last_date:
                category = response.meta.get('category')
                yield response.follow(url=next_button,
                                      callback=self.parse,
                                      meta={'category': category})

    def is_review_of_this_category(self, review_title, key_words):
        for w in key_words:
            if w.lower() in review_title.lower():
                return True
        return False

    def parse_product_review(self, response):
        # print "     ...PARSE_PRODUCT_REVIEW: " + response.url

        category = None
        if response.meta.get('category') == 'other':
            test_title_xpath = '//meta[@property="og:title"]/@content'
            test_title = response.xpath(test_title_xpath).get()

            categoryIdentified = False

            # Checking whether the review is for a smartwatch
            smartwatch_keywords = ['watch',
                                   'smartwatch',
                                   'Ticwatch']

            if self.is_review_of_this_category(test_title,
                                               smartwatch_keywords):
                category = 'Smartwatch'
                categoryIdentified = True

            # Checking whether the review is for headphones
            headphone_keywords = ['headphone',
                                  'headset']

            if not categoryIdentified and self.is_review_of_this_category(
                                          test_title, headphone_keywords):
                category = 'Headphone'
                categoryIdentified = True

            # Checking whether the review is for notebook
            laptop_keywords = ['chromebook',
                               'laptop',
                               'notebook']

            if not categoryIdentified and self.is_review_of_this_category(
                                          test_title, laptop_keywords):
                category = 'Notebook'
                categoryIdentified = True
        else:
            category = response.meta.get('category')

        categories_to_scrape = ['Smartphone',
                                'Tablet',
                                'Smartwatch',
                                'Headphone',
                                'Notebook']

        if category in categories_to_scrape:

            # REVIEW ITEM ----------------------------------------------------
            review_xpaths = {
                'TestTitle': '//meta[@property="og:title"]/@content',
                'Author': '//span[@class="articleAuthorName"]/span//text()',
                'TestSummary': '//meta[@property="og:description"]/@content',
            }

            review = self.init_item_by_xpaths(response, "review",
                                              review_xpaths)

            # 'ProductName'
            js_xpath = '//script[@type="application/ld+json"][last()]//text()'
            js = response.xpath(js_xpath).get()
            js = json.loads(js)
            review['ProductName'] = js["itemReviewed"]["name"]

            # 'TestDateText'
            review['TestDateText'] = response.meta.get('date')

            # 'TestVerdict'
            verdict_xpath = '//div[@class="finalVerdictDesc"]//text()'
            verdict = response.xpath(verdict_xpath).getall()
            if verdict:
                verdict = " ".join(verdict)
                verdict = verdict.replace('  ', ' ')
                review['TestVerdict'] = verdict

            # 'DBaseCategoryName'
            review['DBaseCategoryName'] = 'PRO'

            # 'source_internal_id'
            sid = response.url.split('/')[-1].replace('-review', '')
            sid = sid.strip()
            review['source_internal_id'] = sid
            # ---------------------------------------------------------------------

            # PRODUCT ITEM ----------------------------------------------------
            product = ProductItem()
            product['source_internal_id'] = review['source_internal_id']
            product['OriginalCategoryName'] = category
            product['ProductName'] = review['ProductName']

            pic_url_xpath = '//meta[@property="og:image"]/@content'
            pic_url = response.xpath(pic_url_xpath).get()
            product['PicURL'] = pic_url

            product['TestUrl'] = response.url
            # -----------------------------------------------------------------

            yield review
            yield product
