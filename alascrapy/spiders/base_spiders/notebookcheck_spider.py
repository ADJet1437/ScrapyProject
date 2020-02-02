# -*- coding: utf-8 -*-

# Base class of all notebookcheck spiders
# Different languages will most likely need to be trated differently
#   since the html has some differences in the languages.
# This script works for nottebookcheck_it.
import dateparser
from datetime import datetime
from scrapy.http import Request
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.items import ProductItem, ReviewItem
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.lib.generic import date_format


class Notebookcheck_Spider(AlaSpider):
    allowed_domains = ['notebookcheck.com']

    code_to_category = {
        '16': 'Notebook',
        '11': 'Tablet',
        '10': 'Smartphone'
    }

    curent_category_page_number = {
        'Notebook': 0,
        'Tablet': 0,
        'Smartphone': 0
    }

    def __init__(self, *args, **kwargs):
        super(Notebookcheck_Spider, self).__init__(self, *args, **kwargs)
        if not self.incremental_scraping:
            self.stored_last_date = datetime(1970, 1, 1)
            return

        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

    def start_requests(self):
        for key, value in self.code_to_category.iteritems():
            category_url = self.url_format.format(1, key)

            meta_data = {'category_value': key,
                         'category_name': value}

            category_page_request = Request(category_url,
                                            callback=self.parse,
                                            meta=meta_data)

            yield category_page_request

    def parse(self, response):

        reviews_urls_xpath = '//a[@class="introa_large introa_review"]/@href'
        review_urls = self.extract_list(response.xpath(reviews_urls_xpath))
        if not review_urls:
            another_reviews_urls_xpath = '//a[@class="introa_large introa_news"]/@href'
            review_urls = self.extract_list(response.xpath(another_reviews_urls_xpath))

        for review_url in review_urls:
            yield Request(review_url,
                          callback=self.parse_product_review,
                          meta=response.meta)

    # def get_date(self, response):
    #     date_xpath = '//span[@class="intro-date"]//text()'
    #     date_str = response.xpath(date_xpath).get()
    #     if not date_str:
    #         date_xpath = '(//div[@class="introa_fulldate"]//text())[last()]'
    #         date_str = self.extract(response.xpath(date_xpath))
    #     # date = datetime.strptime(date, '%m/%d/%Y')
    #     date = dateparser.parse(date_str)

    #     return date

    def get_product_name(self, response):
        json_xpath = '//div[@class="tx-nbc2fe-pi1"]'\
                     '//script[@type="application/ld+json"]//text()'
        json_str = response.xpath(json_xpath).get()

        # Parsing this json to a python dictionary is giving too much problems
        # json_str = json_str.encode('utf8')
        # d = json.loads(json_str.decode('unicode-escape'))
        if json_str:
            product_name = json_str.split('"name":')[1]
            product_name = product_name.split('},')[0]
            product_name = product_name.replace('"', '')
            product_name = product_name.strip()

            return product_name
        else:
            title_xpath = '//meta[@property="og:title"]/@content'
            title = response.xpath(title_xpath).get()

            words_to_remove = ['Recensione del Portatile',
                               'Recensione del',
                               'Recensione',
                               'Portatile',
                               'lo Smartphone']

            for word in words_to_remove:
                title = title.replace(word, '')

            title = title.strip()
            return title

    def parse_product_review(self, response):
        review_xpaths = {
            'TestTitle': '//meta[@property="og:title"]/@content',
            'Author': '//meta[@property="article:author"]/@content',
            'TestSummary': '//meta[@property="og:description"]/@content',

        }

        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        if not review['TestSummary']:
            summary_xpath = '//div[@class="nbcintro"]//p//text()'
            summary_list = response.xpath(summary_xpath).getall()
            review['TestSummary'] = ''.join(summary_list).replace('\r', '')
            review['TestSummary'] = review['TestSummary'].strip()

        # SourceTestScale and SourceTestRating
        rating_xpath = '//div[@class="rating_percent_final"]'\
                       '//span[@class="average"]//text()'
        rating = response.xpath(rating_xpath).get()
        if rating:
            rating = rating.replace('%', '')
            review['SourceTestRating'] = rating
            review['SourceTestScale'] = 100

        review['DBaseCategoryName'] = 'PRO'

        review['ProductName'] = 'P1'

        # common date xpath
        date_xpath = "(//div[@class='news-author-date']//text())[last()]"
        date_str = self.extract(response.xpath(date_xpath)).replace(', ', '')
        if date_str:
            date = date_format(date_str, '%Y/%m/%d')
        # for .it
        else:
            date_xpath = '//span[@class="intro-date"]//text()'
            date_str = self.extract(response.xpath(date_xpath))
            date = date_format(date_str, '%m/%d/%Y')
        review['TestDateText'] = date

        # Source Internal ID
        source_internal_id = response.url.split('.0.html')[0]
        source_internal_id = source_internal_id.split('.')[-1]
        review['source_internal_id'] = source_internal_id

        # TestPros
        pros_xpath = '//div[@class="pc_element pc_element_pro"]'\
                     '//div[@class="pc_tr"]//span[2]//text()'
        pros = response.xpath(pros_xpath).getall()
        pros_str = ';'.join(pros).replace('\r', '')
        review['TestPros'] = pros_str

        # TestCons
        cons_xpath = '//div[@class="pc_element pc_element_contra"]'\
                     '//div[@class="pc_tr"]//span[2]//text()'
        cons = response.xpath(cons_xpath).getall()
        cons_str = ';'.join(cons).replace('\r', '')
        review['TestCons'] = cons_str

        # ProductName
        review['ProductName'] = self.get_product_name(response)

        # PRODUCT --------------------------------------------------
        product = ProductItem()
        product['source_internal_id'] = review['source_internal_id']
        product['OriginalCategoryName'] = response.meta.get('category_name')
        product['ProductName'] = review['ProductName']
        pic_url_xpath = '//meta[@property="og:image"]/@content'
        product['PicURL'] = response.xpath(pic_url_xpath).get()
        product['TestUrl'] = response.url

        yield review
        yield product
