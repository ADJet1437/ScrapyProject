
# -*- coding: utf8 -*-

from datetime import datetime
from scrapy.http import Request
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem


class CdrinfoSpider(AlaSpider):
    name = 'cdrinfo'
    allowed_domains = ['cdrinfo.com']

    start_urls = ['https://cdrinfo.com/d7/reviews']

    def __init__(self, *args, **kwargs):
        super(CdrinfoSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

        # In order to test another stored_last_date
        # self.stored_last_date = datetime(2000, 2, 8)

    def parse(self, response):
        # print " 	...PARSE: " + response.url
        # print " --self.stored_last_date: " + str(self.stored_last_date)

        review_lis_xpath = '//div[@class="item"]//li'
        review_lis = response.xpath(review_lis_xpath)

        for r_li in review_lis:
            date_xpath = './/time//text()'
            date = r_li.xpath(date_xpath).get()
            # date looks like: May 6, 2019
            if date:  # if date is none, this is an ad
                date = datetime.strptime(date, '%b %d, %Y')

                if date > self.stored_last_date:
                    review_url_xpath = './/div[@class="block-side"]/a/@href'
                    review_url = r_li.xpath(review_url_xpath).get()

                    review_title_xpath = './/h3[@class="block-heading"]'\
                                         '//a//text()'
                    review_title = r_li.xpath(review_title_xpath).get()

                    img_xpath = './/img/@src'
                    img = r_li.xpath(img_xpath).get()
                    img = "https://cdrinfo.com" + img

                    yield response.follow(url=review_url,
                                          callback=self.parse_product_review,
                                          meta={'date': date.strftime(
                                              "%Y-%m-%d"),
                                                'review_title': review_title,
                                                'img_url': img})

        # Check next pages
        next_page_url_xpath = '//a[@title="Go to next page"]//@href'
        next_page_url = response.xpath(next_page_url_xpath).get()
        if next_page_url:
            yield response.follow(url=next_page_url,
                                  callback=self.parse)

    def parse_product_review(self, response):
        # print "     ...PARSE_PRODUCT_REVIEW: " + response.url

        # REVIEW ITEM ----------------------------------------------
        # Create the review item
        review = ReviewItem()

        # 'TestTitle'
        review['TestTitle'] = response.meta.get('review_title')

        # 'ProductName'
        p_name = review['TestTitle']
        words_to_remove = ['Review: ', 'review']
        for w in words_to_remove:
            if w in p_name:
                p_name = p_name.replace(w, '')
        p_name = p_name.strip()
        review['ProductName'] = p_name

        # 'TestDateText'
        review['TestDateText'] = response.meta.get('date')

        # 'TestSummary'
        summary_xpath = 'string(//div[@class="field field-name-site-article-'\
                        'page-content field-type-ds field-label-hidden"]'\
                        '//div[@class="field-item even"]/p[1])'
        summary = response.xpath(summary_xpath).get()
        remove = ['  ', '\r', '\n']
        for w in remove:
            if w in summary:
                summary = summary.replace(w, '')
        review['TestSummary'] = summary

        # 'DBaseCategoryName'
        review['DBaseCategoryName'] = 'PRO'

        # 'source_internal_id'
        sid_xpath = '//link[@rel="shortlink"]/@href'
        sid = response.xpath(sid_xpath).get()
        # sid looks like: "/d7/node/47999"
        sid = sid.split('/')[-1]
        review['source_internal_id'] = sid

        # 'TestUrl'
        review['TestUrl'] = response.url
        # ----------------------------------------------------------

        # product ITEM ---------------------------------------------
        product = ProductItem()
        product['source_internal_id'] = review['source_internal_id']
        product['OriginalCategoryName'] = None
        product['ProductName'] = review['ProductName']

        product['PicURL'] = response.meta.get('img_url')
        product['TestUrl'] = response.url
        # ----------------------------------------------------------

        # Get the last page of the review
        last_page_url_xpath = '//div[@class="field field-name-site-article'\
                              '-pages-top field-type-ds field-label-hidden"]'\
                              '//span[last()]/a/@href'
        last_page_url = response.xpath(last_page_url_xpath).get()

        # In case this review has multiple pages, let's scrape the last one
        if last_page_url:
            yield Request(url=last_page_url,
                          callback=self.parse_product_review2,
                          meta={'date': response.meta.get('date'),
                                'review_item': review,
                                'product_item': product})

        # In case this review doesn't have multiple pages.
        else:
            yield review
            yield product

    def parse_product_review2(self, response):
        # print "     ...PARSE_PRODUCT_REVIEW2: " + response.url

        review = response.meta.get('review_item')
        product = response.meta.get('product_item')

        # 'TestPros' and 'TestCons'
        # PROS ----------------------------------------------
        pros_xpath = '//p[strong[text()=" Strengths"]]'\
                     '//following-sibling::ul/li//text()'
        pros = response.xpath(pros_xpath).getall()

        if not pros:
            pros_xpath = '//p[em[text()="Positive"]]//'\
                         'following-sibling::ul[1]/li//text()'
            pros = response.xpath(pros_xpath).getall()

        if not pros:
            pros_xpath = '//p[font[strong[text()=" Positive"]]]/'\
                         'following-sibling::ul[1]/li//text()'
            pros = response.xpath(pros_xpath).getall()
        # ---------------------------------------------------

        # CONS ----------------------------------------------
        cons_xpath = '//p[strong[text()="Weaknesses"]]//'\
                     'following-sibling::ul/li//text()'
        cons = response.xpath(cons_xpath).getall()

        if not cons:
            cons_xpath = '//p[em[text()="Negative"]]//'\
                        'following-sibling::ul[1]/li//text()'
            cons = response.xpath(cons_xpath).getall()

        if not cons:
            cons_xpath = '//p[font[strong[text()="Negative"]]]'\
                         '/following-sibling::ul[1]/li//text()'
            cons = response.xpath(cons_xpath).getall()
        # ---------------------------------------------------

        if not pros:
            pros_xpath = 'string(//p[em[text()="Positive"]]'\
                         '//following-sibling::p[1])'
            pros = response.xpath(pros_xpath).get()

            cons = None
            if 'Negatives' in pros:
                cons = pros.split('Negatives')[1]
                pros = pros.split('Negatives')[0]

            if not cons:
                cons_xpath = 'string(//p[em[text()="Positive"]]'\
                            '//following-sibling::p[2])'
                cons = response.xpath(cons_xpath).get()

            if '*' in pros:
                pros = pros.split('*')

            if cons:
                if '-' in cons:
                    cons = cons.split('-')

        if pros and cons:
            remove = ['  ', '\r', '\n']
            pros = ';'.join(pros)
            cons = ';'.join(cons)

            for w in remove:
                if w in pros:
                    pros = pros.replace(w, '')
                if w in cons:
                    cons = cons.replace(w, '')
            pros = pros.strip()
            cons = cons.strip()

            if pros.startswith(';'):
                pros = pros[1:]
                pros = pros.strip()
            if cons.startswith(';'):
                cons = cons[1:]
                cons = cons.strip()

        review['TestPros'] = pros
        review['TestCons'] = cons

        yield review
        yield product
