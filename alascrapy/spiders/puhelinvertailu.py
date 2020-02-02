# -*- coding: utf8 -*-

from datetime import datetime
from scrapy.http import Request
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem


class PuhelinvertailuSpider(AlaSpider):
    name = 'puhelinvertailu'
    allowed_domains = ['puhelinvertailu.com']

    start_urls = ['https://www.puhelinvertailu.com/arvostelut']

    def __init__(self, *args, **kwargs):
        super(PuhelinvertailuSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

        # In order to test another stored_last_date
        # self.stored_last_date = datetime(2018, 2, 8)

    def parse(self, response):
        # print " 	...PARSE: " + response.url
        # print " --self.stored_last_date: " + str(self.stored_last_date)

        review_articles_xpath = '//div[@class="listing tests"]/article'
        review_articles = response.xpath(review_articles_xpath)

        for r_art in review_articles:
            date_xpath = './div[@class="col-list"]/p//text()'
            date = r_art.xpath(date_xpath).get()
            # date looks like: 31.3.2019
            date = datetime.strptime(date, '%d.%m.%Y')

            if date > self.stored_last_date:
                review_url_xpath = './a[1]/@href'
                review_url = r_art.xpath(review_url_xpath).get()

                yield response.follow(url=review_url,
                                      callback=self.parse_product_review,
                                      meta={'date': date.strftime("%Y-%m-%d")})

    def get_product_name_based_on_title(self, title):
            ''' This function will 'clean' the title of the review
                in order to get the product name '''
            p_name = title

            # Spliting title
            get_first_piece = [u' - ', u' – ']
            get_last_piece = [u':']

            for g_f in get_first_piece:
                if g_f in p_name:
                    p_name = p_name.split(g_f)[0]

            for g_l in get_last_piece:
                if g_l in p_name:
                    p_name = p_name.split(g_l)[-1]

            # Removing certain words
            words_to_remove = ['Arvostelussa']
            for w in words_to_remove:
                if w in title:
                    p_name = p_name.replace(w, '')

            # Removing unnecessary spaces:
            p_name = p_name.replace('  ', ' ')
            p_name = p_name.strip()

            return p_name

    def parse_product_review(self, response):
        # print "     ...PARSE_PRODUCT_REVIEW: " + response.url

        # REVIEW ITEM -----------------------------------------------------
        review_xpaths = {
            'TestTitle':  '//header/h1//text()',
            'Author': '//meta[@name="author"]/@content',
            'TestSummary': '//meta[@property="og:description"]/@content',
        }

        # Create the review
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        if not review['TestSummary']:
            summary_xpath = '//meta[@name="description"]/@content'
            summary = response.xpath(summary_xpath).get()
            review['TestSummary'] = summary

        # 'ProductName'
        title = review['TestTitle']
        review['ProductName'] = self.get_product_name_based_on_title(title)

        # 'TestDateText'
        review['TestDateText'] = response.meta.get('date')

        # 'SourceTestScale' and 'SourceTestRating'
        rating_xpath = '//meta[@itemprop="rating"]/@content'
        rating = response.xpath(rating_xpath).get()
        if rating:
            review['SourceTestScale'] = 5
            review['SourceTestRating'] = rating

        # 'DBaseCategoryName'
        review['DBaseCategoryName'] = 'PRO'

        # 'source_internal_id'
        sid = response.url
        # sid looks like: www..../uutiset/2018/11/25/arvostelu-oneplus-6t
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
        # -----------------------------------------------------------------

        yield review
        yield product
