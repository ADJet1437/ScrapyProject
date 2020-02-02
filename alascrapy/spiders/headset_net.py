# -*- coding: utf8 -*-

from datetime import datetime
from scrapy.http import Request
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem, ProductIdItem
import dateparser


class Headset_netSpider(AlaSpider):
    name = 'headset_net'
    allowed_domains = ['headset.net']

    def __init__(self, *args, **kwargs):
        super(Headset_netSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

        # In order to test another stored_last_date
        # self.stored_last_date = datetime(2018, 2, 8)

    def start_requests(self):
        # print " 	...START_REQUESTS: "

        base_url = 'https://www.headset.net'
        url_cat_dict = {'Gaming Headset': base_url + '/gaming/',
                        'Wireless Headset': base_url + '/wireless/',
                        'PC Headset': base_url + '/pc/',
                        'In-ear Headset': base_url + '/in-ear/',
                        'Handy Headset': base_url + '/handy/',
                        'Telefon Headset': base_url + '/telefon/',
                        'Bluetooth Headset': base_url + '/bluetooth/'}

        for cat in url_cat_dict:
            yield Request(url=url_cat_dict[cat],
                          callback=self.parse,
                          meta={'cat': cat})

    def parse(self, response):
        # print " 	...PARSE: " + response.url
        # print " --self.stored_last_date: " + str(self.stored_last_date)

        review_lis_xpath = '//ol[@class="results"]/li'
        review_lis = response.xpath(review_lis_xpath)

        for r_li in review_lis:
            review_url_xpath = './/a[@class="detail"]/@href'
            review_url = r_li.xpath(review_url_xpath).get()

            price_xpath = './/span[@class="price"]//text()'
            price = r_li.xpath(price_xpath).get()

            sid_xpath = './/span[@class="price"]/@id'
            sid = r_li.xpath(sid_xpath).get()
            # sid looks like: price_1754
            sid = sid.replace('price_', '')

            yield Request(url=review_url,
                          callback=self.parse_product_review,
                          meta={'price': price,
                                'sid': sid,
                                'cat': response.meta.get('cat')})

    def parse_product_review(self, response):
        # print "         ...PARSE_PRODUCT_REVIEW: " + response.url

        date_xpath = '//div[@class="opinion"]/strong//text()'
        date = response.xpath(date_xpath).get()
        # date looks like: Januar 2017
        if date:
            date = dateparser.parse(date,
                                    date_formats=['%B %Y'],
                                    languages=['de', 'es'])

        if date and date > self.stored_last_date:
            # REVIEW ITEM ------------------------------------------
            review_xpaths = {
                'TestTitle': '//title//text()',
                'TestSummary': '//meta[@name="description"]/@content',
            }

            # Create the review
            review = self.init_item_by_xpaths(response,
                                              "review",
                                              review_xpaths)

            # 'ProductName'
            p_name = review['TestTitle']
            if ' Headset ' in p_name:
                p_name = p_name.split(' Headset ')[0]
            review['ProductName'] = p_name

            # 'Author'
            author_xpath = '//span[@itemprop="author"]//text()'
            author = response.xpath(author_xpath).get()

            # 'TestDateText'
            review['TestDateText'] = date.strftime("%Y-%m-%d")

            # 'SourceTestScale' and 'SourceTestRating'
            rating_xpath = '(//div[@class="stars"])[1]//text()'
            rating = response.xpath(rating_xpath).getall()
            rating = "".join(rating)
            rating = rating.split('/')[0]
            rating = rating.replace('(', '')
            rating = rating.strip()
            if rating:
                review['SourceTestRating'] = rating
                review['SourceTestScale'] = 100

            #  'DBaseCategoryName'
            review['DBaseCategoryName'] = 'PRO'

            # 'TestPros' and 'TestCons'
            pros_xpath = '//ul[@class="positive"]/li//text()'
            pros = response.xpath(pros_xpath).getall()
            pros = ";".join(pros)

            cons_xpath = '//ul[@class="negative"]/li//text()'
            cons = response.xpath(cons_xpath).getall()
            cons = ";".join(cons)

            review['TestPros'] = pros
            review['TestCons'] = cons

            # 'source_internal_id'
            review['source_internal_id'] = response.meta.get('sid')
            # ------------------------------------------------------

            # PRODUCT ITEM -----------------------------------------
            product = ProductItem()
            product['source_internal_id'] = review['source_internal_id']
            product['OriginalCategoryName'] = response.meta.get('cat')
            product['ProductName'] = review['ProductName']

            pic_url_xpath = '//meta[@property="og:image"]/@content'
            pic_url = response.xpath(pic_url_xpath).get()
            product['PicURL'] = pic_url

            product['TestUrl'] = response.url
            # ------------------------------------------------------

            # PRODUCTID ITEM -----------------------------------------
            price = response.meta.get('price')
            if price:
                yield ProductIdItem.from_product(product,
                                                 kind='price',
                                                 value=price
                                                 )
            # ------------------------------------------------------

            yield review
            yield product
