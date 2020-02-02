# -*- coding: utf8 -*-

from datetime import datetime
from scrapy.http import Request
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem


class Laptopmedia_comSpider(AlaSpider):
    name = 'laptopmedia_com'
    allowed_domains = ['laptopmedia.com']

    start_urls = ['https://laptopmedia.com/category/reviews/']

    def __init__(self, *args, **kwargs):
        super(Laptopmedia_comSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

        # In order to test another stored_last_date
        # self.stored_last_date = datetime(2018, 2, 8)

    def parse(self, response):
        # print "     ...PARSE: " + response.url
        # print " --self.stored_last_date: " + str(self.stored_last_date)

        review_divs_xpath = '//div[@class="alm-reveal"]//article'
        review_divs = response.xpath(review_divs_xpath)

        date = None
        for r_div in review_divs:
            date_xpath = './/i[@class="fa fa-calendar-o"]/'\
                         'following-sibling::text()'
            date = r_div.xpath(date_xpath).get()
            date = date.replace('|', '')
            date = date.strip()
            # date looks like this: 3 April 2019
            date = datetime.strptime(date, '%d %B %Y')

            if date > self.stored_last_date:
                review_url_xpath = './/h2[@class="entry-title"]/a/@href'
                review_url = r_div.xpath(review_url_xpath).get()

                # <aticle class="post-174334 review type-review...
                classes = r_div.xpath('./@class').getall()

                category = 'Notebook'
                if 'smartphone-review' in classes:
                    category = 'Smartphone'

                # The <article> element contains the ID of the review
                sid = classes[0]
                sid = sid.split(' ')[0]
                sid = sid.replace('post-', '')

                yield Request(url=review_url,
                              callback=self.parse_product_review,
                              meta={'date': date.strftime("%Y-%m-%d"),
                                    'sid': sid,
                                    'cat': category})

        # Checking whether we should scrape the next page
        # date already contains the date of the last review of the page
        if date and (date > self.stored_last_date):
            next_page_url_xpath = '//li[@class="pagination-next"]/a/@href'
            next_page_url = response.xpath(next_page_url_xpath).get()

            yield Request(url=next_page_url,
                          callback=self.parse)

    def get_product_name_based_on_title(self, title):
        ''' This function will 'clean' the title of the review
            in order to get the product name '''
        p_name = title

        # Spliting title
        get_first_piece = [u'review –', u' – ']

        for g_f in get_first_piece:
            if g_f in p_name:
                p_name = p_name.split(g_f)[0]

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
        authors_xpath = '//span[@class="entry-info-author"]//text()'
        authors = response.xpath(authors_xpath).get()

        # 'TestDateText'
        review['TestDateText'] = response.meta.get('date')

        # 'DBaseCategoryName'
        review['DBaseCategoryName'] = 'PRO'

        # 'TestPros'  'TestCons'
        pros_xpath = '//div[@class="color-green plus-wrapper col-sm-6 '\
                     'col-xs-12"]/ul/li//text()'
        pros = response.xpath(pros_xpath).getall()
        if pros:
            pros = ";".join(pros)
            review['TestPros'] = pros

        cons_xpath = '//div[@class="color-red minus-wrapper '\
                     'col-sm-6 col-xs-12"]/ul/li//text()'
        cons = response.xpath(cons_xpath).getall()
        if cons:
            cons = ";".join(cons)
            review['TestCons'] = cons

        # 'source_internal_id'
        review['source_internal_id'] = response.meta.get('sid')
        # ------------------------------------------------------------------

        # PRODUCT ITEM -----------------------------------------------------
        product = ProductItem()
        product['source_internal_id'] = review['source_internal_id']
        product['OriginalCategoryName'] = response.meta.get('cat')
        product['ProductName'] = review['ProductName']

        pic_url_xpath = '//meta[@property="og:image"]/@content'
        pic_url = response.xpath(pic_url_xpath).get()
        product['PicURL'] = pic_url

        product['TestUrl'] = response.url
        # ------------------------------------------------------------------

        yield review
        yield product
