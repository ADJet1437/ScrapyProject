# -*- coding: utf8 -*-
from datetime import datetime
from scrapy.http import Request
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem
import json


class MashableSpider(AlaSpider):
    name = 'mashable'
    allowed_domains = ['mashable.com']
    page = 1
    base_url = 'https://mashable.com/category/reviews?format=json&' \
               'europe=true&utm_campaign=mash-prod-nav-sub&' \
               'utm_source=internal&utm_medium=onsite&page={}'
    start_urls = [base_url.format(page)]

    def __init__(self, *args, **kwargs):
        super(MashableSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

        # In order to test another stored_last_date
        # self.stored_last_date = datetime(2018, 2, 8)
    def parse(self, response):
        # print "     ...PARSE: " + response.url
        # print "     self.stored_last_date: " + str(self.stored_last_date)

        js = json.loads(response.body)

        reviews = js["data"]
        date = None
        for r in reviews:
            date = r["post_date"]
            # date looks like: "2019-05-01T14:28:57+00:00"
            date = date.split('T')[0]
            date = datetime.strptime(date, '%Y-%m-%d')

            if date > self.stored_last_date:
                url = r["link"]
                _id = r["_id"]
                author = r["author"]
                img = r["feature_image"]

                yield Request(url=url,
                              callback=self.parse_product_review,
                              meta={'id': _id,
                                    'author': author,
                                    'img': img,
                                    'date': date.strftime("%Y-%m-%d")})

        # Checking whether we should scrape the next page
        if date and date > self.stored_last_date:
            self.page += 1
            yield Request(url=self.base_url.format(self.page),
                          callback=self.parse)

    def parse_product_review(self, response):
        # print "     ...PARSE_PRODUCT_REVIEW: " + response.url

        # check whether it's a video page review
        video_page_review_xpath = '//body[@class="body_video_categories '\
                                  'body_index"]'
        video_page_review = response.xpath(video_page_review_xpath)

        # here we drop the review in case it's a video page review
        if len(video_page_review) > 0:
            return

        # REVIEW ITEM -------------------------------------------------
        review_xpaths = {
            'TestTitle': '//title[1]//text()',
        }

        # Create the review
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        js = response.xpath('//script[@type="application'
                            '/ld+json"]//text()').get()
        js = json.loads(js)

        # Check whether it's a product or not. If it's not a product,
        #  we should not scrape it. It's something like an article.
        review_type = js["@type"]
        if review_type != "Product":
            return

        # 'ProductName'
        review['ProductName'] = js["name"]
        words_to_remove = ['review', 'Review']
        for w in words_to_remove:
            if w in review['ProductName']:
                review['ProductName'] = review['ProductName'].replace(w, '')

        # 'Author'
        review['Author'] = response.meta.get('author')

        # 'TestSummary'
        review['TestSummary'] = js["description"]

        # 'TestDateText'
        review['TestDateText'] = response.meta.get('date')

        # 'SourceTestScale' and 'SourceTestRating'
        rating = js["review"]["reviewRating"]["ratingValue"]
        if rating:
            review['SourceTestRating'] = rating
            scale = js["review"]["reviewRating"]["bestRating"]
            review['SourceTestScale'] = scale

        #  'DBaseCategoryName'
        review['DBaseCategoryName'] = 'PRO'

        # 'TestPros' 'TestCons'
        pros_xpath = '(//ul[@class="pro-con-list-items"])[1]/li/span//text()'
        pros = response.xpath(pros_xpath).getall()
        if not pros:
            pros_xpath = '//div[@class="product-section-header good"]'\
                         '//following::text()'
            pros = response.xpath(pros_xpath).get()
            pros = pros.strip()
            pros = pros.split(u'•')
        pros = ";".join(pros)

        cons_xpath = '(//ul[@class="pro-con-list-items"])[2]/li/span//text()'
        cons = response.xpath(cons_xpath).getall()
        if not cons:
            cons_xpath = '//div[@class="product-section-header bad"]'\
                         '//following::text()'
            cons = response.xpath(cons_xpath).get()
            cons = cons.strip()
            cons = cons.split(u'•')
        cons = ";".join(cons)

        review['TestPros'] = pros
        review['TestCons'] = cons

        # 'source_internal_id'
        review['source_internal_id'] = response.meta.get('id')
        # -------------------------------------------------------------

        # PRODUCT ITEM ------------------------------------------------
        product = ProductItem()
        product['source_internal_id'] = review['source_internal_id']
        product['OriginalCategoryName'] = None
        product['ProductName'] = review['ProductName']
        product['PicURL'] = response.meta.get('img')
        product['TestUrl'] = response.url
        # -------------------------------------------------------------

        yield review
        yield product
