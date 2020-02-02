# -*- coding: utf8 -*-

from datetime import datetime
from scrapy.http import Request
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem, ProductIdItem


class BestvacuuminfoSpider(AlaSpider):
    name = 'bestvacuuminfo'
    allowed_domains = ['bestvacuuminfo.com']

    def __init__(self, *args, **kwargs):
        super(BestvacuuminfoSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

        # In order to test another stored_last_date
        # self.stored_last_date = datetime(2018, 2, 8)

    def start_requests(self):
        # print " 	...START_REQUESTS: "

        url_cat_dict = {'Vacuum Cleaner':
                        'https://bestvacuuminfo.com/reviews/',
                        'Robotic Vacuum Cleaner':
                        'https://bestvacuuminfo.com/robotic/'}

        for cat in url_cat_dict:
            yield Request(url=url_cat_dict[cat],
                          callback=self.parse,
                          meta={'cat': cat})

    def parse(self, response):
        # print " 	...PARSE: " + response.url
        # print " --self.stored_last_date: " + str(self.stored_last_date)

        review_urls_xpath = '//article[not(@class)]/div/a[1]/@href'
        review_urls = response.xpath(review_urls_xpath).getall()

        for r_url in review_urls[:-1]:
            yield Request(url=r_url,
                          callback=self.parse_product_review,
                          meta={'try_next_page': False,
                                'cat': response.meta.get('cat')})

        # This is the last post. We are both sending it for scraping
        # and also sending the URL of the next posts' list page
        # in case the date of the post is earlier than the
        # self.stored_last_date.
        next_page_url_xpath = '//a[@class="next page-numbers"]/@href'
        next_page_url = None
        try:
            next_page_url = response.xpath(next_page_url_xpath).get()
        except:
            pass

        yield Request(url=review_urls[-1],
                      callback=self.parse_product_review,
                      meta={'try_next_page': True,
                            'next_page_url': next_page_url,
                            'cat': response.meta.get('cat')})

    def get_product_name_based_on_title(self, title):
        ''' This function will 'clean' the title of the review
            in order to get the product name '''
        p_name = title

        # Spliting title
        get_first_piece = [u':', u' - ', u' – ']
        for g_f in get_first_piece:
            if g_f in p_name:
                p_name = p_name.split(g_f)[0]

        # Removing certain words
        words_to_remove = ['Review']
        for w in words_to_remove:
            if w in title:
                p_name = p_name.replace(w, '')

        # Removing unnecessary spaces:
        p_name = p_name.replace('  ', ' ')
        p_name = p_name.strip()

        return p_name

    def parse_product_review(self, response):
        # print "     ...PARSE_PRODUCT_REVIEW: " + response.url

        date_xpath = '//meta[@property="og:updated_time"]/@content'
        date = response.xpath(date_xpath).get()
        date = date.split('T')[0]
        date = datetime.strptime(date, '%Y-%m-%d')

        if date > self.stored_last_date:
            # REVIEW ITEM -----------------------------------------------------
            review_xpaths = {
                'TestTitle': '//meta[@property="og:title"]/@content',
                'TestSummary': '//meta[@property="og:description"]/@content',
            }

            # Create the review
            review = self.init_item_by_xpaths(response,
                                              "review",
                                              review_xpaths)

            # 'ProductName'
            title = review['TestTitle']
            review['ProductName'] = self.get_product_name_based_on_title(title)

            # 'Author'
            review['Author'] = None

            # 'TestDateText'
            review['TestDateText'] = date.strftime("%Y-%m-%d")

            # 'SourceTestScale' and 'SourceTestRating'
            review['SourceTestScale'] = None
            review['SourceTestRating'] = None

            # 'DBaseCategoryName'
            review['DBaseCategoryName'] = 'PRO'

            # 'TestPros' and 'TestCons'
            pros_xpath = '//h3[text()="Pros"]/following-sibling::ul/li//text()'
            pros = response.xpath(pros_xpath).getall()
            if not pros:
                pros_xpath = '//h2[text()="Pros"]/following-sibling'\
                             '::ul/li//text()'
                pros = response.xpath(pros_xpath).getall()
            pros = ";".join(pros)
            review['TestPros'] = pros

            cons_xpath = '//h3[text()="Cons"]/following-sibling::p//text()'
            cons = response.xpath(cons_xpath).get()
            if not cons:
                cons_xpath = '//h2[text()="Cons"]/following-sibling::p//text()'
                cons = response.xpath(cons_xpath).get()
            review['TestCons'] = cons

            # 'source_internal_id'
            sid_xpath = '//link[@rel="shortlink"]/@href'
            sid = response.xpath(sid_xpath).get()
            # sid looks like this: https://wp.me/paNYQ4-7x
            sid = sid.split('/')[-1]
            review['source_internal_id'] = sid
            # -----------------------------------------------------------------

            # PRODUCT ITEM ----------------------------------------------------
            product = ProductItem()
            product['source_internal_id'] = review['source_internal_id']

            product['OriginalCategoryName'] = response.meta.get('cat')
            product['ProductName'] = review['ProductName']

            pic_url_xpath = '//meta[@property="og:image"]/@content'
            pic_url = response.xpath(pic_url_xpath).get()
            product['PicURL'] = pic_url

            product['TestUrl'] = response.url
            # -----------------------------------------------------------------

            # PRICE ITEM ------------------------------------------------------
            price_xpath = '//span[@class="aalb-pa-product-'\
                          'offer-price-value"]//text()'
            price = response.xpath(price_xpath).get()
            if price:
                key_words = ['Check on Amazon', 'Out of stock']
                has_price = True
                for w in key_words:
                    if w in price:
                        has_price = False

                if has_price:
                    yield ProductIdItem.from_product(product,
                                                     kind='price',
                                                     value=price)
            # -----------------------------------------------------------------

            yield review
            yield product

        # Call parse again for the "next button"s URL in case the
        # last review (response.meta.get('try_next_page') is True in
        # case this is the last review of the page) is earlier
        # than self.stored_last_date
        if response.meta.get('try_next_page') and \
           response.meta.get('next_page_url'):
            if date > self.stored_last_date:
                url = response.meta.get('next_page_url')
                yield Request(url=url,
                              callback=self.parse,
                              meta={'cat': response.meta.get('cat')})
