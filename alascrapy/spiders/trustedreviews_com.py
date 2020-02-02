# -*- coding: utf8 -*-

from datetime import datetime
from scrapy.http import Request
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem


class TrustedReviewsSpider(AlaSpider):
    name = 'trustedreviews_com'
    allowed_domains = ['trustedreviews.com']

    def __init__(self, *args, **kwargs):
        super(TrustedReviewsSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

        # In order to test another stored_last_date
        # self.stored_last_date = datetime(2010, 2, 8)

    def start_requests(self):
        # print " 	...START_REQUESTS: "

        base_url = 'https://www.trustedreviews.com/reviews'
        url_cat_dict = {'Desktop PC': base_url + '?product_type='
                        'desktop-pcs&brands=&rating=&s=',

                        'Laptop': base_url + '?product_type=laptops'
                        '&brands=&rating=&s=',

                        'Printer': base_url + '?product_type=printers'
                        '&brands=&rating=&s=',

                        'Smartphone': base_url + '?product_type=mobile'
                        '-phones&brands=&rating=&s=',

                        'Tablet': base_url + '?product_type=tablets&brands'
                        '=&rating=&s=',

                        'Camera': base_url + '?product_type=digital-cameras'
                        '&brands=&rating=&s='
                        }

        for cat in url_cat_dict:
            yield Request(url=url_cat_dict[cat],
                          callback=self.parse,
                          meta={'cat': cat})

    def parse(self, response):
        # print " 	...PARSE: " + response.url
        # print " --self.stored_last_date: " + str(self.stored_last_date)

        review_lis_xpath = '//section[@class="s-container s-container--'\
                           'inc-sidebar listing--single-inc-sidebar '\
                           'image-aspect-landscape "]//ul[@class="'\
                           'listing-items"]/li'

        review_lis = response.xpath(review_lis_xpath)

        date = None
        for r_li in review_lis:
            date_xpath = './/span[@class="date entry-date details"]//text()'
            date = r_li.xpath(date_xpath).get()
            # date looks like: "June 26, 2019 4:02 pm BST"
            date = date.split(' ')[:-3]
            date = ' '.join(date)
            # date now looks like: "February 13, 2019"
            date = datetime.strptime(date, '%B %d, %Y')

            if date > self.stored_last_date:
                review_url_xpath = './a/@href'
                review_url = r_li.xpath(review_url_xpath).get()

                yield Request(url=review_url,
                              callback=self.parse_product_review,
                              meta={'cat': response.meta.get('cat'),
                                    'date': date.strftime("%Y-%m-%d")})

        # Checking whether we should scrape the next page
        if date and date > self.stored_last_date:
            next_page_url_xpath = '//a[@class="nextpostslink"]/@href'
            next_page_url = response.xpath(next_page_url_xpath).get()

            yield Request(url=next_page_url,
                          callback=self.parse,
                          meta={'cat': response.meta.get('cat')})

    def parse_product_review(self, response):
        # print "     ...PARSE_PRODUCT_REVIEW: " + response.url

        # REVIEW ----------------------------------------------------------
        review_xpaths = {
            'TestTitle': '//meta[@property="og:title"]/@content',
            'Author': '(//span[@class="author vcard"])[1]/text()',
            'TestSummary': '//meta[@property="og:description"]/@content'
        }

        # Create the review
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        # 'ProductName'
        header = self.extract(response.xpath("//h1[@class='title-primary']/text()"))
        review['ProductName'] = header.replace(" Review", "").replace(" review", "")

        # 'TestDateText'
        review['TestDateText'] = response.meta.get('date')

        # 'DBaseCategoryName'
        review['DBaseCategoryName'] = 'PRO'

        # 'TestPros'    'TestCons'
        pros_xpath = '//div[@class="review-points__pros"]//li/'\
                     'span[@class="point"]/text()'
        pros = response.xpath(pros_xpath).getall()
        pros = ";".join(pros)

        cons_xpath = '//div[@class="review-points__cons"]//li/'\
                     'span[@class="point"]/text()'
        cons = response.xpath(cons_xpath).getall()
        cons = ";".join(cons)

        if pros and cons:
            review['TestPros'] = pros
            review['TestCons'] = cons

        # 'source_internal_id'
        review['source_internal_id'] = response.url.split('/')[-1]
        # ---------------------------------------------------------------------

        # PRODUCT -------------------------------------------------------------
        product = ProductItem()
        product['source_internal_id'] = review['source_internal_id']
        product['OriginalCategoryName'] = response.meta.get('cat')
        product['ProductName'] = review['ProductName']

        pic_url_xpath = '(//meta[@property="og:image"])[1]/@content'
        pic_url = response.xpath(pic_url_xpath).get()
        product['PicURL'] = pic_url

        product['TestUrl'] = response.url
        # ---------------------------------------------------------------------

        yield review
        yield product
