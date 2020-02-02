"""mediamarkt_nl Spider: """
__author__ = 'leonardo'

import dateparser
import re
from scrapy.http import Request
from alascrapy.items import CategoryItem, ReviewItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, set_query_parameter, get_text_from_selector
from alascrapy.lib.dao.incremental_scraping import get_latest_user_review_date_by_sii

import alascrapy.lib.extruct_helper as extruct_helper


class MediaMarktDESpider(AlaSpider):
    name = 'mediamarkt_de'
    allowed_domains = ['mediamarkt.de']
    start_urls = ['http://www.mediamarkt.de']
    locale = 'de'

    def parse(self, response):
        category_xpath = "//ul[contains (@class, 'navigation')]/li/a[contains(@href,'category')]/@href"

        category_urls = self.extract_list_xpath(response, category_xpath)
        for category_url in category_urls:
            category_url = get_full_url(response, category_url)
            request = Request(category_url, callback=self.parse_sub_category)
            yield request

    def parse_sub_category(self, response):
        lvl1_sub_cat_url_xpath = "//fieldset//ul[" \
                           "@class='categories-flat-descendants']/li/a/@href"
        lvl2_sub_cat_url_xpath = "//fieldset[@class='active']//ul/li[" \
                                  "@class='active']/ul/li/a/@href"

        sub_categories_urls = self.extract_list_xpath(response,
                                                      lvl1_sub_cat_url_xpath)

        if not sub_categories_urls:
            sub_categories_urls = self.extract_list_xpath(response,
                                                          lvl2_sub_cat_url_xpath)

        if sub_categories_urls:
            for category_url in sub_categories_urls:
                category_url = get_full_url(response, category_url)
                request = Request(category_url, callback=self.parse_sub_category)
                yield request
        else:
            for item in self.parse_category(response):
                yield item

    def parse_category(self, response):
        category_path_xpath = "//ul[@class='breadcrumbs']/li[not(@class='home')]//text()"
        category_leaf_xpath = "//ul[@class='breadcrumbs']/li[not(@class='home')]/text()"
        product_url_xpath = "//div[contains(@class, 'product-wrapper')]//h2/a/@href"
        next_page_xpath = "//ul[@class='pagination']/li[@class='pagination-next']/a/@href"

        category = response.meta.get('category', None)
        if not category:
            category_path = self.extract_all_xpath(response, category_path_xpath,
                                                   separator='/')
            category_leaf = self.extract_all_xpath(response, category_leaf_xpath)

            category = CategoryItem()
            category['category_path'] = category_path
            category['category_leaf'] = category_leaf
            category['category_url'] = response.url
            yield category

        if self.should_skip_category(category):
            return

        product_urls = self.extract_list_xpath(response, product_url_xpath)
        for product_url in product_urls:
            product_url = get_full_url(response, product_url)
            request = Request(product_url, callback=self.parse_product)
            request.meta['category'] = category
            yield request

        next_page_url = self.extract_xpath(response, next_page_xpath)
        if next_page_url:
            next_page_url = get_full_url(response, next_page_url)
            request = Request(next_page_url, callback=self.parse_category)
            request.meta['category'] = category
            yield request

    def parse_product(self, response):
        category = response.meta['category']
        items = extruct_helper.get_microdata_extruct_items(response.body_as_unicode())
        ean_xpath = '//a[@data-ean]/@data-ean'
        brand_alt_xpath = "//meta[@property='product:brand']/@content"
        product = list(extruct_helper.get_products_microdata_extruct(items, response, category))
        if len(product) != 1:
            request = self._retry(response.request)
            yield request
            return

        product_dict = product[0]
        product = product_dict['product']

        if not product['ProductManufacturer']:
            product['ProductManufacturer'] = self.extract_xpath(response,
                                                                brand_alt_xpath)

        yield product
        for product_id in product_dict['product_ids']:
            yield product_id

        ean_value = int(self.extract_xpath(response, ean_xpath))
        if ean_value:
            ean = self.product_id(product, kind='EAN', value=ean_value)
            yield ean

        first_page_review_xpath = "//ul[contains(@class, 'js-product-reviews-first')]/@data-href"
        next_page_review_xpath = "//ul[contains(@class, 'js-product-reviews-remaining')]/@data-href"
        reviews_per_page_xpath = "//ul[contains(@class, 'js-product-reviews-remaining')]/@data-paged-per-page"
        total_reviews_xpath = "//ul[contains(@class, 'js-product-reviews-remaining')]/@data-paged-all"
        initial_index_xpath  = "//ul[contains(@class, 'js-product-reviews-remaining')]/@data-paged-current-index"
        paging_parameter_xpath  = "//ul[contains(@class, 'js-product-reviews-remaining')]/@data-paged-url-param"

        first_page_review_url = self.extract_xpath(response,
                                                   first_page_review_xpath)
        if first_page_review_url:
            first_page_review_url = get_full_url(response, first_page_review_url)
            first_page_review_url = set_query_parameter(first_page_review_url,
                                                        'sorting', 'LATEST')

            next_page_review_url = self.extract_xpath(response,
                                                      next_page_review_xpath)

            paging_meta = {}
            if next_page_review_url:
                last_review_db = get_latest_user_review_date_by_sii(
                    self.mysql_manager, self.spider_conf['source_id'],
                    product['source_internal_id'])
                next_page_review_url = get_full_url(response, next_page_review_url)
                next_page_review_url = set_query_parameter(next_page_review_url,
                                                            'sorting', 'LATEST')

                reviews_per_page = self.extract_xpath(response, reviews_per_page_xpath)
                total_reviews= self.extract_xpath(response, total_reviews_xpath)
                current_index = self.extract_xpath(response, initial_index_xpath)
                paging_parameter = self.extract_xpath(response, paging_parameter_xpath)
                paging_meta = { 'next_page_review_url': next_page_review_url,
                                'reviews_per_page': int(reviews_per_page),
                                'total_reviews': int(total_reviews),
                                'current_index': int(current_index),
                                'paging_parameter': paging_parameter,
                                'last_review_db': last_review_db
                              }

            meta = {'product': product}
            headers = {'Referer': response.url,
                       'X-Requested-With': 'XMLHttpRequest'}
            meta.update(paging_meta)

            request = Request(first_page_review_url, meta=meta, headers=headers,
                              callback=self.parse_reviews)
            yield request

    def parse_reviews(self, response):
        product = response.meta['product']

        summary_xpath = ".//article/text()"
        rating_xpath = ".//meta[@itemprop='rating']/@content"
        title_xpath = ".//meta[@itemprop='summary']/@content"
        date_xpath = ".//meta[@itemprop='dtreviewed']/@content"
        author_xpath = ".//meta[@itemprop='reviewer']/@content"
        pros_xpath = ".//div[contains(@class, 'review-features') and " \
                     "contains(@class, 'review-pros')]/text()"
        cons_xpath = ".//div[contains(@class, 'review-features') and " \
                     "contains(@class, 'review-cons')]/text()"

        review_selectors = response.xpath('//li')
        for review_selector in review_selectors:
            rating = self.extract_xpath(review_selector, rating_xpath)
            title = self.extract_xpath(review_selector, title_xpath)
            date = self.extract_xpath(review_selector, date_xpath)
            author = self.extract_xpath(review_selector, author_xpath)
            summary = self.extract_all_xpath(review_selector, summary_xpath)
            pros = self.extract_all_xpath(review_selector, pros_xpath)
            cons = self.extract_all_xpath(review_selector, cons_xpath)

            pros = re.sub("[\s]+",' ', pros)
            cons = re.sub("[\s]+",' ', cons)

            review = ReviewItem.from_product(product=product, title=title, rating=rating,
                                             tp='USER', scale=5, date=date, summary=summary,
                                             pros=pros, cons=cons, author=author)
            yield review

        last_date_in_page = dateparser.parse(date, ["%Y-%m-%d"])
        next_page_url = response.meta.get('next_page_review_url', None)
        if next_page_url:
            paging_parameter = response.meta['paging_parameter']
            current_index = response.meta['current_index']
            reviews_per_page = response.meta['reviews_per_page']
            total_reviews = response.meta['total_reviews']
            last_review_db = response.meta['last_review_db']

            if current_index >= total_reviews: #We reached the end
                return

            if last_review_db > last_date_in_page: #reached the end of new data
                return

            next_page_url = set_query_parameter(next_page_url,
                                                paging_parameter, current_index)

            headers = {'Referer': response.request.headers['Referer'],
                       'X-Requested-With': response.request.headers['X-Requested-With']}

            meta = { 'next_page_review_url': next_page_url,
                     'reviews_per_page': reviews_per_page,
                     'total_reviews': total_reviews,
                     'current_index': current_index + reviews_per_page,
                     'paging_parameter': paging_parameter,
                     'last_review_db': last_review_db,
                     'product': product
                   }

            request = Request(next_page_url, meta=meta,
                              headers=headers, callback=self.parse_reviews)
            yield request
