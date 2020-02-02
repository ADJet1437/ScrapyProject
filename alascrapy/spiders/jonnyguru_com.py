# -*- coding: utf8 -*-

from datetime import datetime
from scrapy.http import Request
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem


class Jonnyguru_comSpider(AlaSpider):
    name = 'jonnyguru_com'
    allowed_domains = ['jonnyguru.com']

    def __init__(self, *args, **kwargs):
        # print "     ..._INIT_"
        super(Jonnyguru_comSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

        # In order to test another stored_last_date
        # self.stored_last_date = datetime(2017, 2, 8)

    def start_requests(self):
        # print "     ...START_URLS"

        url_base = 'http://www.jonnyguru.com/blog/category/reviews/'

        url_cat_dict = {'CPU cooler': 'cpu-coolers',
                        'Power Supplier': 'power-supplies'}

        for cat in url_cat_dict:
            yield Request(url=url_base+url_cat_dict[cat],
                          callback=self.parse,
                          meta={'cat': cat})

    def parse(self, response):
        # print "     ...PARSE: " + response.url
        # print " --self.stored_last_date: " + str(self.stored_last_date)

        cat = response.meta.get('cat')

        review_divs_xpath = '//div[@class="powerwp-posts-container"]/div'
        review_divs = response.xpath(review_divs_xpath)

        date = None
        for r_div in review_divs:
            date_xpath = './/span[@class="powerwp-list-post-date '\
                         'powerwp-list-post-meta"]//text()'
            date = r_div.xpath(date_xpath).get()
            # date looks like: April 8, 2019
            date = datetime.strptime(date, '%B %d, %Y')

            if date > self.stored_last_date:
                url_review_xpath = './/div[@class="powerwp-list-post-'\
                                   'thumbnail"]/a/@href'
                url_review = r_div.xpath(url_review_xpath).get()

                sid = r_div.xpath('./@id').get()
                sid = sid.split('-')[-1]

                img_xpath = './/img[@class="powerwp-list-post-thumbnail-img '\
                            'wp-post-image"]/@src'
                img = r_div.xpath(img_xpath).get()

                yield Request(url=url_review,
                              callback=self.parse_product_review,
                              meta={'date': date.strftime("%Y-%m-%d"),
                                    'sid': sid,
                                    'last_page': False,
                                    'cat': cat,
                                    'img': img})

        # Check whether we should scrape the next page
        if date and (date > self.stored_last_date):
            next_page_url_xpath = '//a[@class="nextpostslink"]/@href'
            next_page_url = response.xpath(next_page_url_xpath).get()

            if next_page_url:
                yield Request(url=next_page_url,
                              callback=self.parse,
                              meta={'cat': cat})

    def get_product_name_based_on_title(self, title):
        ''' This function will 'clean' the title of the review
            in order to get the product name '''
        p_name = title

        # Spliting title
        get_first_piece = [u' – ']
        get_last_piece = []

        for g_f in get_first_piece:
            if g_f in p_name:
                p_name = p_name.split(g_f)[0]

        # Removing certain words
        words_to_remove = [u' – JonnyGURU.com']
        for w in words_to_remove:
            if w in title:
                p_name = p_name.replace(w, '')

        # Removing unnecessary spaces:
        p_name = p_name.replace('  ', ' ')
        p_name = p_name.strip()

        return p_name

    def get_review(self, response, pros_cons):
        review_xpaths = {
            'TestTitle': '//title//text()',
            'Author': '//span[@class="author vcard"]/a//text()',
        }

        # Create the review
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        # 'TestTitle'
        if u' – ' in review['TestTitle']:
            review['TestTitle'] = review['TestTitle'].split(u' – ')[0]

        # 'ProductName'
        title = review['TestTitle']
        review['ProductName'] = self.get_product_name_based_on_title(title)

        # 'TestDateText'
        review['TestDateText'] = response.meta.get('date')

        # 'DBaseCategoryName'
        review['DBaseCategoryName'] = 'PRO'

        # 'source_internal_id'
        review['source_internal_id'] = response.meta.get('sid')

        # 'summary'
        summary_xpath = '//p[@align="left"]  [strong[text()="SUMMARY"] ]'\
                        '/following-sibling::p[1]//text()'
        summary = response.xpath(summary_xpath).get()
        if summary:
            review['TestSummary'] = summary

        # 'TestPros' 'TestCons'
        if pros_cons:
            pros_xpath = '//p[@align="left"][strong[text()="The GOOD:"] ]'\
                         '/following-sibling::ul[1]/li//text()'
            pros = response.xpath(pros_xpath).getall()
            pros = ";".join(pros)

            cons_xpath = '//p[@align="left"]  [strong[text()="The BAD:"] ]'\
                         '/following-sibling::ul[1]/li//text()'
            cons = response.xpath(cons_xpath).getall()
            cons = ";".join(cons)

            review['TestPros'] = pros
            review['TestCons'] = cons

        return review

    def parse_product_review(self, response):
        # print "     ...PARSE_PRODUCT_REVIEW: " + response.url

        cat = response.meta.get('cat')

        # In case we are in the first page of the reiview
        if not response.meta.get('last_page'):
            last_page_xpath = '//div[@class="page-links"]/a[last()]//@href'
            last_page = response.xpath(last_page_xpath).get()

            # In case the review has multiple pages, let's go to the last
            #  one because that's where we find the Pros and Cons.
            if last_page:
                date = response.meta.get('date')
                sid = response.meta.get('sid')
                img = response.meta.get('img')
                yield Request(url=last_page,
                              callback=self.parse_product_review,
                              meta={'date': date,
                                    'sid': sid,
                                    'last_page': True,
                                    'cat': cat,
                                    'img': img})
                return

            # In case the review doesn't have multiple pages.
            else:
                review = self.get_review(response, False)

        # In case we are in the last page of the review
        else:
            review = self.get_review(response, True)

        url = response.url.split('/')
        if url[-2].isdigit():
            review['TestUrl'] = "/".join(url[:-2])

        # PRODUCT ITEM ---------------------------------------------
        product = ProductItem()
        product['source_internal_id'] = review['source_internal_id']
        product['OriginalCategoryName'] = cat
        product['ProductName'] = review['ProductName']

        product['PicURL'] = response.meta.get('img')

        product['TestUrl'] = review['TestUrl']
        # ----------------------------------------------------------

        yield review
        yield product
