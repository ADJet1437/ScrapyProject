# -*- coding: utf8 -*-

from datetime import datetime
import re
from scrapy.http import Request
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem


class TechspectiveSpider(AlaSpider):
    name = 'techspective'
    allowed_domains = ['techspective.net']

    start_urls = ['https://techspective.net/category/reviews']

    def __init__(self, *args, **kwargs):
        super(TechspectiveSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

        # In order to test another stored_last_date
        # self.stored_last_date = datetime(2000, 2, 8)

    def parse(self, response):
        # print "     ...PARSE: " + response.url
        # print " -- self.stored_last_date: " + str(self.stored_last_date)

        cat_dict = {'Tablet': 'category-tablets-mobile-2',
                    'Laptop': 'category-laptops',
                    'Smartphone': 'category-smartphones',
                    'Smartwatch': 'category-smartwatches',
                    'Monitor': 'category-monitors',
                    'Headphone': 'category-headphones'}

        review_divs_xpath = '//div[@class="column half b-col"]'
        review_divs = response.xpath(review_divs_xpath)

        date = None
        for r_div in review_divs:
            categories_xpath = ".//article/@class"
            categories = r_div.xpath(categories_xpath).get()
            categories = categories.split(' ')

            product_category = None
            for cat in cat_dict:
                if cat_dict[cat] in categories:
                    product_category = cat

            if product_category:
                date_xpath = './/time/@datetime'
                date = r_div.xpath(date_xpath).get()
                date = date.split('T')[0]
                date = datetime.strptime(date, "%Y-%m-%d")

                if date > self.stored_last_date:
                    r_url_xpath = './/article/a/@href'
                    r_url = r_div.xpath(r_url_xpath).get()

                    yield Request(url=r_url,
                                  callback=self.parse_product_review,
                                  meta={'date': date.strftime("%Y-%m-%d"),
                                        'cat': product_category})

        # Checking whether we should scrape the next page
        next_page_url_xpath = '//a[@class="next page-numbers"]/@href'
        next_page_url = response.xpath(next_page_url_xpath).get()

        if next_page_url:
            # 'date' contains the date of the last review in the page
            if date and (date > self.stored_last_date):
                yield Request(url=next_page_url,
                              callback=self.parse)

    def get_product_name_based_on_title(self, title):
        ''' This function will 'clean' the title of the review
            in order to get the product name '''
        p_name = title

        # Title begins with unnecessary sentence
        discart_beggings = ['Review: ']

        for s in discart_beggings:
            if p_name.startswith(s):
                p_name = p_name.replace(s, '')

        # Spliting title
        get_first_piece = [u':', u' – ']
        get_last_piece = []

        for g_f in get_first_piece:
            if g_f in p_name:
                p_name = p_name.split(g_f)[0]

        for g_l in get_last_piece:
            if g_l in p_name:
                p_name = p_name.split(g_l)[-1]

        # Removing certain words
        words_to_remove = ['review', 'hands-on', 'Gaming Laptop']
        for w in words_to_remove:
            if w in title:
                p_name = p_name.replace(w, '')

        # Removing unnecessary spaces:
        p_name = p_name.replace('  ', ' ')
        p_name = p_name.strip()

        return p_name

    def parse_product_review(self, response):
        # print "     ...PARSE_PRODUCT_REVIEW: " + response.url

        # Check whether this is a proper review:
        title = title = response.xpath('//meta[@property="og:title"]'
                                       '/@content').get()

        if '30 Days series' in title:
            return
        else:
            expressions_to_exclude = [r', Day [0-9]:', r', Day [0-9]:']
            for exp in expressions_to_exclude:
                if re.search(exp, title):
                    print "EXCLUDING! " + title
                    return

        # REVIEW ITEM ---------------------------------------------------------
        # Check whether the title starts with: 'The Best...' if so, exclude it.
        review_xpaths = {
            'TestTitle': '//meta[@property="og:title"]/@content',
            'Author': '//span[@class="reviewer"]/a[@rel="author"]//text()',
            'TestSummary': '//meta[@property="og:description"]/@content',
        }

        # Create the review
        review = self.init_item_by_xpaths(response, "review",
                                          review_xpaths)

        # 'ProductName'
        title = review['TestTitle']
        review['ProductName'] = self.get_product_name_based_on_title(title)

        # 'TestDateText'
        review['TestDateText'] = response.meta.get('date')

        # 'SourceTestScale' 'SourceTestRating'
        rating_xpath = '//span[@class="number rating"]//span[@class="value"]'\
                       '/text()'
        rating = response.xpath(rating_xpath).get()
        if rating:
            review['SourceTestRating'] = rating
            review['SourceTestScale'] = 100

        # 'DBaseCategoryName'
        review['DBaseCategoryName'] = 'PRO'

        # 'source_internal_id'
        sid = response.xpath('//link[@rel="shortlink"]/@href').get()
        sid = sid.split('p=')[-1]
        review['source_internal_id'] = sid
        # ---------------------------------------------------------------------

        # PRODUCT ITEM --------------------------------------------------------
        product = ProductItem()
        product['source_internal_id'] = review['source_internal_id']
        product['OriginalCategoryName'] = response.meta.get('cat')
        product['ProductName'] = review['ProductName']

        pic_url_xpath = '//meta[@property="og:image"]/@content'
        pic_url = response.xpath(pic_url_xpath).get()
        product['PicURL'] = pic_url

        product['TestUrl'] = response.url
        # ---------------------------------------------------------------------

        yield review
        yield product
