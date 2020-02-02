# -*- coding: utf8 -*-

from datetime import datetime

from scrapy.http import Request
import json
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.items import ProductItem, ReviewItem
import alascrapy.lib.dao.incremental_scraping as incremental_utils


class ProductReviewComAuSpider(AlaSpider):
    name = 'productreview_com_au'
    allowed_domains = ['productreview.com.au']
    start_urls = ['https://www.productreview.com.au/i/sitemap.html']

    def __init__(self, *args, **kwargs):
        super(ProductReviewComAuSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

        # Testing another date
        # self.stored_last_date = datetime(2019, 1, 1)

    def parse(self, response):
        # print "     ...PARSE: " + response.url

        categories_xpath = '//ul[@class="mb-4_1be columns-0 columns-sm-2_33O '\
                           'columns-md-3_3Ip columns-xl-4_2UD '\
                           'list-unstyled_3FI"]//li'

        categories = response.xpath(categories_xpath)

        for category in categories:
            category_name = category.xpath('.//text()').get()

            # Filter the categories here
            categories_to_scrape = ['4K Ultra HD TVs',
                                    'Action Cameras',
                                    'Digital Cameras',
                                    'Drones',
                                    'Full HD TVs',
                                    'Headphones',
                                    'Laptops',
                                    'Mirrorless Cameras',
                                    'Mobile Phones',
                                    'Monitors',
                                    'Printers',
                                    'TVs',
                                    'Tablets',
                                    'Top Loading Washing Machines',
                                    'Video Cameras',
                                    'Washing Machines',
                                    'Wired Headphones',
                                    'Wireless Headphones'
                                    ]

            if category_name in categories_to_scrape:
                # print " ---SCRAPE: " + category_name

                category_url_xpath = ".//a/@href"
                category_url = category.xpath(category_url_xpath).get()

                yield response.follow(url=category_url,
                                      callback=self.parse_category,
                                      meta={'category': category_name})

    def parse_category(self, response):
        # print "     ...PARSE_CATEGORY: " + response.url

        product_urls_xpath = '//div[@id="search-results"]'\
                             '//a[div][not(ancestor::li)]/@href'
        product_urls = response.xpath(product_urls_xpath).getall()

        category = response.meta.get('category')
        for p_url in product_urls:
            yield response.follow(url=p_url,
                                  callback=self.parse_product_reviews,
                                  meta={'category': category})

        # Check for next page button
        nxt_pg_button_xpath = '//li[@class="ml-1_W40 flex-grow-1_3A8"]'\
                              '[last()]/a/div[text()="Next ›"]'.decode('utf-8')

        next_page_button = response.xpath(nxt_pg_button_xpath)

        if next_page_button:
            next_page_url_xpath = '//li[@class="ml-1_W40 flex-grow-1_3A8"]'\
                                  '[last()]/a/@href'
            next_page_url = response.xpath(next_page_url_xpath).get()

            category = response.meta.get('category')
            yield response.follow(url=next_page_url,
                                  callback=self.parse_category,
                                  meta={'category': category})

    def parse_product_reviews(self, response):
        # print "     ...PARSE_PRODUCT_REVIEWS: " + response.url

        # We need to get the JSON which contains all info for the
        #  reviews
        html = response.body
        js_starts = 'window.__productreview_data='
        js_ends = ';</script>'
        js = html.split(js_starts)[1]
        js = js.split(js_ends)[0]

        js = json.loads(js)

        reviews = js["listing"]["reviews"]["collection"]
        product_name = js["listing"]["details"]["fullName"]

        # PRODUCT ITEM --------------------------------------------------------
        product = ProductItem()

        # sid = js["listing"]["details"]["id"]

        product['OriginalCategoryName'] = response.meta.get('category')
        product['ProductName'] = product_name

        pic_url_xpath = '//div[@class="p-1_2ec align-items-center_nNY '\
                        'flex-column_36B justify-content-center_1IB '\
                        'relative_2e- d-flex_b9D card-body_10p"]//img/@src'
        pic_url = response.xpath(pic_url_xpath).get()
        product['PicURL'] = pic_url

        product['TestUrl'] = response.url
        # ---------------------------------------------------------------------

        # REVIEW ITEM ---------------------------------------------------------
        for r in reviews:
            # Checking whether it's a new review
            date_str = r["author"]["registeredAt"].split("T")[0]
            date = datetime.strptime(date_str, '%Y-%m-%d')

            if date > self.stored_last_date:
                review = ReviewItem()

                review['Author'] = r["author"]["displayName"]
                review['TestSummary'] = r["body"]

                review['TestDateText'] = date_str

                rating = r["subject"]["entry"]['statistics']['rating']
                scale = 5
                if rating:
                    review['SourceTestRating'] = rating
                    review['SourceTestScale'] = scale

                review['DBaseCategoryName'] = 'USER'

                review['source_internal_id'] = r["id"]

                review['TestTitle'] = r["title"]
                review['ProductName'] = product_name
                review['TestUrl'] = response.url

                # As requested, the yield product is now inside the for loop,
                # so we are saving the same product several times (once for
                # each review).
                product['source_internal_id'] = review['source_internal_id']

                yield review
                yield product
        # ---------------------------------------------------------------------
