# -*- coding: utf8 -*-

from datetime import datetime
from scrapy.http import Request
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem


class Projectorreviews_com_auSpider(AlaSpider):
    name = 'projectorreviews_com_au'
    allowed_domains = ['projectorreviews.com.au']

    base_url = 'http://projectorreviews.com.au'
    start_urls = [base_url + '/hometheatrereviews.htm',
                  base_url + '/portableprojectorreviews.htm',
                  base_url + '/multipurposeprojectorreviews.htm',
                  base_url + '/largevenueprojectorreviews.htm']

    def __init__(self, *args, **kwargs):
        super(Projectorreviews_com_auSpider, self).__init__(self,
                                                            *args,
                                                            **kwargs)

        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

        # In order to test another stored_last_date
        # self.stored_last_date = datetime(2000, 2, 8)

    def parse(self, response):
        # print "     ...PARSE: " + response.url
        # print " --self.stored_last_date: " + str(self.stored_last_date)

        review_urls_xpath = '(//table[@width="100%"])[last()]//p//a/@href'
        review_urls = response.xpath(review_urls_xpath).getall()

        for r_url in review_urls:
            yield response.follow(url=r_url,
                                  callback=self.parse_product_review)

    def get_product_name_based_on_title(self, title):
        ''' This function will 'clean' the title of the review
            in order to get the product name '''
        p_name = title

        # Removing certain words
        words_to_remove = ['Projector Review at Projector Reviews Australia',
                           'Projector Review',
                           u' - ',
                           'Projector Reviews Australia']
        for w in words_to_remove:
            if w in title:
                p_name = p_name.replace(w, '')

        # Removing unnecessary spaces:
        p_name = p_name.replace('  ', ' ')
        p_name = p_name.strip()

        return p_name

    def parse_product_review(self, response):
        # print "     ...PARSE_PRODUCT_REVIEW: " + response.url

        title = response.xpath('//title//text()').get()
        if ' vs ' in title:
            return

        # Check review date
        date_xpath = '//span[@class="value-title"]/@title'
        date = response.xpath(date_xpath).get()
        if date:
            date = date.replace('  ', ' ')
            date = date.strip()
            # date looks like this: 2011-11-30
            date = datetime.strptime(date, '%Y-%m-%d')
            if date > self.stored_last_date:
                # REVIEW ITEM ---------------------------------
                review_xpaths = {
                    'TestTitle': '//title//text()',
                }

                # Create the review
                review = self.init_item_by_xpaths(response,
                                                  "review",
                                                  review_xpaths)

                # 'ProductName'
                title = review['TestTitle']
                pn = self.get_product_name_based_on_title(title)
                review['ProductName'] = pn

                # 'TestSummary'
                summary_xpath = '//td[@width="64%"]//text()'
                summary = response.xpath(summary_xpath).getall()
                summary = "".join(summary)

                words_to_remove = ['\n']
                for w in words_to_remove:
                    if w in summary:
                        summary = summary.replace(w, '')
                summary = summary.replace('  ', '')
                summary = summary.strip()
                if 'Where to Buy' in summary:
                    summary = summary.split('Where to Buy')[0]

                review['TestSummary'] = summary

                # 'TestDateText'
                review['TestDateText'] = date.strftime("%Y-%m-%d")

                # 'SourceTestScale' and 'SourceTestRating'
                rating_xpath = '//span[@class="rating"]//text()'
                rating = response.xpath(rating_xpath).get()
                if rating:
                    review['SourceTestScale'] = 5
                    review['SourceTestRating'] = rating

                # 'DBaseCategoryName'
                review['DBaseCategoryName'] = 'PRO'

                # 'source_internal_id'
                sid = response.url.split('http://projectorreviews.'
                                         'com.au/review')[-1]
                sid = sid.replace('.htm', '')
                review['source_internal_id'] = sid
                # ---------------------------------------------

                # PRODUCT ITEM --------------------------------
                product = ProductItem()
                product['source_internal_id'] = review['source_internal_id']
                product['OriginalCategoryName'] = 'Projector'
                product['ProductName'] = review['ProductName']
                product['TestUrl'] = response.url
                # ---------------------------------------------

                yield review
                yield product
