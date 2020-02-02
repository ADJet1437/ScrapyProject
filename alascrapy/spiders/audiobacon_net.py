# -*- coding: utf8 -*-

from datetime import datetime
from scrapy.http import Request, FormRequest
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem


class Audiobacon_netSpider(AlaSpider):
    name = 'audiobacon_net'
    allowed_domains = ['audiobacon.net']

    def __init__(self, *args, **kwargs):
        super(Audiobacon_netSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

    def start_requests(self):

        b_url = 'https://audiobacon.net/category/headphones'
        cat_url_dict = {'Wireless-Headphones': b_url + '/wireless',
                        'In-Ear Headphones': b_url + '/iem-earphones',
                        'Over-Ear Open Headphones': b_url + '/over-ear-open',
                        'Over-Ear Closed Headphones': b_url + '/over-ear-'
                                                              'closed',
                        'On-Ear Open Headphones': b_url + '/on-ear-open',
                        'On-Ear Closed Headphones': b_url + '/on-ear-'
                                                            'portable-closed'
                        }

        for cat in cat_url_dict:
            yield Request(url=cat_url_dict[cat],
                          callback=self.parse,
                          meta={'cat': cat,
                                'page': 1})

    def parse(self, response):

        review_divs_xpath = '//div[contains(@class, "paginated_page")]' \
                            '//article'

        review_divs = response.xpath(review_divs_xpath)
        cat = response.meta.get('cat')

        date = None
        for r_div in review_divs:
            date_xpath = './/div[@class="post-meta vcard"]/p/span[@class=' \
                         '"updated"]//text()'
            date = r_div.xpath(date_xpath).get()
            # date looks like this: Jan 28, 2019
            date = datetime.strptime(date, '%b %d, %Y')

            if date > self.stored_last_date:
                author_xpath = './/div[@class="post-meta vcard"]/p' \
                               '/a[@rel="author"]//text()'
                author = r_div.xpath(author_xpath).get()

                review_url_xpath = './/div[@class="header"]/a/@href'
                review_url = r_div.xpath(review_url_xpath).get()

                sid = r_div.xpath('./@id').get()
                sid = sid.split('-')[-1]

                yield Request(url=review_url,
                              callback=self.parse_product_review,
                              meta={'cat': cat,
                                    'author': author,
                                    'date': date.strftime("%Y-%m-%d"),
                                    'sid': sid})

        if cat == 'Over-Ear Open Headphones':
            # Check whether we should scrape the next page
            if date and (date > self.stored_last_date):
                next_page_li_xpath = '//li[ @class="next arrow" and '\
                                     'not(contains(@style, "display: none;"))]'
                next_page_li = response.xpath(next_page_li_xpath)

                if next_page_li:

                    page = response.meta.get('page') + 1

                    frmdata = {'action': 'extra_blog_feed_get_content',
                               'et_load_builder_modules': '1',
                               'blog_feed_nonce': 'd0cb14c2b2',
                               'to_page': str(page),
                               'posts_per_page': '10',
                               'order': 'desc',
                               'orderby': 'date',
                               'categories': '10',
                               'show_featured_image': '1',
                               'blog_feed_module_type': 'standard',
                               'et_column_type': '',
                               'show_author': '1',
                               'show_categories': '1',
                               'show_date': '1',
                               'show_rating': '1',
                               'show_more': '1',
                               'show_comments': '1',
                               'date_format': 'M j, Y',
                               'content_length': 'excerpt',
                               'hover_overlay_icon': '',
                               'use_tax_query': '1',
                               'tax_query[0][taxonomy]': 'category',
                               'tax_query[0][terms][]': 'over-ear-open',
                               'tax_query[0][field]': 'slug',
                               'tax_query[0][operator]': 'IN',
                               'tax_query[0][include_children]': 'true'}

                    url = "https://audiobacon.net/wp-admin/admin-ajax.php"

                    yield FormRequest(url=url,
                                      callback=self.parse,
                                      formdata=frmdata,
                                      meta={'page': page,
                                            'cat': cat})

    def get_product_name_based_on_title(self, title):
        ''' This function will 'clean' the title of the review
            in order to get the product name '''
        p_name = title

        # Title begins with unnecessary sentence
        discart_beggings = ['Headphone Review: ',
                            "World's Best Electrostatic Headphones -"]

        for s in discart_beggings:
            if p_name.startswith(s):
                p_name = p_name.replace(s, '')

        # Spliting title
        if u' - ' in p_name:
            p_name = p_name.split(u' - ')[0]

        # Removing certain words
        words_to_remove = ['Headphone Review', 'Review']
        for w in words_to_remove:
            if w in title:
                p_name = p_name.replace(w, '')

        # Removing unnecessary spaces:
        p_name = p_name.replace('  ', ' ')
        p_name = p_name.strip()

        return p_name

    def parse_product_review(self, response):
        # print "     ...PARSE_PRODUCT_REVIEW: " + response.url

        title_xpath = '//meta[@property="og:title"]/@content'
        title = response.xpath(title_xpath).get()

        dont_scrape_words = ['Headphone Battle',
                             'Comparison',
                             'Comparisons']

        scrape = True
        for w in dont_scrape_words:
            if w in title:
                scrape = False
                break

        if scrape:
            # REVIEW ITEM --------------------------------------------------
            review_xpaths = {
                'TestTitle': '//meta[@property="og:title"]/@content',
                'TestSummary': '//meta[@property="og:description"]/@content',
            }

            # Create the review
            review = self.init_item_by_xpaths(response,
                                              "review",
                                              review_xpaths)

            # 'ProductName'
            r_title = review['TestTitle']
            review['ProductName'] = \
                self.get_product_name_based_on_title(r_title)

            # 'Author'
            review['Author'] = response.meta.get('author')

            # 'TestDateText'
            review['TestDateText'] = response.meta.get('date')

            # 'DBaseCategoryName'
            review['DBaseCategoryName'] = 'PRO'

            # 'source_internal_id'
            '''sid_xpath = '//link[@rel="shortlink"]/@href'
            sid = response.xpath(sid_xpath).get()
            sid = sid.split('?p=')[-1]
            review['source_internal_id'] = sid'''
            review['source_internal_id'] = response.meta.get('sid')

            # PRODUCT ITEM -------------------------------------------------
            product = ProductItem()
            product['source_internal_id'] = review['source_internal_id']
            product['OriginalCategoryName'] = response.meta.get('cat')
            product['ProductName'] = review['ProductName']

            pic_url_xpath = '//meta[@property="og:image"]/@content'
            pic_url = response.xpath(pic_url_xpath).get()
            product['PicURL'] = pic_url

            product['TestUrl'] = response.url

            yield review
            yield product
