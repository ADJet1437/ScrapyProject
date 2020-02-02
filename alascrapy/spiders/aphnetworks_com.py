# -*- coding: utf8 -*-

from datetime import datetime
from scrapy.http import Request
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem


class Aphnetworks_comSpider(AlaSpider):
    name = 'aphnetworks_com'
    allowed_domains = ['aphnetworks.com']

    def __init__(self, *args, **kwargs):
        super(Aphnetworks_comSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

        # In order to test another stored_last_date
        # self.stored_last_date = datetime(1990, 2, 8)

    def start_requests(self):
        # print "     ...START_REQUESTS: "

        base_url = 'https://aphnetworks.com/reviews/'
        url_cat_dict = {'Camera': base_url + 'cameras',
                        'Headphone': base_url + 'personal_audio',
                        'CPU Cooler': base_url + 'cooling'
                        }

        for cat in url_cat_dict:
            yield Request(url=url_cat_dict[cat],
                          callback=self.parse,
                          meta={'cat': cat})

    def parse(self, response):
        # print "     ...PARSE: " + response.url
        # print " --self.stored_last_date: " + str(self.stored_last_date)

        review_urls_xpath = '//div[@class="field-item odd"]/p/a/@href'
        review_urls = response.xpath(review_urls_xpath).getall()
        cat = response.meta.get('cat')

        for r_url in review_urls:
            # r_url looks like: //aphnetworks.com/reviews/camorama
            review_url = 'https:' + r_url
            yield Request(url=review_url,
                          callback=self.parse_product_review,
                          meta={'cat': cat,
                                'request_from_1st_page': False})

    def get_product_name_based_on_title(self, title):
        ''' This function will 'clean' the title of the review
            in order to get the product name '''
        p_name = title

        # Spliting title
        get_first_piece = [u' | APH Networks',
                           '(Page']

        for g_f in get_first_piece:
            if g_f in p_name:
                p_name = p_name.split(g_f)[0]

        # Removing certain words
        if 'Review' in title:
            p_name = p_name.replace('Review', '')

        # Removing unnecessary spaces:
        p_name = p_name.replace('  ', ' ')
        p_name = p_name.strip()

        return p_name

    def get_review(self, response, scrape_all):

        date_xpath = '//div[@class="field-item odd"]/p/b/i//text()[2]'
        date = response.xpath(date_xpath).get()
        if date:
            if 'Previewed on' in date:
                date = date.replace('Previewed on', '')
            # date looks like: October 8, 2010
            date = date.strip()
            date = datetime.strptime(date, '%B %d, %Y')

        if date and date > self.stored_last_date:

            review_xpaths = {
                'TestTitle': '//title//text()',
            }

            # Create the review
            review = self.init_item_by_xpaths(response,
                                              "review",
                                              review_xpaths)

            # 'ProductName'
            title = review['TestTitle']
            pn = self.get_product_name_based_on_title(title)
            review['ProductName'] = pn

            # 'Author'
            author_xpath = '//div[@class="field-item odd"]'\
                           '/p/b/i//text()[1]'
            author = response.xpath(author_xpath).get()
            # author looks like: By: Jonathan Kwan
            author = author.replace('By:', '')
            author = author.strip()
            review['Author'] = author

            # 'TestDateText'
            review['TestDateText'] = date.strftime("%Y-%m-%d")

            # 'DBaseCategoryName'
            review['DBaseCategoryName'] = 'PRO'

            # 'source_internal_id'
            sid_xpath = '//link[@rel="shortlink"]/@href'
            sid = response.xpath(sid_xpath).get()
            sid = sid.split('/')[-1]
            review['source_internal_id'] = sid

            if scrape_all:
                # 'SourceTestScale' and 'SourceTestRating'
                rating_xpath = '//u/b/font//text()'
                rating = response.xpath(rating_xpath).get()
                if rating:
                    # rating looks like: 7.9/10
                    review['SourceTestRating'] = rating.split('/')[0]
                    review['SourceTestScale'] = 10

                # 'TestSummary'
                summary_xpath = '//p[u/b]//following-sibling::p//text()'
                summary = response.xpath(summary_xpath).get()
                if not summary:
                    summary_xpath = '//div[@class="field-item odd"]'\
                                    '/p[last()]//text()'
                    summary = response.xpath(summary_xpath).get()
                review['TestSummary'] = summary

                return review
            else:
                return review

    def get_product(self, response, review):
        if review:
            product = ProductItem()
            product['source_internal_id'] = review['source_internal_id']
            product['OriginalCategoryName'] = response.meta.get('cat')
            product['ProductName'] = review['ProductName']

            pic_url_xpath = '//img/@src'
            pic_url = response.xpath(pic_url_xpath).getall()
            pic_url = pic_url[1]
            product['PicURL'] = 'https:' + pic_url

            product['TestUrl'] = response.url

            return product
        else:
            return None

    def parse_product_review(self, response):
        # print "     ...PARSE_PRODUCT_REVIEW: " + response.url

        request_from_1st_page = response.meta.get('request_from_1st_page')

        # FROM SELF.PARSE()
        # If we got here from a call from self.parse().
        if not request_from_1st_page:
            # print "     -- call from PARSE"
            final_page_url_xpath = '//a[text()="Conclusion"]/@href'
            final_page_url = response.xpath(final_page_url_xpath).get()

            # SINGLE PAGE REVIEW
            # If it's a single page review:
            # e.g: https://aphnetworks.com/reviews/antec_spot_cool
            if not final_page_url:
                # print "     -- SINGLE PAGE REVIEW"

                review = self.get_review(response, True)
                product = self.get_product(response, review)

                yield review
                yield product

            # MULTIPLE PAGES REVIEW
            # If the review has multiple pages
            # e.g: https://aphnetworks.com/reviews/d-link-dcs-8010-lh
            else:
                # print "     -- MULTIPLE PAGES REVIEW"

                review = self.get_review(response, False)

                cat = response.meta.get('cat')
                yield Request(url='https:' + final_page_url,
                              callback=self.parse_product_review,
                              meta={'review': review,
                                    'request_from_1st_page': True,
                                    'cat': cat})

        # REQUEST FROM 1ST PAGE
        else:
            # print "     -- call from 1ST PAGE"
            review = response.meta.get('review')

            # 'SourceTestScale' and 'SourceTestRating'
            rating_xpath = '//u/b/font//text()'
            rating = response.xpath(rating_xpath).get()
            if rating:
                # rating looks like: 7.9/10
                review['SourceTestRating'] = rating.split('/')[0]
                review['SourceTestScale'] = 10

            # 'TestSummary'
            summary_xpath = '//p[u/b]//following-sibling::p//text()'
            summary = response.xpath(summary_xpath).get()
            if not summary:
                summary_xpath = '//div[@class="field-item odd"]'\
                                '/p[last()]//text()'
                summary = response.xpath(summary_xpath).get()
            review['TestSummary'] = summary

            product = self.get_product(response, review)

            yield review
            yield product
