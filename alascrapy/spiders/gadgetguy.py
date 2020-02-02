# -*- coding: utf8 -*-

from datetime import datetime
from scrapy.http import Request
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem


class GadgetguySpider(AlaSpider):
    name = 'gadgetguy'
    allowed_domains = ['gadgetguy.com.au']

    start_urls = ['https://www.gadgetguy.com.au/product/']

    def __init__(self, *args, **kwargs):
        super(GadgetguySpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

        # In order to test another stored_last_date
        # self.stored_last_date = datetime(2018, 2, 8)

    def parse(self, response):
        # print " 	...PARSE: " + response.url
        # print " --self.stored_last_date: " + str(self.stored_last_date)

        review_articles_xpath = '//div[@class="cb-main clearfix '\
                                'cb-module-block"]//article'
        review_articles = response.xpath(review_articles_xpath)

        date = None
        for r_a in review_articles:
            date_xpath = './/span[@class="cb-date"]/time/@datetime'
            date = r_a.xpath(date_xpath).get()
            # date looks like: 2019-05-07
            date = datetime.strptime(date, '%Y-%m-%d')
            if date > self.stored_last_date:
                author_xpath = './/span[@class="cb-author"]//a//text()'
                author = r_a.xpath(author_xpath).get()

                rating_xpath = '//span[@class="cb-score"]//text()'
                rating = r_a.xpath(rating_xpath).get()

                url_xpath = './div/a/@href'
                url = r_a.xpath(url_xpath).get()
                url = url + '?display=all'

                yield Request(url=url,
                              callback=self.parse_product_review,
                              meta={'author': author,
                                    'date': date.strftime("%Y-%m-%d"),
                                    'rating': rating})

        # Checking whether we should scrape the next page
        if date and date > self.stored_last_date:
            next_page_url_xpath = '//a[@class="next page-numbers"]/@href'
            next_page_url = response.xpath(next_page_url_xpath).get()

            if next_page_url:
                yield Request(url=next_page_url,
                              callback=self.parse)

    def get_product_name_based_on_title(self, title):
        ''' This function will 'clean' the title of the review
            in order to get the product name '''
        p_name = title

        # Title begins with unnecessary sentence
        discart_beggings = ['Review: ']

        for s in discart_beggings:
            if p_name.startswith(s):
                p_name = p_name.replace(s, '')

        # Spliting title
        get_first_piece = [u':', u' – ']

        for g_f in get_first_piece:
            if g_f in p_name:
                p_name = p_name.split(g_f)[0]

        # Removing certain words
        words_to_remove = ['Hands-on with the new',
                           'Hands-on with the',
                           'updated',
                           'at affordable price']

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

        # 'Author'
        review['Author'] = response.meta.get('author')

        # 'ProductName'
        title = review['TestTitle']
        p_n = self.get_product_name_based_on_title(title)
        review['ProductName'] = p_n

        # 'TestDateText'
        review['TestDateText'] = response.meta.get('date')

        # 'SourceTestScale' and 'SourceTestRating'
        review['SourceTestRating'] = response.meta.get('rating')
        if review['SourceTestRating']:
            review['SourceTestScale'] = 5

        # 'DBaseCategoryName'
        review['DBaseCategoryName'] = 'PRO'

        # 'TestPros' and 'TestCons'
        pros_xpath = '(//div[@class="cb-pros-cons cb-font-header '\
                     'cb-pros-list"])[1]/span//text()'
        pros = response.xpath(pros_xpath).getall()
        pros = ";".join(pros)

        cons_xpath = '(//div[@class="cb-pros-cons cb-font-header '\
                     'cb-pros-list"])[2]/span//text()'
        cons = response.xpath(cons_xpath).getall()
        cons = ";".join(cons)

        review['TestPros'] = pros
        review['TestCons'] = cons

        # 'source_internal_id'
        sid_xpath = '//link[@rel="shortlink"]/@href'
        sid = response.xpath(sid_xpath).get()
        sid = sid.split('?p=')[-1]
        review['source_internal_id'] = sid
        # ------------------------------------------------------------------

        # PRODUCT ITEM -----------------------------------------------------
        product = ProductItem()
        product['source_internal_id'] = review['source_internal_id']

        # Category
        cat = None
        k_printer = ['Laser', 'printer']
        cat = self.get_cat('Printer', k_printer, review['TestTitle'])

        k_speaker = ['speakers']
        if not cat:
            cat = self.get_cat('Speakers', k_speaker, review['TestTitle'])

        k_headphone = ['earphones', 'airpods']
        if not cat:
            cat = self.get_cat('Headphones', k_headphone, review['TestTitle'])

        k_v_cleaner = ['vacuum cleaner', 'vacuum sucks', ]
        if not cat:
            cat = self.get_cat('Vacuum Cleaner',
                               k_v_cleaner,
                               review['TestTitle'])

        k_smartwatch = ['Fitbit', 'smartwatch']
        if not cat:
            cat = self.get_cat('Smartwatch', k_smartwatch, review['TestTitle'])

        if not cat:
            cat = 'Unkown'

        product['OriginalCategoryName'] = cat
        product['ProductName'] = review['ProductName']

        pic_url_xpath = '//meta[@property="og:image"]/@content'
        pic_url = response.xpath(pic_url_xpath).get()
        product['PicURL'] = pic_url

        product['TestUrl'] = response.url
        # ------------------------------------------------------------------

        yield review
        yield product

    def get_cat(self, cat_name, key_words, t_title):
        cat = None
        for w in key_words:
            if w in t_title:
                cat = cat_name
                break

        return cat
