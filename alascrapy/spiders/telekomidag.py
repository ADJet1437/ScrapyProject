# -*- coding: utf8 -*-

from datetime import datetime
from scrapy.http import Request
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem
import dateparser


class TelekomidagSpider(AlaSpider):
    name = 'telekomidag'
    allowed_domains = ['telekomidag.se']

    start_urls = ['http://telekomidag.se/avdelning/tester/']

    def __init__(self, *args, **kwargs):
        super(TelekomidagSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

    def parse(self, response):
        # print " 	...PARSE: " + response.url
        # print " --self.stored_last_date: " + str(self.stored_last_date)

        review_divs_xpath = '//div[contains(@class, "post-listed")]'
        review_divs = response.xpath(review_divs_xpath)

        for r_div in review_divs[:-1]:
            sid_xpath = './@id'
            sid = r_div.xpath(sid_xpath).get()
            # looks like this: post-123512
            sid = sid.split('-')[-1]

            # review url
            review_url_xpath = './/h2//a[@rel="bookmark"]/@href'
            review_url = r_div.xpath(review_url_xpath).get()

            yield Request(url=review_url,
                          callback=self.parse_product_review,
                          meta={'sid': sid,
                                'try_next_page': False})

        # This is the last post. We are both sending it for scraping
        # and also sending the URL of the next posts' list page
        # in case the date of the post is earlier than the
        # self.stored_last_date.
        next_page_url_xpath = '//div[@class="nav-previous"]/a/@href'
        next_page_url = None
        try:
            next_page_url = response.xpath(next_page_url_xpath).get()
        except:
            pass

        # source internal id
        sid_xpath = './@id'
        sid = review_divs[-1].xpath(sid_xpath).get()
        # looks like this: post-123512
        sid = sid.split('-')[-1]

        # review url
        review_url_xpath = './/h2//a[@rel="bookmark"]/@href'
        review_url = review_divs[-1].xpath(review_url_xpath).get()

        yield Request(url=review_url,
                      callback=self.parse_product_review,
                      meta={'sid': sid,
                            'try_next_page': True,
                            'next_page_url': next_page_url})

    def clean_product_name(self, p_name):
        # Spliting name
        get_first_piece = [u'Snittbetyg:', u'Totaltbetyg:']

        for g_f in get_first_piece:
            if g_f in p_name:
                p_name = p_name.split(g_f)[0]

        # Removing certain words
        words_to_remove = ['Fakta:', 'Fakta', 'Betyg', 'Betyg:', u'>>', ':']
        for w in words_to_remove:
            if w in p_name:
                p_name = p_name.replace(w, '')

        # Removing unnecessary spaces:
        p_name = p_name.replace('  ', ' ')
        p_name = p_name.strip()

        return p_name

    def parse_product_review(self, response):
        # print "     ...PARSE_PRODUCT_REVIEW: " + response.url

        # Check date of the review
        date_xpath = '(//span[@class="date"])[1]//text()'
        date = response.xpath(date_xpath).get()
        # Looks like: 23 april, 2018
        date = dateparser.parse(date,
                                date_formats=['%d %B, %Y'])

        if date and date > self.stored_last_date:

            p_name_xpath = '//ul[@id="factboxes"]//h3//text()'
            p_name = response.xpath(p_name_xpath).get()

            # Some products have their information compeltely locked for
            #   members. We scrape only the reviews that are not locked.
            if p_name:
                # REVIEW ITEM -------------------------------------------------
                review_xpaths = {
                    'TestTitle': '//meta[@property="og:title"]/@content',
                    'ProductName': '//ul[@id="factboxes"]//h3//text()',
                    'Author': '//span[@class="author"]//text()',
                    'TestSummary': '//meta[@name="description"]/@content',
                }

                # Create the review
                review = self.init_item_by_xpaths(response,
                                                  "review",
                                                  review_xpaths)

                # 'ProductName'
                p_name = review['ProductName']
                review['ProductName'] = self.clean_product_name(p_name)

                # 'TestDateText'
                review['TestDateText'] = date.strftime("%Y-%m-%d")

                # 'SourceTestScale' and 'SourceTestRating'
                ratings_xpath = '//div[@class="content"]/h3[text()="Betyg:"]'\
                                '/following-sibling::p//text()'
                ratings = response.xpath(ratings_xpath).getall()
                rating = None
                for r in ratings:
                    if 'Totalt:' in r:
                        r = r.replace('Totalt', '')
                        if ',' in r:
                            r = r.replace(',', '.')
                            # Remove everything from this string that is not a
                            #  number or a dot
                            r = ''.join(i for i in r if (i.isdigit() or
                                                         i == '.'))
                            rating = float(r)

                if rating:
                    review['SourceTestScale'] = 10
                    review['SourceTestRating'] = rating

                # 'DBaseCategoryName'
                review['DBaseCategoryName'] = 'PRO'

                # 'source_internal_id'
                review['source_internal_id'] = response.meta.get('sid')
                # -------------------------------------------------------------

                # PRODUCT ITEM ------------------------------------------------
                product = ProductItem()
                product['source_internal_id'] = review['source_internal_id']

                product['OriginalCategoryName'] = 'Unkown'
                product['ProductName'] = review['ProductName']

                pic_url_xpath = '//meta[@property="og:image"]/@content'
                pic_url = response.xpath(pic_url_xpath).get()
                product['PicURL'] = pic_url

                product['TestUrl'] = response.url
                # -------------------------------------------------------------

                if review['ProductName']:
                    yield review
                    yield product

            # Call parse again for the "next button"s URL in case the
            # last review ( response.meta.get('try_next_page') is True
            if response.meta.get('try_next_page'):
                url = response.meta.get('next_page_url')
                yield Request(url=url,
                              callback=self.parse)
