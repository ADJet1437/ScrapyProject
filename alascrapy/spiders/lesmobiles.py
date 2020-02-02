# -*- coding: utf8 -*-

from datetime import datetime
from scrapy.http import Request
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem, ProductIdItem
import dateparser


class LesmobilesSpider(AlaSpider):
    name = 'lesmobiles'
    allowed_domains = ['lesmobiles.com']
    page_number = 1
    base_url = 'https://www.lesmobiles.com/tests/telephones-mobiles.html?p={}'
    start_urls = [base_url.format(page_number)]

    def __init__(self, *args, **kwargs):
        super(LesmobilesSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

        # In order to test another stored_last_date
        self.stored_last_date = datetime(2017, 2, 8)

    def parse(self, response):
        # print " 	...PARSE: " + response.url
        # print " --self.stored_last_date: " + str(self.stored_last_date)

        review_articles_xpath = '//article[@class="clearfix"]'
        review_articles = response.xpath(review_articles_xpath)

        date = None
        for r_art in review_articles:
            date_xpath = './/time//text()'
            date = r_art.xpath(date_xpath).get()
            # date looks like: '19 décembre 2018 - 09h00'
            date = date.split('-')[0]
            date = date.strip()
            date = dateparser.parse(date, date_formats=['%d %B %Y'])

            if date > self.stored_last_date:
                review_url_xpath = './a/@href'
                review_url = r_art.xpath(review_url_xpath).get()

                yield response.follow(url=review_url,
                                      callback=self.parse_product_review,
                                      meta={'date': date.strftime("%Y-%m-%d")})

        # Checking whether we should scrape the next page
        if date and date > self.stored_last_date:
            self.page_number += 1
            yield Request(url=self.base_url.format(self.page_number),
                          callback=self.parse)

    def get_product_name_based_on_title(self, title):
        ''' This function will 'clean' the title of the review
            in order to get the product name '''
        p_name = title

        # Spliting title
        get_first_piece = [u':']

        for g_f in get_first_piece:
            if g_f in p_name:
                p_name = p_name.split(g_f)[0]

        # Removing certain words
        words_to_remove = ['Test du', u'Test de l’', u"Test de l'", 'Test de',
                           'Prise en main du']
        for w in words_to_remove:
            if w in title:
                p_name = p_name.replace(w, '')

        # Removing unnecessary spaces:
        p_name = p_name.replace('  ', ' ')
        p_name = p_name.strip()

        return p_name

    def parse_product_review(self, response):
        # print "     ...PARSE_PRODUCT_REVIEW: " + response.url

        # REVIEW ITEM -----------------------------------------------------
        review_xpaths = {
            'TestTitle': '//meta[@property="og:title"]/@content',
            'TestSummary': '//meta[@property="og:description"]/@content',
        }

        # Create the review
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        # 'ProductName'
        title = review['TestTitle']
        review['ProductName'] = self.get_product_name_based_on_title(title)

        # 'Author'
        author_xpath = '//p[@itemprop="author"]//text()'
        author = response.xpath(author_xpath).get()
        # author looks like: Par Samir Azzemou
        if 'Par' in author:
            author = author.replace('Par', '')
            author = author.strip()
        review['Author'] = author

        # 'TestDateText'
        review['TestDateText'] = response.meta.get('date')

        # 'SourceTestScale' and 'SourceTestRating'
        rating_xpath = '//span[@itemprop="ratingValue"]//text()'
        rating = response.xpath(rating_xpath).get()
        scale_xpath = '//span[@itemprop="bestRating"]//text()'
        scale = response.xpath(scale_xpath).get()
        if rating and scale:
            review['SourceTestRating'] = rating
            review['SourceTestScale'] = scale

        # 'DBaseCategoryName'
        review['DBaseCategoryName'] = 'PRO'

        # 'source_internal_id'
        sid = response.url
        # sid looks like: https://www.lesmobiles.com/test/apple-iphone-xs-64go
        sid = sid.split('/')[-1]
        review['source_internal_id'] = sid
        # -----------------------------------------------------------------

        # PRODUCT ITEM ----------------------------------------------------
        product = ProductItem()
        product['source_internal_id'] = review['source_internal_id']
        product['OriginalCategoryName'] = 'Smartphone'
        product['ProductName'] = review['ProductName']

        pic_url_xpath = '//meta[@property="og:image"]/@content'
        pic_url = response.xpath(pic_url_xpath).get()
        product['PicURL'] = pic_url

        product['TestUrl'] = response.url
        # -----------------------------------------------------------------

        # PRICE ITEM ------------------------------------------------------
        price_xpath = '//p[@class="price"]//text()'
        price = response.xpath(price_xpath).get()
        if price:
                price = price.strip()
                yield ProductIdItem.from_product(product,
                                                 kind='price',
                                                 value=price
                                                 )
        # -----------------------------------------------------------------

        yield review
        yield product
