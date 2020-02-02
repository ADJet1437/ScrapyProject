# -*- coding: utf8 -*-

from datetime import datetime
from scrapy.http import Request
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem


class Mobiili_fiSpider(AlaSpider):
    name = 'mobiili_fi'
    allowed_domains = ['mobiili.fi']

    start_urls = ['https://mobiili.fi/category/arvostelut/']

    def __init__(self, *args, **kwargs):
        super(Mobiili_fiSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

        # In order to test another stored_last_date
        # self.stored_last_date = datetime(2018, 2, 8)

    def parse(self, response):
        # print " 	...PARSE: " + response.url
        # print "     self.stored_last_date: " + str(self.stored_last_date)

        review_divs_xpath = '//div[@class="fullarticle"]'
        review_divs = response.xpath(review_divs_xpath)

        for r_div in review_divs:
            date_xpath = './/span[@class="date"]//text()'
            date = r_div.xpath(date_xpath).get().strip()
            # date looks like: 'su 28.10.2018, klo 12:19 |'
            date = date.split(',')[0]
            date = date.split(' ')[-1]
            date = datetime.strptime(date, '%d.%m.%Y')
            if date > self.stored_last_date:
                author_xpath = './/a[@rel="author"]//text()'
                author = r_div.xpath(author_xpath).get()

                review_url_xpath = './/a[@class="thumblink"]/@href'
                review_url = r_div.xpath(review_url_xpath).get()

                yield Request(url=review_url,
                              callback=self.parse_product_review,
                              meta={'date': date.strftime("%Y-%m-%d"),
                                    'author': author})

        # Check for next page
        next_page_url_xpath = '//a[@class="next page-numbers"]/@href'
        next_page_url = response.xpath(next_page_url_xpath).get()
        if next_page_url:
            yield Request(url=next_page_url,
                          callback=self.parse)

    def get_product_name_based_on_title(self, title):
        ''' This function will 'clean' the title of the review
            in order to get the product name '''
        p_name = title

        # Spliting title
        get_first_piece = [u':', u' – ']

        for g_f in get_first_piece:
            if g_f in p_name:
                p_name = p_name.split(g_f)[0]

        # Removing certain words
        words_to_remove = [u'Arvostelussa', u'Testissä', u'Tällainen on',
                           u'-älypuhelin']
        for w in words_to_remove:
            if w in title:
                p_name = p_name.replace(w, '')

        # Removing unnecessary spaces:
        p_name = p_name.replace('  ', ' ')
        p_name = p_name.strip()

        return p_name

    def parse_product_review(self, response):
        # print "     ...PARSE_PRODUCT_REVIEW: " + response.url

        # REVIEW ITEM ------------------------------------------------------
        review_xpaths = {
            'TestTitle': '//meta[@property="og:title"]/@content',
            'TestSummary': '//meta[@property="og:description"]/@content',
        }

        # Create the review
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        # 'ProductName'
        title = review['TestTitle']
        review['ProductName'] = self.get_product_name_based_on_title(title)

        # 'Author'
        review['Author'] = response.meta.get('author')

        # 'TestDateText'
        review['TestDateText'] = response.meta.get('date')

        # 'DBaseCategoryName'
        review['DBaseCategoryName'] = 'PRO'

        # 'source_internal_id'
        sid_xpath = '//link[@rel="shortlink"]/@href'
        sid = response.xpath(sid_xpath).get()
        # sid looks like: "https://mobiili.fi/?p=125312"
        sid = sid.split('?p=')[-1]
        review['source_internal_id'] = sid
        # ------------------------------------------------------------------

        # PRODUCT ITEM -----------------------------------------------------
        product = ProductItem()
        product['source_internal_id'] = review['source_internal_id']

        cats_xpath = '//div[@class="categories"]/a//text()'
        cats = response.xpath(cats_xpath).getall()
        category = None
        if u'Älypuhelimet' in cats:
            category = 'Smartphone'
        elif u'Tabletit' in cats:
            category = 'Tablet'

        product['OriginalCategoryName'] = category
        product['ProductName'] = review['ProductName']

        pic_url_xpath = '//meta[@property="og:image"]/@content'
        pic_url = response.xpath(pic_url_xpath).get()
        product['PicURL'] = pic_url

        product['TestUrl'] = response.url
        # ------------------------------------------------------------------

        yield review
        yield product
