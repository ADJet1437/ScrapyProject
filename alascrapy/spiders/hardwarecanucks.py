# -*- coding: utf8 -*-

from datetime import datetime
from scrapy.http import Request
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem


class HardwarecanucksSpider(AlaSpider):
    name = 'hardwarecanucks'
    allowed_domains = ['hardwarecanucks.com']

    def __init__(self, *args, **kwargs):
        super(HardwarecanucksSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

        # In order to test another stored_last_date
        # self.stored_last_date = datetime(2000, 2, 8)

    def start_requests(self):
        # print " 	...START_REQUESTS: "

        base_url = 'https://www.hardwarecanucks.com/content/reviews'
        url_cat_dict = {'Headphone': base_url + '/audio/',
                        'CPU cooler': base_url + '/cooling/',
                        'Monitor': base_url + '/displays/',
                        'Notebook_smartphone': base_url + '/mobile-reviews/'
                        }

        for cat in url_cat_dict:
            yield Request(url=url_cat_dict[cat],
                          callback=self.parse,
                          meta={'cat': cat})

    def parse(self, response):
        # print " 	...PARSE: " + response.url
        # print " --self.stored_last_date: " + str(self.stored_last_date)

        review_divs_xpath = '//div[@class="subbox subbox2"]'
        review_divs = response.xpath(review_divs_xpath)

        date = None
        for r_div in review_divs:
            date_xpath = './/small//text()'
            date = r_div.xpath(date_xpath).get()
            # date looks like: April 26th, 2017
            to_remove = ['th', 'rd', 'nd', 'st']
            for w in to_remove:
                date = date.replace(w, '')

            if 'Augu' in date:
                date = date.replace('Augu', 'August')

            date = datetime.strptime(date, '%B %d, %Y')

            if date > self.stored_last_date:
                # source id
                sid_xpath = './/div[@class="entry"]/@id'
                sid = r_div.xpath(sid_xpath).get()
                sid = sid.replace('post-', '')

                # image
                img_xpath = './/img/@src'
                img = r_div.xpath(img_xpath).get()

                url_xpath = './/h2[@class="listing"]/a/@href'
                url = r_div.xpath(url_xpath).get()

                yield Request(url=url,
                              callback=self.parse_product_review,
                              meta={'cat': response.meta.get('cat'),
                                    'sid': sid,
                                    'date': date.strftime("%Y-%m-%d"),
                                    'img': img})

        # Check whether we should scrape the next page
        if date > self.stored_last_date:
            next_page_url_xpath = '//a[@class="nextpostslink"]/@href'
            next_page_url = response.xpath(next_page_url_xpath).get()

            if next_page_url:
                yield Request(url=next_page_url,
                              callback=self.parse,
                              meta={'cat': response.meta.get('cat')})

    def get_product_name_based_on_title(self, title):
        ''' This function will 'clean' the title of the review
            in order to get the product name '''
        p_name = title

        # Removing certain words
        words_to_remove = [': Cases and Coolers',
                           'CPU Cooler ',
                           'Coolers',
                           'Cooler',
                           'Gaming Headset Review',
                           'Headphones Review',
                           'Headset Review',
                           'Headsets Review',
                           'Gaming Monitor',
                           'Professional Monitor Review',
                           'Curved Monitor Review',
                           'Monitor',
                           'Review',
                           'A Week With',
                           'Gaming Notebook',
                           'Notebook',
                           'Smartphone',
                           'Tablet',
                           'Ultrabook',
                           'Preview',
                           'The ']

        for w in words_to_remove:
            if w in title:
                p_name = p_name.replace(w, '')

        # Removing unnecessary spaces:
        p_name = p_name.replace('  ', ' ')
        p_name = p_name.strip()

        return p_name

    def parse_product_review(self, response):
        # print "     ...PARSE_PRODUCT_REVIEW: " + response.url

        # Filtering the reviews
        cat = response.meta.get('cat')
        test_title_xpath = '//td[@class="reviewpage_header1"]//h1//text()'
        test_title = response.xpath(test_title_xpath).get()

        if cat == 'Headphone':
            key_words = ['Headsets', 'Headphones', 'Headset']
            is_a_headphone = False
            for w in key_words:
                if w in test_title:
                    is_a_headphone = True

            if not is_a_headphone:
                return
        elif cat == 'Notebook_smartphone':
            if 'Battle' in test_title:
                return

            valid_category = False

            laptop_key_words = ['Laptop',
                                'Notebook',
                                'Notebooks',
                                'Chromebook',
                                'Ultrabook',
                                'Sleekbook']

            for w in laptop_key_words:
                if w in test_title:
                    cat = 'Laptop'
                    valid_category = True
                    break

            if 'Tablet' in test_title:
                cat = 'Tablet'
                valid_category = True

            smartphone_key_words = ['Smartphone',
                                    'Samsung Galaxy']
            for w in smartphone_key_words:
                if w in test_title:
                    cat = 'Smartphone'
                    valid_category = True
                    break

            if not valid_category:
                return

        # REVIEW ITEM ---------------------------------------------------------
        review_xpaths = {
            'Author': '(//strong[text()="Author:"]/following::text())[1]',
            'TestSummary': '//meta[@name="description"]/@content',
        }

        # Create the review
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        # 'TestTitle'
        review['TestTitle'] = test_title

        # 'ProductName'
        title = review['TestTitle']
        review['ProductName'] = self.get_product_name_based_on_title(title)

        # 'TestDateText'
        review['TestDateText'] = response.meta.get('date')

        # 'SourceTestScale' and 'SourceTestRating'
        review['SourceTestScale'] = None
        review['SourceTestRating'] = None

        # 'DBaseCategoryName'
        review['DBaseCategoryName'] = 'PRO'

        # 'TestPros' and 'TestCons'
        review['TestPros'] = None
        review['TestCons'] = None

        # 'source_internal_id'
        review['source_internal_id'] = response.meta.get('sid')
        # ---------------------------------------------------------------------

        # PRODUCT ITEM --------------------------------------------------------
        product = ProductItem()
        product['source_internal_id'] = review['source_internal_id']
        product['OriginalCategoryName'] = cat
        product['ProductName'] = review['ProductName']
        product['PicURL'] = response.meta.get('img')
        product['TestUrl'] = response.url
        # ---------------------------------------------------------------------

        yield review
        yield product
