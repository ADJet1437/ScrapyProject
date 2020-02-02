# -*- coding: utf8 -*-
from datetime import datetime

from scrapy.http import Request

from alascrapy.spiders.base_spiders import ala_spider as spiders
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem


class HifiChoiceUkSpider(spiders.AlaSpider):
    name = 'hifichoice_uk'
    allowed_domains = ['hifichoice.co.uk',
                       'hifichoicemag.com']

    def __init__(self, *args, **kwargs):
        super(HifiChoiceUkSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

        # In order to test another stored_last_date
        # self.stored_last_date = datetime(2000, 2, 8)

    def start_requests(self):
        # print "     ...START_REQUESTS"

        categories_to_scrape = {
            'headphone': 'https://www.hifichoicemag.com/category/headphones'
        }

        for category in categories_to_scrape:
            yield Request(url=categories_to_scrape[category],
                          callback=self.parse,
                          meta={'category': category})

    def parse(self, response):
        # print "     ...PARSE: " + response.url

        reviews_div_xpath = '//div[contains(@class,"views-row")]'
        reviews_div = response.xpath(reviews_div_xpath)

        # Checking date for each review.
        for r_div in reviews_div:
            date_xpath = './span[@class="views-field views-field-created"]'\
                         '//span//text()'
            date = r_div.xpath(date_xpath).get()
            # date looks like this: Feb 04, 2019
            date = datetime.strptime(date, '%b %d, %Y')

            if date > self.stored_last_date:
                review_url_xpath = './/div[@class="views-field views-field-'\
                                   'title"]//span//a/@href'

                review_url = r_div.xpath(review_url_xpath).get()

                category = response.meta.get('category')
                # Converting back to string in order to pass it as a meta value
                date = date.strftime("%Y-%m-%d")
                yield response.follow(url=review_url,
                                      callback=self.parse_product_review,
                                      meta={'category': category,
                                            'date': date})

        # Checking whether we should scrape the next page
        next_page_url_xpath = '//li[@class="pager-next"]//a/@href'
        next_page_url = response.xpath(next_page_url_xpath).get()

        # In case we have a 'next' button.
        if next_page_url:
            # Check the date of the last post
            date_xpath = './span[@class="views-field views-field-created"]'\
                          '//span//text()'
            date = reviews_div[-1].xpath(date_xpath).get()
            # date looks like this: Feb 04, 2019
            date = datetime.strptime(date, '%b %d, %Y')
            if date > self.stored_last_date:
                category = response.meta.get('category')
                yield response.follow(url=next_page_url,
                                      callback=self.parse,
                                      meta={'category': category})

    def parse_product_review(self, response):
        # print "     ...PARSE_PRODUCT_REVIEW: " + response.url

        # REVIEW --------------------------------------------------------------
        review_xpaths = {
            'TestTitle': '//meta[@property="og:title"]/@content',
            'ProductName': '//meta[@itemprop="name"]/@content',
            'TestSummary': '//meta[@name="description"]/@content'
        }

        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        # 'source_internal_id': ''
        shortlink = response.xpath('//link[@rel="shortlink"]/@href').get()
        # short link looks like this: https://www.hifichoicemag.com/node/144763
        review['source_internal_id'] = shortlink.split('/')[-1]

        # 'TestDateText'
        review['TestDateText'] = response.meta.get('date')

        # 'DBaseCategoryName'
        review['DBaseCategoryName'] = 'PRO'
        # ---------------------------------------------------------------------

        # PRODUCT -------------------------------------------------------------
        product = ProductItem()
        product['source_internal_id'] = review['source_internal_id']
        product['OriginalCategoryName'] = response.meta.get('category')
        product['ProductName'] = review['ProductName']

        picurl_xpath = '//meta[@property="og:image"]/@content'
        product['PicURL'] = response.xpath(picurl_xpath).get()

        product['TestUrl'] = response.url
        # ---------------------------------------------------------------------

        yield review
        yield product
