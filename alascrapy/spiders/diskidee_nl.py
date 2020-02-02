# -*- coding: utf8 -*-

from datetime import datetime
from scrapy.http import Request
from scrapy.http import FormRequest
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem, ProductIdItem
import json


class Diskidee_nlSpider(AlaSpider):
    name = 'diskidee_nl'
    allowed_domains = ['diskidee.be']

    page = 1

    frmdata = {'action': 'extra_blog_feed_get_content',
               'action': 'td_ajax_loop',
               'loopState[sidebarPosition]': '',
               'loopState[moduleId]': '16',
               'loopState[currentPage]': '',
               'loopState[max_num_pages]': '484',
               'loopState[atts][category_id]': '10',
               'loopState[atts][offset]': '7',
               'loopState[ajax_pagination_infinite_stop]': '3',
               'loopState[server_reply_html_data]': ''}

    post_request_url = \
        "https://www.diskidee.be/wp-admin/admin-ajax.php?td_theme_" \
        "name=Newspaper&v=9.5"

    def __init__(self, *args, **kwargs):
        super(Diskidee_nlSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

        # In order to test another stored_last_date
        # self.stored_last_date = datetime(2018, 2, 8)

    def start_requests(self):
        # print "     ...START_REQUESTS: "
        # print "     - PAGE: " + str(self.page)

        self.frmdata['loopState[currentPage]'] = str(self.page)
        yield FormRequest(url=self.post_request_url,
                          callback=self.parse,
                          formdata=self.frmdata)

    def parse(self, response):
        # print "     ...PARSE: " + response.url
        # print " --self.stored_last_date: " + str(self.stored_last_date)

        js = json.loads(response.body)

        response = response.replace(body=js["server_reply_html_data"])

        review_divs_xpath = '//div[@class="td_module_16 td_module_wrap '\
                            'td-animation-stack td-meta-info-hide"]'
        review_divs = response.xpath(review_divs_xpath)

        review_url_xpath = './/h3[@class="entry-title td-module-title"]'\
                           '/a[@rel="bookmark"]/@href'

        for r_div in review_divs[:-1]:
            review_url = r_div.xpath(review_url_xpath).get()

            yield Request(url=review_url,
                          callback=self.parse_product_review,
                          meta={'check_for_next_page': False})

        # The last review of the 'page'
        review_url = review_divs[-1].xpath(review_url_xpath).get()
        yield Request(url=review_url,
                      callback=self.parse_product_review,
                      meta={'check_for_next_page': True})

    def parse_product_review(self, response):
        # print "     ...PARSE_PRODUCT_REVIEW: " + response.url

        # Category
        classes_xpath = '//article/@class'
        classes = response.xpath(classes_xpath).get()
        classes = classes.split(' ')
        cat = None
        if 'tag-smartphones' in classes:
            cat = 'Smartphone'
        elif 'tag-headsets' in classes:
            cat = 'Headphone'
        elif 'tag-laptops' in classes:
            cat = 'Laptop'
        elif ('tag-laserprinters' in classes) or \
             ('tag-printers' in classes) or \
             ('tag-inkjetprinters' in classes):
            cat = 'Printer'
        elif 'tag-scanners' in classes:
            cat = 'Scanner'
        elif 'tag-tablets' in classes:
            cat = 'Tablet'
        elif 'tag-desktops' in classes:
            cat = 'Desktop PC'

        # Checking the date
        date_xpath = '//time[@class="entry-date updated td-module-date"]'\
                     '/@datetime'
        date = response.xpath(date_xpath).get()
        # date looks like: 2019-02-22T11:07:05+00:00
        date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S+00:00')

        if date > self.stored_last_date and cat:
            js_xpath = '(//script[@type="application/ld+json"])'\
                       '[last()]//text()'
            js = response.xpath(js_xpath).get()
            js = json.loads(js)

            # REVIEW ITEM -------------------------------------------------
            review_xpaths = {
                'TestTitle': '//meta[@itemprop="headline "]/@content',
                'TestVerdict': '//span[@class="conclusietxt"]//text()',
                'TestSummary': '//meta[@name="description"]/@content'
            }

            # Create the review
            review = self.init_item_by_xpaths(response,
                                              "review",
                                              review_xpaths)

            # 'ProductName'
            p_name = js["review"]["name"]
            review['ProductName'] = p_name

            # 'Author'
            review['Author'] = js["review"]["author"]["name"]

            # 'TestDateText'
            review['TestDateText'] = date.strftime("%Y-%m-%d")

            # 'SourceTestScale' and 'SourceTestRating'
            review['SourceTestRating'] = \
                js["review"]["reviewRating"]["ratingValue"]

            if review['SourceTestRating']:
                review['SourceTestScale'] = \
                    js["review"]["reviewRating"]["bestRating"]

            # 'DBaseCategoryName'
            review['DBaseCategoryName'] = 'PRO'

            # 'TestPros' 'TestCons'
            pros_xpath = '//div[@class=" pros"]/ul/li//text()'
            pros = response.xpath(pros_xpath).getall()
            pros = ";".join(pros)

            cons_xpath = '//div[@class=" cons"]/ul/li//text()'
            cons = response.xpath(cons_xpath).getall()
            cons = ";".join(cons)

            review['TestPros'] = pros
            review['TestCons'] = cons

            # 'source_internal_id'
            sid = response.url.split('/')[-2]
            review['source_internal_id'] = sid
            # -------------------------------------------------------------

            # PRODUCT ITEM ------------------------------------------------
            product = ProductItem()
            product['source_internal_id'] = review['source_internal_id']

            product['OriginalCategoryName'] = cat
            product['ProductName'] = review['ProductName']

            pic_url_xpath = '//meta[@property="og:image"]/@content'
            pic_url = response.xpath(pic_url_xpath).get()
            product['PicURL'] = pic_url

            product['TestUrl'] = response.url
            # -------------------------------------------------------------

            # PRODUCT ID ITEM ---------------------------------------------
            price = js["offers"]["price"] + js["offers"]["priceCurrency"]
            if price:
                productId = ProductIdItem.from_product(product,
                                                       kind='price',
                                                       value=price)
            # -------------------------------------------------------------

            yield review
            yield product
            yield productId

        # If this is the last review of the page we should check whether
        #  we should scrape the next page.
        if response.meta.get('check_for_next_page') and \
           date > self.stored_last_date:

            self.page += 1

            self.frmdata['loopState[currentPage]'] = str(self.page)
            yield FormRequest(url=self.post_request_url,
                              callback=self.parse,
                              formdata=self.frmdata)
