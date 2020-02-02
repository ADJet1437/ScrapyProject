# -*- coding: utf8 -*-

from datetime import datetime
from scrapy.http import Request
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem
from scrapy.http import FormRequest


class IndianexpressSpider(AlaSpider):
    name = 'indianexpress'
    allowed_domains = ['indianexpress.com']
    start_urls = ['http://indianexpress.com/section/technology/tech-reviews/']

    page_number = 1

    def __init__(self, *args, **kwargs):
        super(IndianexpressSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

        # In order to test another stored_last_date
        # self.stored_last_date = datetime(2018, 2, 8)

    def parse(self, response):
        # print " 	...PARSE: " + response.url
        # print " --self.stored_last_date: " + str(self.stored_last_date)
        # print "     self.page_number: " + str(self.page_number)

        review_divs_xpath = '//div[@class="l-grid__item '\
                            'l-grid__item--divided"]'
        review_divs = response.xpath(review_divs_xpath)

        date = None
        for r_div in review_divs:
            date_xpath = './/time/@datetime'
            date = r_div.xpath(date_xpath).get()
            # date looks like: 2019-06-12 08:16:13+05:30
            date = date.split(' ')[0]
            date = datetime.strptime(date, '%Y-%m-%d')

            if date > self.stored_last_date:
                review_url_xpath = './/a[1]/@href'
                review_url = r_div.xpath(review_url_xpath).get()

                yield Request(url=review_url,
                              callback=self.parse_product_review,
                              meta={'date': date.strftime("%Y-%m-%d")})

        # Checking whether we should search for new items
        if date and date > self.stored_last_date:
            self.page_number += 1
            frmdata = {'action': 'ie_load_more',
                       'next_page': str(self.page_number),
                       'exclude_id': '',
                       'query': '{"post_type":"article","tax_query":'
                                '[{"taxonomy":"ie_section","field":"slug",'
                                '"terms":"tech-reviews"}],"posts_per_page":12,'
                                '"orderby":"post_modified"}',
                       'template': 'template-parts/partials/listings/'
                                   'listing.php',
                       'story_id': '0',
                       'ie_secure': '9d9a76049d',
                       }

            url = "https://indianexpress.com/wp-admin/admin-ajax.php"

            yield FormRequest(url=url,
                              callback=self.parse,
                              formdata=frmdata)

    def get_product_name_based_on_title(self, title):
        ''' This function will 'clean' the title of the review
            in order to get the product name '''
        p_name = title

        # Spliting title
        get_first_piece = [u'review:', u'Review', u':']

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
            'Author': '//meta[@itemprop="author"]/@content',
            'TestSummary': '//meta[@property="og:description"]/@content',
                        }

        # Create the review
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        # 'ProductName'
        title = review['TestTitle']
        review['ProductName'] = self.get_product_name_based_on_title(title)

        # 'TestDateText'
        review['TestDateText'] = response.meta.get('date')

        # 'DBaseCategoryName'
        review['DBaseCategoryName'] = 'PRO'

        # 'SourceTestScale' and 'SourceTestRating'
        rating_xpath = '//span[@class="m-review-stars__label"]//text()'
        rating = response.xpath(rating_xpath).get()
        if rating:
            review['SourceTestScale'] = 5
            review['SourceTestRating'] = rating

        # 'source_internal_id'
        sid_xpath = '//link[@rel="shortlink"]/@href'
        sid = response.xpath(sid_xpath).get()
        # sid looks like: href="https://wp.me/p3DY9j-onsE"
        sid = sid.split('-')[-1]
        review['source_internal_id'] = sid
        # ------------------------------------------------------------------

        # PRODUCT ITEM -----------------------------------------------------
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
