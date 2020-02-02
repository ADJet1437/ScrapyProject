# -*- coding: utf8 -*-

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from datetime import datetime
from scrapy.http import Request
from alascrapy.items import ProductItem, ReviewItem


class RecombuSpider(AlaSpider):
    name = 'recombu'
    allowed_domains = ['recombu.com']
    start_urls = ['https://recombu.com/category/reviews']

    def __init__(self, *args, **kwargs):
        super(RecombuSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

        # In order to test another stored_last_date
        # self.stored_last_date = datetime(2000, 2, 8)

    def parse(self, response):
        # print "     ...PARSE: " + response.url

        post_urls_xpath = '//div[@class="content left"]//ul[contains(@class, '\
                          '"articles")]//li/article/a/@href'
        post_urls = response.xpath(post_urls_xpath).getall()

        # Send all posts for scraping, excepting the last one
        for url in post_urls[:-1]:
            yield Request(url=url,
                          callback=self.parse_product_review,
                          meta={'try_next_page': False})

        # This is the last post. We are both sending it for scraping
        # and also sending the URL of the next posts' list page
        # in case the date of the post is earlier than the
        # self.stored_last_date.
        next_page_url_xpath = '//a[@class="next page-numbers"]/@href'
        next_page_url = None
        try:
            next_page_url = response.xpath(next_page_url_xpath).get()
        except:
            pass

        yield Request(url=post_urls[-1],
                      callback=self.parse_product_review,
                      meta={'try_next_page': True,
                            'next_page_url': next_page_url})
        # ----------------------------------------------------------

    def parse_product_review(self, response):
        # print "     ...PARSE_PRODUCT_REVIEW: " + response.url

        category_xpath = '//li[@class="section"]/a//text()'
        category = response.xpath(category_xpath).get()

        # This website has a difficult categorization of their reviews.
        # For example. 'Broadband & TV' includes laptops, speakers, pendrivers,
        # and so on...
        categories_to_scrape = ['Mobile Phones', 'Broadband & TV', ]

        if category in categories_to_scrape:
            # Check the date
            date_xpath = '//time[@class="updated entry-time"]/@datetime'
            date = response.xpath(date_xpath).get()
            date = datetime.strptime(date, '%Y-%m-%d')

            if date > self.stored_last_date:
                # If the post doesn't have a review Rate, it means it's not a
                # review of one product.
                rating_scale_xpath = '//meta[@itemprop="bestRating"]/@content'
                if response.xpath(rating_scale_xpath).get():

                    # REVIEW ITEM ---------------------------------------------
                    review_xpaths = {
                        'TestTitle': '//div[@class="title"]/h1//text()',
                        'Author': '//a[@rel="author"]//text()',
                        'TestSummary': '//meta[@property="og:description"]'
                                       '/@content',
                        'SourceTestScale': '//meta[@itemprop="bestRating"]/'
                                           '@content',
                        'SourceTestRating': '//span[@itemprop="ratingValue"]//'
                                            'text()'
                    }

                    # Create the review
                    review = self.init_item_by_xpaths(response, "review",
                                                      review_xpaths)

                    # 'ProductName'
                    product_name_xpath = '//div[@class="title"]/h1//text()'
                    product_name = response.xpath(product_name_xpath).get()
                    words_to_split = ['Review:',
                                      'review: Hands-on',
                                      'review:']

                    for w in words_to_split:
                        if w in product_name:
                            product_name = product_name.split(w)[0]

                    words_to_remove = ['Review', 'review']
                    for word in words_to_remove:
                        product_name = product_name.replace(word, '')
                    product_name = product_name.strip()
                    review['ProductName'] = product_name

                    # 'TestDateText'
                    date = date.strftime("%Y-%m-%d")
                    review['TestDateText'] = date

                    # 'DBaseCategoryName'
                    review['DBaseCategoryName'] = 'PRO'

                    # 'TestPros' and 'TestCons'
                    pros_xpath = '//div[@class="the-good"]//ul/li//text()'
                    pros = response.xpath(pros_xpath).getall()
                    pros = ";".join(pros)

                    cons_xpath = '//div[@class="the-bad"]//ul/li//text()'
                    cons = response.xpath(cons_xpath).getall()
                    cons = ";".join(cons)

                    review['TestPros'] = pros
                    review['TestCons'] = cons

                    # 'source_internal_id'
                    id_xpath = '//link[@rel="shortlink"]/@href'
                    sid = response.xpath(id_xpath).get()
                    sid = sid.split('?p=')[-1]
                    review['source_internal_id'] = sid
                    # ---------------------------------------------------------

                    # PRODUCT ITEM --------------------------------------------
                    product = ProductItem()
                    product['source_internal_id'] = review['source_'
                                                           'internal_id']
                    product['OriginalCategoryName'] = category
                    product['ProductName'] = review['ProductName']
                    pic_url_xpath = '//meta[@property="og:image"]/@content'
                    pic_url = response.xpath(pic_url_xpath).get()
                    product['PicURL'] = pic_url
                    product['TestUrl'] = response.url
                    # ---------------------------------------------------------

                    yield review
                    yield product

        '''# Another option to identify the product category is through the
        meta article tag. Still has some flaws on that logic.

        possible_categories_xp = '//meta[@property="article:tag"]/@content'
        possible_categories = response.xpath(possible_categories_xp).getall()

        for c in possible_categories:
            print c
        '''

        # Call parse again for the "next button"s URL in case the
        # last review ( response.meta.get('try_next_page') is True in
        # case this is the last review of the page) is earlier
        # than self.stored_last_date
        date_xpath = '//time[@class="updated entry-time"]/@datetime'
        date = response.xpath(date_xpath).get()
        date = datetime.strptime(date, '%Y-%m-%d')

        if response.meta.get('try_next_page'):
            if date > self.stored_last_date:
                url = response.meta.get('next_page_url')
                yield Request(url=url,
                              callback=self.parse)
