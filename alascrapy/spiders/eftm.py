# -*- coding: utf8 -*-

from datetime import datetime
from scrapy.http import Request
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem


class Audiobacon_netSpider(AlaSpider):
    name = 'eftm'
    allowed_domains = ['eftm.com']
    page_number = 1
    start_urls = ['https://eftm.com/tech/page/1']

    def __init__(self, *args, **kwargs):
        super(Audiobacon_netSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

        # In order to test another stored_last_date
        # self.stored_last_date = datetime(2018, 2, 8)

    def parse(self, response):
        # print " 	...PARSE: " + response.url
        # print " --self.stored_last_date: " + str(self.stored_last_date)

        review_lis_xpath = '//li[@class="infinite-post"]'
        review_lis = response.xpath(review_lis_xpath)

        review_url_xpath = './a/@href'
        test_title_xpath = './a/@title'
        for l_r in review_lis[:-1]:
            review_url = l_r.xpath(review_url_xpath).get()
            test_title = l_r.xpath(test_title_xpath).get()

            yield Request(url=review_url,
                          callback=self.parse_product_review,
                          meta={'last_review': False,
                                'test_title': test_title})

        # Last review of the page
        review_url = review_lis[-1].xpath(review_url_xpath).get()
        test_title = review_lis[-1].xpath(test_title_xpath).get()
        yield Request(url=review_url,
                      callback=self.parse_product_review,
                      meta={'last_review': True,
                            'test_title': test_title})

    def get_product_name_based_on_title(self, title):
        ''' This function will 'clean' the title of the review
            in order to get the product name '''
        p_name = title

        # Spliting title
        get_first_piece = [u'Review:', u' – ', 'Review', 'review', 'review:']
        get_last_piece = []

        for g_f in get_first_piece:
            if g_f in p_name:
                p_name = p_name.split(g_f)[0]

        for g_l in get_last_piece:
            if g_l in p_name:
                p_name = p_name.split(g_l)[-1]

        # Removing certain words
        words_to_remove = ['review']
        for w in words_to_remove:
            if w in title:
                p_name = p_name.replace(w, '')

        # Removing unnecessary spaces:
        p_name = p_name.replace('  ', ' ')
        p_name = p_name.strip()

        return p_name

    def parse_product_review(self, response):
        # print "     ...PARSE_PRODUCT_REVIEW: " + response.url

        # Check date of the review
        date_xpath = '//time/@datetime'
        date = response.xpath(date_xpath).get()
        # date looks like: 2019-06-06
        date = datetime.strptime(date, '%Y-%m-%d')
        if date > self.stored_last_date:

            # REVIEW ITEM -----------------------------------------------------
            review_xpaths = {
                'Author': '(//a[@rel="author"])[1]//text()',
                'TestSummary': '//meta[@property="og:description"]/@content',
            }

            # Create the review
            review = self.init_item_by_xpaths(response,
                                              "review",
                                              review_xpaths)

            # 'TestTitle'
            review['TestTitle'] = response.meta.get('test_title')

            # 'ProductName'
            title = review['TestTitle']
            review['ProductName'] = self.get_product_name_based_on_title(title)

            # 'TestDateText'
            review['TestDateText'] = date.strftime("%Y-%m-%d")

            # 'DBaseCategoryName'
            review['DBaseCategoryName'] = 'PRO'

            # 'source_internal_id'
            sid_xpath = '//link[@rel="shortlink"]/@href'
            sid = response.xpath(sid_xpath).get()
            # sid looks like: href="https://eftm.com/61404"
            sid = sid.split('/')[-1]
            review['source_internal_id'] = sid
            # -----------------------------------------------------------------

            # PRODUCT ITEM ----------------------------------------------------
            product = ProductItem()
            product['source_internal_id'] = review['source_internal_id']
            product['OriginalCategoryName'] = None
            product['ProductName'] = review['ProductName']

            pic_url_xpath = '//meta[@property="og:image"]/@content'
            pic_url = response.xpath(pic_url_xpath).get()
            product['PicURL'] = pic_url

            product['TestUrl'] = response.url
            # ------------------------------------------------------------------

            yield review
            yield product

            # Checking whether we should scrape the next page
            if response.meta.get('last_review'):
                self.page_number += 1
                base_url = 'https://eftm.com/tech/page/{}'
                next_page_url = base_url.format(self.page_number)
                yield Request(url=next_page_url,
                              callback=self.parse)
