# -*- coding: utf8 -*-
from datetime import datetime

from scrapy.http import Request

import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.items import ProductItem, ReviewItem


class Chip_deSpider(AlaSpider):
    name = 'chip_de'
    allowed_domains = ['chip.de']

    def __init__(self, *args, **kwargs):
        super(Chip_deSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

        # In order to test another stored_last_date
        # self.stored_last_date = datetime(2018, 2, 8)

    def start_requests(self):
        # print "     ...START_REQUESTS"

        categories_to_scrape = {
            'notebook': 'https://www.chip.de/tests/notebook,14933',
            'smartphone': 'https://www.chip.de/handy',
            'printer': 'https://www.chip.de/tests/drucker-scanner,43736',
            'monitors': 'https://www.chip.de/tests/tft-monitor,14945',
            'tablet': 'https://www.chip.de/tests/tablet-pc,64445',
            'camera': 'https://www.chip.de/tests/digitalkamera,43744',
            'headphone': 'https://www.chip.de/tests/kopfhoerer,90885',
            'smartwatch': 'https://www.chip.de/tests/smartwatch,106298',
        }

        for category in categories_to_scrape:
            yield Request(url=categories_to_scrape[category],
                          callback=self.parse,
                          meta={'category': category})

    def parse(self, response):
        # print "     ...PARSE: " + response.url

        # REVIEWS IN THE TOP --------------------------------------------------
        reviews_on_top_xpath = '//section[@class="fb fb-align-content-start '\
                               'unit-block-1"]//article//a/@href'

        reviews_on_top_urls = response.xpath(reviews_on_top_xpath).getall()

        # It's not possible to detect whether the first 3 posts are reviews
        #  or not.
        for url in reviews_on_top_urls:
            category = response.meta.get('category')
            yield Request(url=url,
                          callback=self.parse_product_review,
                          meta={'category': category})
        # ---------------------------------------------------------------------

        # REVIEWS IN THE BOTTOM -----------------------------------------------
        posts_li_xpath = '//div[@class="Listing"]//ul//li'
        posts_li = response.xpath(posts_li_xpath)

        for p_li in posts_li:
            post_type_xpath = './/figcaption//div//div//text()'
            post_type = p_li.xpath(post_type_xpath).get()

            # If the post is an actual review.
            if post_type == "Testbericht" or post_type == "Test":
                review_url_xpath = './/a/@href'
                review_url = p_li.xpath(review_url_xpath).get()

                category = response.meta.get('category')
                yield Request(url=review_url,
                              callback=self.parse_product_review,
                              meta={'category': category})
        # ---------------------------------------------------------------------

        # CHECKING WHETHER THE NEXT PAGE SHOULD BE SCRAPED --------------------
        next_page_button_xpath = '//a[@class="Button Button--Pagination '\
                                 'Button--Primary is-next "]/@href'
        next_page_url = response.xpath(next_page_button_xpath).get()

        # If there's a next page possibility, let's check the date of the last
        # review.
        if next_page_url:
            last_review_date_xpath = '//div[@class="Listing"]//ul//li[last()]'\
                                    '//a//time//text()'
            last_date = response.xpath(last_review_date_xpath).get()
            last_date = datetime.strptime(last_date, "%d.%m.%Y")

            if last_date > self.stored_last_date:
                category = response.meta.get('category')
                yield response.follow(url=next_page_url,
                                      callback=self.parse,
                                      meta={'category': category})
        # ---------------------------------------------------------------------

    def parse_product_review(self, response):
        # print "     ...PARSE_PRODUCT_REVIEW: " + response.url

        # The website doesn't have a clear way of distinguishing an actual
        # review from a comparison. We try to refine that by trying to find the
        # 'Vergleich'(comparison) word in the title and discarting the post in
        # that case.
        post_title_xpath = '//h1[@class="Article__Title hl-lg"]//text()'
        post_title = response.xpath(post_title_xpath).get()

        # There are 2 possible ways of tagging the title in their website
        if not post_title:
            post_title_xpath = '//h1[@class="TestReport__Title hl-lg"]//text()'
            post_title = response.xpath(post_title_xpath).get()

        if post_title and ('Vergleich' not in post_title):
            review_xpaths = {
                'ProductName': '//a[@class="arrow Link Link--Pv  cart "]'
                               '/@title',
                'Author': '//span[@itemprop="author"]//text()',
                'TestSummary': '//meta[@property="og:description"]/@content',
            }

            review = self.init_item_by_xpaths(response, "review",
                                              review_xpaths)

            review['TestTitle'] = post_title

            # Sometimes the productName is not clearly available.
            # Below are our tried to extract it in diff ways.
            # The last option is to set it to 'TestTitle'
            if not review['ProductName']:
                p_name_xpath = '//a[@class="arrow Link Link--Pv  cart "]'\
                               '/@title'
                p_name = response.xpath(p_name_xpath).get()
                if p_name:
                    review['ProductName'] = p_name
                else:
                    review['ProductName'] = review['TestTitle']

                words_to_remove = ['im Test in',
                                   'im Test']

                for word in words_to_remove:
                    if word in review['ProductName']:
                        npn = review['ProductName'].replace(word, "")
                        review['ProductName'] = npn

                review['ProductName'] = review['ProductName'].strip()

            # 'TestDateText'
            date_xpath = '//time/@datetime'
            date = response.xpath(date_xpath).get()
            date = date.split(' ')[0]
            date = datetime.strptime(date, '%d.%m.%Y')
            date = date.strftime("%Y-%m-%d")
            review['TestDateText'] = date

            # 'SourceTestRating'  and  'SourceTestScale'
            t_rating_xpath = '//div[contains(@class, "RatingChip__Progress")]'\
                             '//text()'
            test_rating = response.xpath(t_rating_xpath).get()
            if test_rating:
                test_rating = test_rating.replace("%", '')
                review['SourceTestRating'] = test_rating
                review['SourceTestScale'] = 100

            review['DBaseCategoryName'] = 'PRO'

            # 'TestPros' and 'TestCons'
            pros_xpath = '//dl[@class="List List--Definition is-pro"]'\
                         '//dd//text()'
            pros = response.xpath(pros_xpath).getall()
            pros = ";".join(pros)
            review['TestPros'] = pros

            cons_xpath = '//dl[@class="List List--Definition is-con"]'\
                         '//dd//text()'
            cons = response.xpath(cons_xpath).getall()
            cons = ";".join(cons)
            review['TestCons'] = cons

            # 'source_internal_id'
            id = response.url.split('_')[-1]
            id = id.replace('.html', '')
            review['source_internal_id'] = id

            # PRODUCT --------------------------------------------------------
            product = ProductItem()
            product['source_internal_id'] = review['source_internal_id']
            product['OriginalCategoryName'] = response.meta.get('category')
            product['ProductName'] = review['ProductName']

            img_xpath = '//meta[@property="og:image"]/@content'
            img = response.xpath(img_xpath).get()
            product['PicURL'] = img

            product['TestUrl'] = response.url

            yield product
            yield review
