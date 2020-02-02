# -*- coding: utf8 -*-

from scrapy.http import Request
from datetime import datetime
import json

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.items import ProductItem, ReviewItem
import alascrapy.lib.dao.incremental_scraping as incremental_utils


class PhoneArenaSpider(AlaSpider):
    name = 'phonearena_com'
    allowed_domains = ['phonearena.com']

    def __init__(self, *args, **kwargs):
        super(PhoneArenaSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

        # In order to test another stored_last_date
        # self.stored_last_date = datetime(2018, 2, 8)

    def start_requests(self):
        # There are 4 categories to scrape in this website:
        #   smartphones, tablets, smartwatches, and headphones

        cat_dict = {'android_smartphone': 'https://www.phonearena.com/reviews'
                                          '/OS/Android%20phones/page/1',
                    'windows_smartphone': 'https://www.phonearena.com/reviews'
                                          '/OS/Windows%20phones/page/1',
                    'android_tablet': 'https://www.phonearena.com/reviews/OS'
                                      '/Android%20tablets/page/1',
                    'windows_tablet': 'https://www.phonearena.com/reviews/OS'
                                      '/Windows+tablets',
                    'smartwatch_and_earbuds': 'https://www.phonearena.com'
                                              '/reviews/page/1'
                    }

        for category in cat_dict:
            yield Request(url=cat_dict[category],
                          callback=self.parse,
                          meta={'category': category})

    def parse(self, response):
        # print "     ...PARSE: " + response.url

        review_divs_xpath = '//div[@class="col-xs-12 mid-half-size '\
                            'single-review-container"]'
        review_divs = response.xpath(review_divs_xpath)

        date = None
        for r_div in review_divs:
            date_xpath = './/span[@class="timestamp"]/@title'
            date = r_div.xpath(date_xpath).get()

            if date:
                # date looks like 'title="Thu, 28 Mar 2019 01:28:00 -0500'
                date = date.split(',')[-1]
                date = date.split('-')[0]
                date = date.strip()
                date = datetime.strptime(date, '%d %b %Y %H:%M:%S')
            else:
                date_xpath = './/span[@class="ago"]//text()'
                date = r_div.xpath(date_xpath).get()
                date = datetime.strptime(date, '%b %d, %Y, %I:%M %p,')

            if date > self.stored_last_date:
                review_url_xpath = './/a/@href'
                review_url = r_div.xpath(review_url_xpath).get()

                category = response.meta.get('category')
                yield response.follow(url=review_url,
                                      callback=self.parse_product_review,
                                      meta={'date': date.strftime("%Y-%m-%d"),
                                            'category': category})

        # Checking whether we should load more reviews (next page)
        if date and date > self.stored_last_date:
            current_page_number = response.url.split('/')[-1]
            next_page_number = int(current_page_number) + 1

            next_page_url = 'https://www.phonearena.com/reviews/page/{}'
            next_page_url = next_page_url.format(next_page_number)

            category = response.meta.get('category')
            yield Request(url=next_page_url,
                          callback=self.parse,
                          meta={'category': category})

    def parse_product_review(self, response):
        # print "     ...PARSE_PRODUCT_REVIEW: " + response.url

        category = response.meta.get('category')

        if category == 'android_smartphone' or \
           category == 'windows_smartphone':
            category = 'Smartphone'
        elif category == 'android_tablet' or category == 'windows_tablet':
            category = 'Tablet'
        elif category == 'smartwatch_and_earbuds':
            # This website is tricky on their category classification.
            # We are classifying based on the tags and description
            # Smartwatch -> 'watch' or 'smartwatch' in the title
            # Headphone -> tag = Accessories  and 'earphones' 'earbuds'
            # 'headphones' in the property="og:description"

            tags_xpath = '//div[@class="tags clearfix"]//span//text()'
            tags = response.xpath(tags_xpath).getall()

            description_xpath = '//meta[@property="og:description"]/@content'
            description = response.xpath(description_xpath).get()
            description = description.split(' ')
            description = [word.lower() for word in description]
            description = set(description)

            headphones_key_words = ['headphones', 'earbuds']
            headphones_key_words = set(headphones_key_words)

            smartwatch_key_words = ['smartwatch', 'smart']
            smartwatch_key_words = set(smartwatch_key_words)
            # Headphones -----------------------------------------------------
            if ('Accessories' in tags) and \
               (len(headphones_key_words.intersection(description)) > 0):
                category = "Headphones"

            # Smartwatch -----------------------------------------------------
            elif len(smartwatch_key_words.intersection(description)) > 0:
                category = "Smartwatch"

            # Something else -------------------------------------------------
            else:
                category = None

        # Excluding comparison reviews
        test_t = response.xpath('//meta[@property="og:title"]/@content').get()
        test_t = test_t.lower()
        test_t = test_t.split(' ')
        if 'vs' in test_t:
            category = None

        if category:
            # REVIEW ITEM ----------------------------------------------------
            review_xpaths = {
                'TestTitle': '//meta[@property="og:title"]/@content',
                'Author': '//meta[@name="author"]/@content',
                'TestSummary': '//meta[@property="og:description"]/@content',
            }

            # Create the review
            review = self.init_item_by_xpaths(response, "review",
                                              review_xpaths)

            # 'ProductName'
            words_to_remove = ['Review',
                               'review']
            product_name = review['TestTitle']
            for word in words_to_remove:
                product_name = product_name.replace(word, '')
            product_name = product_name.strip()
            review['ProductName'] = product_name

            # 'TestDateText'
            review['TestDateText'] = response.meta.get('date')

            # 'SourceTestScale' 'SourceTestRating'
            js_xpath = '//script[@type="application/ld+json"]//text()'
            js = response.xpath(js_xpath).get()
            js = json.loads(js)

            try:
                review['SourceTestRating'] = js["reviewRating"]["ratingValue"]
                if review['SourceTestRating']:
                    review['SourceTestScale'] = 10
            except:
                pass

            # 'DBaseCategoryName'
            review['DBaseCategoryName'] = 'PRO'

            # 'TestPros' and 'TestCons'
            pros_xpath = '//ul[@class="pros block"]//li//text()'
            pros = response.xpath(pros_xpath).getall()
            pros = ";".join(pros)
            review['TestPros'] = pros

            cons_xpath = '//ul[@class="cons block"]//li//text()'
            cons = response.xpath(cons_xpath).getall()
            cons = ";".join(cons)
            review['TestCons'] = cons

            # 'source_internal_id'
            sid = response.url.split('id')[-1]
            review['source_internal_id'] = sid
            # ----------------------------------------------------------------

            # PRODUCT ITEM ---------------------------------------------------
            product = ProductItem()
            product['source_internal_id'] = review['source_internal_id']
            product['OriginalCategoryName'] = category
            product['ProductName'] = review['ProductName']

            pic_url_xpath = '//meta[@property="og:image"]/@content'
            pic_url = response.xpath(pic_url_xpath).get()
            product['PicURL'] = pic_url

            product['TestUrl'] = response.url
            # ----------------------------------------------------------------

            yield review
            yield product
