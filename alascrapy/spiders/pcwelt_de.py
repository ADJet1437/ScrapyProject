# -*- coding: utf8 -*-
from datetime import datetime

import calendar  # Used to find out what's the last day of a month.

from scrapy.http import Request
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem


class Pcwelt_deSpider(AlaSpider):
    name = 'pcwelt_de'
    allowed_domains = ['pcwelt.de']

    def __init__(self, *args, **kwargs):
        super(Pcwelt_deSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

        # Testing another date
        # self.stored_last_date = datetime(2019, 1, 27)
        # print "     --- stored_last_date: " + str(self.stored_last_date)

    def start_requests(self):
        # print "     ...START_REQUESTS"
        # print "     --- stored_last_date: " + str(self.stored_last_date)

        # This website uses dynamic data.
        # It has an /archive section which is guided by the dates.
        # We can check what were all the posts in each day, for every year.
        # We are going to scrape through that in order to avoid using selenium.
        #
        # This is how an URL looks like for that archive:
        #   https://www.pcwelt.de/archiv/tag/2019-01-28

        last_scraped_year = self.stored_last_date.year
        last_scraped_month = self.stored_last_date.month
        last_scraped_day = self.stored_last_date.day

        years_range = range(last_scraped_year, datetime.now().year+1)
        first_year_month_range = range(last_scraped_month, 13)

        # The last day of the month that the spider scraped the website
        month_last_day = calendar.monthrange(last_scraped_year,
                                             last_scraped_month)[1]

        first_month_day_range = range(last_scraped_day + 1, month_last_day + 1)

        # print "     --years range: " + str(years_range)
        # print "     --first year month range: " + str(first_year_month_range)
        # print "     --first month day range: " + str(first_month_day_range)

        # FIRST YEAR -------------------------------------------------------
        if len(years_range) > 0:
            year = years_range[0]
        else:
            year = datetime.now().year

        # First month
        month = first_year_month_range[0]

        for day in first_month_day_range:
            date = str(year)+"-"+str(month).zfill(2)+"-"+str(day).zfill(2)

            # Make sure we are not creating an URL for a date in the future
            if datetime.strptime(date, '%Y-%m-%d') < datetime.now():
                # print "     --date: " + date

                url_date = 'https://www.pcwelt.de/archiv/tag/' + date

                yield Request(url=url_date,
                              callback=self.parse,
                              meta={'date': date})

        # Other months
        for month in first_year_month_range[1:]:
            last_day_of_month = calendar.monthrange(year, month)[1]
            for day in range(1,  last_day_of_month + 1):
                date = str(year)+"-"+str(month).zfill(2)+"-"+str(day).zfill(2)

                # Make sure we are not creating an URL for a date in the future
                if datetime.strptime(date, '%Y-%m-%d') < datetime.now():
                    # print "     --date: " + date

                    url_date = 'https://www.pcwelt.de/archiv/tag/' + date

                    yield Request(url=url_date,
                                  callback=self.parse,
                                  meta={'date': date})
        # ------------------------------------------------------------------

        # REST OF THE YEARS ------------------------------------------------
        for year in years_range[1:]:
            for month in range(1, 13):
                last_day_of_month = calendar.monthrange(year, month)[1]
                for day in range(1,  last_day_of_month + 1):
                    date = str(year) + "-" + str(month).zfill(2) \
                                    + "-" + str(day).zfill(2)

                    # Make sure we are not creating an URL for a date in the
                    #  future
                    if datetime.strptime(date, '%Y-%m-%d') < datetime.now():
                        # print "     --date: " + date

                        url_date = 'https://www.pcwelt.de/archiv/tag/' + date

                        yield Request(url=url_date,
                                      callback=self.parse,
                                      meta={'date': date})
        # ------------------------------------------------------------------

    def parse(self, response):
        # print "     ...PARSE: " + response.url

        posts_xpath = '//ul[@class="info-list"]//li//div[@class="outer"]'
        posts = response.xpath(posts_xpath)

        post_type_xpath = './/span[@class="info-link"]//text()'

        for post in posts:
            post_type = post.xpath(post_type_xpath).get()

            if post_type == "Test":
                post_url = post.xpath('.//a//@href').get()

                yield Request(url=post_url,
                              callback=self.parse_review_product,
                              meta={'date': response.meta.get('date')})

    def get_product_name(self, response):
        # print "     ...GET_PRODUCT_NAME: " + response.url

        test_title_xpath = '//meta[@property="og:title"]'\
                           '/@content'

        product_name = response.xpath(test_title_xpath).get()

        words_to_remove = ['Im Test:',
                           'Test',
                           'im',
                           ':']

        for word in words_to_remove:
            product_name = product_name.replace(word, '')

        product_name = product_name.replace('  ', ' ')

        product_name = product_name.strip()

        '''
        # Second option. Doesn't work always.
        #
        # There are way too many exceptions. Exemple:
        # https://www.pcwelt.de/produkte/Sony-Xperia-1-Test-Ausstattung-Preis-Release-10538846.html
        xpath = '//div[@class="banner-left"]//div[@class="content"]'\
                '//div[@class="header"]//text()'

        product_name = response.xpath(xpath).get()

        if product_name:
            product_name = product_name.strip()

        # print " =============== " + str(product_name)
        '''

        ''' # Third option (doesn't work for all possibilities):
        # It doesn't work for this case, for example:
        #  https://www.pcwelt.de/produkte/Test-Die-besten-Smartwatches-9952038.html

        p_name_xpath = '//div[@class="table-holder linkdb-marker"]'\
                       '//tr[@class="even"]/th[2]/p'

        product_name = response.xpath(p_name_xpath)[0]
        product_name = product_name.xpath('.//text()').getall()

        product_name = ''.join(product_name)
        product_name = product_name.strip()

        print " =============== " + product_name '''

        return product_name

    def parse_review_product(self, response):
        # print "     ... PARSE_REVIEW_PRODUCT: " + response.url

        category_xpath = '//div[@class="breadcrumb"]/span[last()]/'\
                         'span[@property="itemListElement"]/a/span//text()'

        category = response.xpath(category_xpath).get()

        categories_to_scrape = ["Notebook",
                                "Monitor",
                                "Tablet",
                                "Smartphone",
                                "Audio & TV / Video"]

        if category in categories_to_scrape:
            # print "      ---> Scrape it! Category: " + category

            # REVIEW -----------------------------------------------------
            review_xpaths = {'TestTitle': '//meta[@property="og:title"]'
                                          '/@content',
                             'Author': '//meta[@name="author"]/@content',
                             'TestSummary': '//meta[@name="description"]'
                                            '/@content',
                             }

            review = self.init_item_by_xpaths(response, "review",
                                              review_xpaths)

            review['DBaseCategoryName'] = 'PRO'
            review['TestDateText'] = response.meta.get('date')

            # Product_id
            # There are typically 2 types of URL:
            # 1:  www. ... -10113167.html
            # 2:  www. ... ,10113167
            if response.url.endswith('.html'):
                p_id = response.url.split('.html')[0]
                p_id = p_id.split('-')[-1]

            else:
                p_id = response.url.split(',')[-1]

            review['source_internal_id'] = p_id

            # PROS and CONS
            paragraphs_xpath = '//div[@class=" visual inline-box '\
                               'linkdb-marker"]/p[@class="linkdb-marker"]'

            paragraphs = response.xpath(paragraphs_xpath)

            pros = cons = ''
            for paragraph in paragraphs:
                text = paragraph.xpath('.//text()').get()
                text = text.strip()
                if text.startswith('+'):
                    text = text.replace('+', '').strip()
                    pros = pros + text + ";"

                elif text.startswith('-'):
                    text = text.replace('-', '').strip()
                    cons = cons + text + ";"

            # removing the last ';'
            if pros:
                pros = pros[:-1]
            if cons:
                cons = cons[:-1]

            review['TestPros'] = pros
            review['TestCons'] = cons

            review['ProductName'] = self.get_product_name(response)
            # ------------------------------------------------------------

            # PRODUCT ---------------------------------------------
            product = ProductItem()
            product['source_internal_id'] = review['source_internal_id']
            product['OriginalCategoryName'] = category
            product['ProductName'] = review['ProductName']

            pic_url_xpath = '//meta[@property="ob:image"]/@content'
            pic_url = response.xpath(pic_url_xpath).get()
            product['PicURL'] = pic_url

            product['TestUrl'] = response.url
            # ------------------------------------------------------------

            yield review
            yield product
