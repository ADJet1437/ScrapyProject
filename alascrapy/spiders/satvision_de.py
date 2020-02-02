# -*- coding: utf8 -*-

import re
import dateparser
from datetime import datetime
from scrapy.http import Request
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem


class Satvision_deSpider(AlaSpider):
    name = 'satvision_de'
    allowed_domains = ['satvision.de']

    # Monitors
    start_urls = ['https://satvision.de/tests/fernseher/']

    def __init__(self, *args, **kwargs):
        super(Satvision_deSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

        # In order to test another stored_last_date
        # self.stored_last_date = datetime(2018, 2, 8)

    def parse(self, response):
        # print "     ...PARSE: " + response.url
        # print " --self.stored_last_date: " + str(self.stored_last_date)

        review_lis_xpath = '//li[contains(@class, "fc_bloglist_item")]'
        review_lis = response.xpath(review_lis_xpath)

        date = None
        for r_li in review_lis:
            date_xpath = './/div[@class="beitragsinfo"]//text()'
            date = r_li.xpath(date_xpath).get()

            # date looks like:
            # Heft 04/2019
            # or
            # 22. November 2018
            if 'Heft' in date:  # Heft 04/2019
                date = date.replace('Heft', '')
                date = date.strip()
                date = datetime.strptime(date, '%m/%Y')
            else:  # 22. November 2018
                try:
                    date = datetime.strptime(date, '%d. %B %Y')
                except:
                    try:
                        date = dateparser.parse(date,
                                                date_formats=['%d. %B %Y'],
                                                languages=['de', 'es'])
                    except:
                        pass

            if date and date > self.stored_last_date:
                # check whether the review is about more than one product
                metadata_xpath = './/div[@class="beitragsinfo"]//text()'
                metadata = r_li.xpath(metadata_xpath).getall()

                match = re.findall(r'[0-9] Produkte im Test', metadata[-1])
                # In case the review is about only one produce:
                if not match:
                    review_url_xpath = './/div[@class="image_descr"]/a/@href'
                    review_url = r_li.xpath(review_url_xpath).get()

                    yield response.follow(url=review_url,
                                          callback=self.parse_product_review,
                                          meta={'date':
                                                date.strftime("%Y-%m-%d")})

        # Checking whether we should scrape the next page
        if date and date > self.stored_last_date:
            next_page_url_xpath = '//a[text()="Weiter"]/@href'
            next_page_url = response.xpath(next_page_url_xpath).get()

            yield response.follow(url=next_page_url,
                                  callback=self.parse,
                                  meta={'date':
                                        date.strftime("%Y-%m-%d")})

    def get_product_name_based_on_title(self, title):
        ''' This function will 'clean' the title of the review
            in order to get the product name '''
        p_name = title

        # Title begins with unnecessary sentence
        discart_beggings = ['ok.',
                            'Ok.',
                            'Preview:',
                            'Test:',
                            'Exklusiv:']

        for s in discart_beggings:
            if p_name.startswith(s):
                p_name = p_name.replace(s, '')

        # Removing certain words
        words_to_remove = ['im Test',
                           'zum Sparpreis',
                           'oled in der Preview',
                           'im Vorab-Test',
                           'in der Preview']

        for w in words_to_remove:
            if w in title:
                p_name = p_name.replace(w, '')

        # Removing unnecessary spaces:
        p_name = p_name.replace('  ', ' ')
        p_name = p_name.strip()

        return p_name

    def parse_product_review(self, response):
        # print "     ...PARSE_PRODUCT_REVIEW: " + response.url

        p_name_xpath = '//meta[@name="title"]/@content'
        p_name = response.xpath(p_name_xpath).get()
        if 'vs.' in p_name.split(' '):
            return

        # REVIEW ITEM ------------------------------------------------------
        review_xpaths = {
            'TestTitle': '//p[@class="subline"]//text()',
            'TestSummary': '//meta[@name="description"]/@content',
        }

        # Create the review
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        # 'TestSummary'
        if not review['TestSummary']:
            summary_xpath = '//meta[@property="og:description"]/@content'
            summary = response.xpath(summary_xpath).get()
            review['TestSummary'] = summary

        # 'ProductName'
        p_name = self.get_product_name_based_on_title(p_name)
        review['ProductName'] = p_name

        # 'Author'
        author_xpath = '(//div[@class="beitragsinfo"])[1]//text()'
        author = response.xpath(author_xpath).getall()[-1]
        review['Author'] = author

        # 'TestDateText': '',
        review['TestDateText'] = response.meta.get('date')

        # 'DBaseCategoryName'
        review['DBaseCategoryName'] = 'PRO'

        # 'source_internal_id'
        sid = response.url.split('-')[-1]
        review['source_internal_id'] = sid
        # ------------------------------------------------------------------

        # PRODUCT ITEM -----------------------------------------------------
        product = ProductItem()
        product['source_internal_id'] = review['source_internal_id']
        product['OriginalCategoryName'] = 'Monitor'
        product['ProductName'] = review['ProductName']

        pic_url_xpath = '//meta[@property="og:image"]/@content'
        pic_url = response.xpath(pic_url_xpath).get()
        product['PicURL'] = pic_url

        product['TestUrl'] = response.url
        # ------------------------------------------------------------------

        yield review
        yield product
