# -*- coding: utf8 -*-

from datetime import datetime
from scrapy.http import Request
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem


class Telix_plSpider(AlaSpider):
    name = 'telix_pl'
    allowed_domains = ['telix.pl']
    page_number = 1

    start_urls = ['https://www.telix.pl/home/testy-opinie/page/1/']

    def __init__(self, *args, **kwargs):
        super(Telix_plSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

        # In order to test another stored_last_date
        # self.stored_last_date = datetime(2018, 2, 8)

    def parse(self, response):
        # print " 	...PARSE: " + response.url
        # print " --self.stored_last_date: " + str(self.stored_last_date)

        review_articles_xpath = '//div[contains(@class, "fusion-'\
                                'posts-container")]/article'
        review_articles = response.xpath(review_articles_xpath)

        date = None
        for r_a in review_articles[:-1]:
            date_xpath = './/span[@class="updated"]//text()'
            date = r_a.xpath(date_xpath).get()
            # date looks like: 2019-06-02T10:19:11+02:00
            date = date.split('T')[0]
            date = datetime.strptime(date, '%Y-%m-%d')

            if date > self.stored_last_date:
                author_xpath = './/a[@rel="author"]//text()'
                author = r_a.xpath(author_xpath).get()

                review_url_xpath = './/a[img]/@href'
                review_url = r_a.xpath(review_url_xpath).get()

                test_title_xpath = './/h2[@class="blog-shortcode-post-title '\
                                   'entry-title"]//text()'
                test_title = r_a.xpath(test_title_xpath).get()

                yield Request(url=review_url,
                              callback=self.parse_product_review,
                              meta={'author': author,
                                    'date': date.strftime("%Y-%m-%d"),
                                    'test_title': test_title})

        # Check for next page
        if date > self.stored_last_date:
            self.page_number += 1
            next_page_url = 'https://www.telix.pl/home/testy-opinie/'\
                            'page/{}/'.format(self.page_number)
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
        words_to_remove = ['Test']
        for w in words_to_remove:
            if w in title:
                p_name = p_name.replace(w, '')

        # Removing unnecessary spaces:
        p_name = p_name.replace('  ', ' ')
        p_name = p_name.strip()

        return p_name

    def parse_product_review(self, response):
        # print "     ...PARSE_PRODUCT_REVIEW: " + response.url

        # REVIEW ITEM ---------------------------------------------------------
        review_xpaths = {
            'TestSummary': '//meta[@property="og:description"]/@content',
        }

        # Create the review
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        # 'TestSummary'
        remove = ['\r', '\n']
        for w in remove:
            if w in review['TestSummary']:
                review['TestSummary'] = review['TestSummary'].replace(w, '')

        # 'TestTitle'
        review['TestTitle'] = response.meta.get('test_title')

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
        sid_xpath = '//article/@id'
        sid = response.xpath(sid_xpath).get()
        # sid looks like: "post-941172"
        sid = sid.split('post-')[-1]
        review['source_internal_id'] = sid
        # ---------------------------------------------------------------------

        # PRODUCT ITEM --------------------------------------------------------
        product = ProductItem()
        product['source_internal_id'] = review['source_internal_id']
        product['OriginalCategoryName'] = None
        product['ProductName'] = review['ProductName']

        pic_url_xpath = '//meta[@property="og:image"]/@content'
        pic_url = response.xpath(pic_url_xpath).get()
        product['PicURL'] = pic_url

        product['TestUrl'] = response.url
        # ---------------------------------------------------------------------

        yield review
        yield product
