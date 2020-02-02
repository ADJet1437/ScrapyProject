# -*- coding: utf8 -*-

from datetime import datetime

import json
import logging
from scrapy.http import Request
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.items import ProductItem, ProductIdItem, ReviewItem
import alascrapy.lib.dao.incremental_scraping as incremental_utils

logger = logging.getLogger(__name__)


class WhichSpider(AlaSpider):
    name = 'which_co_uk'
    allowed_domains = ['which.co.uk']

    username = 'K920483499'
    password = 'alascore2015'

    def __init__(self, *args, **kwargs):
        super(WhichSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

        # In order to test another stored_last_date
        # self.stored_last_date = datetime(2015, 2, 8)

    def start_requests(self):
        # print "     ...START_REQUESTS"

        cat_url = {'Television': 'https://www.which.co.uk/reviews/televisions',
                   'Desktop': 'https://www.which.co.uk/reviews/desktop-pcs',
                   'Tablet': 'https://www.which.co.uk/reviews/tablets',
                   'Laptop': 'https://www.which.co.uk/reviews/laptops',
                   'Printer': 'https://www.which.co.uk/reviews/printers-'
                              'and-ink',
                   'DSLR camera': 'https://www.which.co.uk/reviews/dslr-and-'
                                  'mirrorless-cameras',
                   'Action camera': 'https://www.which.co.uk/reviews/action-'
                                    'cameras',
                   'Bridge Camera': 'https://www.which.co.uk/reviews/bridge-'
                                    'cameras',
                   'Camcoder': 'https://www.which.co.uk/reviews/camcorders',
                   'Compact Camera': 'https://www.which.co.uk/reviews/compact-'
                                     'cameras',
                   'Headphones': 'https://www.which.co.uk/reviews/headphones',
                   'Simple Mobile Phones': 'https://www.which.co.uk/reviews/'
                                           'simple-mobile-phones',
                   'Smartphone': 'https://www.which.co.uk/reviews/mobile-'
                                 'phones',
                   'Drone': 'https://www.which.co.uk/reviews/drones',
                   'Washing Machines': 'https://www.which.co.uk/reviews'
                                       '/washing-machines',
                   'Dish Washers': 'https://www.which.co.uk/reviews'
                                   '/dishwashers'
                   }

        for cat in cat_url:
            yield Request(url=cat_url[cat],
                          callback=self.parse,
                          meta={'cat': cat})

    def get_date(self, date_str):
        # They don't put the days of the month.
        try:
            date = datetime.strptime(date_str, '%b %Y')
        except:
            # Sometimes they don't have the dates for the very old
            #  reviews. We don't scrape them in that case.
            date = None
        return date

    def parse(self, response):
        # print "     ...PARSE: " + response.url

        review_divs_xpath = '//li[@itemprop="itemListElement"]'
        review_divs = response.xpath(review_divs_xpath)

        for r_div in review_divs:
            date_xpath = './/p[@data-test-element="tested-date"]'\
                         '//text()[last()]'
            date = r_div.xpath(date_xpath).get()
            # The dates looks like this: Sep 2018.
            date = self.get_date(date)

            if date and (date > self.stored_last_date):
                review_url_xpath = './/a[1]/@href'
                review_url = r_div.xpath(review_url_xpath).get()
                review_url += '/review'

                cat = response.meta.get('cat')
                yield response.follow(url=review_url,
                                      callback=self.parse_product_review,
                                      meta={'date': date.strftime("%Y-%m-%d"),
                                            'cat': cat})

        # Checking whether we should scrape the next page
        date = review_divs[-1].xpath(date_xpath).get()
        date = self.get_date(date)
        if date:
            next_page_url_xpath = '//a[@rel="next"]/@href'
            next_page_url = response.xpath(next_page_url_xpath).get()
            if next_page_url:
                if date > self.stored_last_date:
                    cat = response.meta.get('cat')

                    yield Request(url=next_page_url,
                                  callback=self.parse,
                                  meta={'cat': cat})

    def parse_product_review(self, response):
        # print "     ...PARSE_PRODUCT_REVIEW: " + response.url

        # REVIEW ITEM ---------------------------------------------------------
        review_xpaths = {
            'TestTitle': '//title//text()',
            'TestVerdict': '//span[@data-test-element="headline-verdict"]'
                           '//text()',
            'TestSummary': '//meta[@name="description"]/@content',
        }

        # Create the review
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        # 'TestTitle'
        if '- Which?' in review['TestTitle']:
            review['TestTitle'] = review['TestTitle'].replace('- Which?', '')
            review['TestTitle'] = review['TestTitle'].strip()

        # 'TestSummary'
        if 'Product Review:' in review['TestSummary']:
            summary = review['TestSummary'].replace('Product Review:', '')
            summary = summary.strip()
            review['TestSummary'] = summary

        # 'ProductName'
        js_xpath = '//script[@type="application/ld+json"][2]//text()'
        js = response.xpath(js_xpath).get()
        js = json.loads(js)
        review['ProductName'] = js["name"]

        # 'Author'
        author = js['model']['Review']['author']
        if not author == 'Which?':
            review['Author'] = author
        # 'TestDateText'
        review['TestDateText'] = response.meta.get('date')

        ''' This is only available if you are logged in.
        # 'SourceTestScale' SourceTestRating'
        rating_xpath = '//span[@data-test-element="score"]//text()'
        rating = response.xpath(rating_xpath)

        if rating:
            review['SourceTestRating'] = rating
            review['SourceTestScale'] = 100
        '''

        # 'DBaseCategoryName'
        review['DBaseCategoryName'] = 'PRO'

        # 'TestPros' 'TestCons' -----------------------------------------------
        '''
        js2_xpath = '//div[@data-react-class="product-pages/components/'\
                    'product-page"]/@data-react-props'
        js2 = response.xpath(js2_xpath).get()
        js2 = json.loads(js2)
        print js2
        '''
        # pros and cons
        # pros_xpath = '//div[@class="pros__text _UD8t"]//span//text()'
        # pros = response.xpath(pros_xpath).getall()
        # pros = pros.split(',')
        # print pros

        '''
        f = open('HTML.txt', 'w')
        f.write(response.url)
        f.write(" ")
        f.write(response.body)
        f.close()
        # When we analyze the HTML the spider sees, there's no PROS/CONS there
        '''
        # ---------------------------------------------------------------------

        # 'source_internal_id'
        sid = response.url.split('/')[-2]
        review['source_internal_id'] = sid
        # ---------------------------------------------------------------------

        # PRODUCT ITEM --------------------------------------------------------
        product = ProductItem()
        product['source_internal_id'] = review['source_internal_id']
        product['OriginalCategoryName'] = response.meta.get('cat')
        product['ProductName'] = review['ProductName']

        pic_url_xpath = '//div[@data-test-element="product-gallery"]/img/@src'
        pic_url = response.xpath(pic_url_xpath).get()
        product['PicURL'] = pic_url

        product['TestUrl'] = response.url
        # ---------------------------------------------------------------------

        # Some products have a price
        price_xpath = '//span[@data-test-element="price"]//text()'
        price = response.xpath(price_xpath).get()
        if price:
            yield ProductIdItem.from_product(product,
                                             kind='price',
                                             value=price
                                             )
        yield review
        yield product
