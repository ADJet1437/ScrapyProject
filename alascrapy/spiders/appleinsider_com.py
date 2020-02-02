# -*- coding: utf8 -*-

from datetime import datetime
from scrapy.http import Request
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem


class Appleinsider_comSpider(AlaSpider):
    name = 'appleinsider_com'
    allowed_domains = ['appleinsider.com']
    page_number = 1
    start_urls = ['https://appleinsider.com/reviews/']

    def __init__(self, *args, **kwargs):
        super(Appleinsider_comSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

        # In order to test another stored_last_date
        # self.stored_last_date = datetime(2018, 2, 8)

    def parse(self, response):
        # print " 	...PARSE: " + response.url
        # print " --self.stored_last_date: " + str(self.stored_last_date)

        review_divs_xpath = '//div[@class="post mr18"]'
        review_divs = response.xpath(review_divs_xpath)

        date = None
        for r_div in review_divs:
            date_xpath = './p[@class="sh-date-header small gray"]//text()'
            date = r_div.xpath(date_xpath).get()
            # date looks like: 05/20/2019, 02:54:PM
            date = date.split(',')[0]
            date = datetime.strptime(date, '%m/%d/%Y')
            if date > self.stored_last_date:
                rating_xpath = './/span[@class="rating-hl"]//img/@src'
                rating = r_div.xpath(rating_xpath).get()
                # rating looks like:
                #   src="https://photos5.appleinsider.com/v9/images/ratings_hl_50.png"
                rating = rating.split('_')[-1]
                rating = rating.split('.')[0]
                rating = float(rating)
                rating = rating/10

                sid_xpath = './/img/@src'
                sid = r_div.xpath(sid_xpath).get()
                # sid looks like:
                #   "https://photos5.appleinsider.com/apps/ipad/images/articles/47439.jpg"
                sid = sid.split('/')[-1]
                sid = sid.split('.')[0]

                review_url_xpath = './h1/a/@href'
                review_url = r_div.xpath(review_url_xpath).get()
                review_url = "https:" + review_url

                yield Request(url=review_url,
                              callback=self.parse_product_review,
                              meta={'date': date.strftime("%Y-%m-%d"),
                                    'rating': rating,
                                    'sid': sid})

        # Checking whether we should scrape the next page
        if date and date > self.stored_last_date:
            next_page_url_xpath = '//a[text()="Next Page"]/@href'
            next_page_url = r_div.xpath(next_page_url_xpath).get()
            if next_page_url:
                self.page_number += 1
                next_page_url = "https://appleinsider.com/reviews"\
                                "/imp%20tracking/page/{}"\
                                .format(self.page_number)

                yield Request(url=next_page_url,
                              callback=self.parse)

    def get_product_name_based_on_title(self, title):
        ''' This function will 'clean' the title of the review
            in order to get the product name '''
        p_name = title

        # Spliting title
        get_first_piece = [u' -- ']

        for g_f in get_first_piece:
            if g_f in p_name:
                p_name = p_name.split(g_f)[0]

        # Removing certain words
        words_to_remove = ['Review:', 'review:']
        for w in words_to_remove:
            if w in title:
                p_name = p_name.replace(w, '')

        # Removing unnecessary spaces:
        p_name = p_name.replace('  ', ' ')
        p_name = p_name.strip()

        return p_name

    def parse_product_review(self, response):
        # print "     ...PARSE_PRODUCT_REVIEW: " + response.url

        # REVIEW ITEM ------------------------------------------------------
        review_xpaths = {
            'TestTitle': '//meta[@property="og:title"]/@content',
            'Author': '//p[@class="gray small byline"]/a//text()',
            'TestSummary': '//meta[@name="description"]/@content',
        }

        # Create the review
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        # 'ProductName'
        title = review['TestTitle']
        review['ProductName'] = self.get_product_name_based_on_title(title)

        # 'TestDateText'
        review['TestDateText'] = response.meta.get('date')

        # 'SourceTestScale' and 'SourceTestRating'
        rating = response.meta.get("rating")
        if rating:
            review['SourceTestScale'] = 5
            review['SourceTestRating'] = rating

        # 'DBaseCategoryName'
        review['DBaseCategoryName'] = 'PRO'

        # 'source_internal_id'
        review['source_internal_id'] = response.meta.get('sid')
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
