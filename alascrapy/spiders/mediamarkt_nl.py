"""mediamarkt_nl Spider: """

__author__ = 'leonardo'

import re

from scrapy.http import Request
from alascrapy.items import CategoryItem, ReviewItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import  get_full_url

import alascrapy.lib.extruct_helper as extruct_helper


class MediaMarktNlSpider(AlaSpider):
    name = 'mediamarkt_nl'
    allowed_domains = ['mediamarkt.nl']
    locale = 'nl'
    download_delay=1
    start_urls = ['http://www.mediamarkt.nl/?langId=-11']
    kind = 'mediamarkt_nl_id'
    rating_regex = re.compile('value-([1-5])')

    def parse(self, response):
        # Nav bar parsing for categories
        root_cat_xpath = '//ul[@role="menu"]/li/a/@href'
        category_url_list = self.extract_list_xpath(response, root_cat_xpath)
        for category_url in category_url_list:
            category_request = Request(url=category_url,
                                        callback=self.parse_category)
            yield category_request

    def parse_category(self, response):
        sub_categories_xpath = "//ul[@class='categories-flat-descendants']/li/ul/li/a/@href"
        sub_category_url_list = self.extract_list_xpath(response,
                                                        sub_categories_xpath)

        for sub_category_url in sub_category_url_list:
            sub_category_url = get_full_url(response.url, sub_category_url)
            sub_category_request = Request(url=sub_category_url, callback=self.parse_sub_category)
            yield sub_category_request

    def parse_sub_category(self, response):
        category = response.meta.get('category', None)

        products_html_xpath = '//*[@class="product-wrapper"]'
        product_url_xpath = './/h2/a/@href'
        no_reviews_xpath = "./following::footer[1]//a[contains(@class, 'first-review') and contains(@href, '#reviews')]"
        next_page_url_xpath = '//*[@class="pagination-next"]//@href'
        category_path_xpath = "//ul[@class='breadcrumbs']/li[not(" \
                              "@class='home')]//text()"

        if not category:
            category = CategoryItem()
            category['category_path'] = self.extract_all_xpath(response,
                                                        category_path_xpath,
                                                        separator="|")
            category['category_url'] = response.url
            yield category
        else:
            category = response.meta['category']

        if not self.should_skip_category(category):
            products_html = response.xpath(products_html_xpath)
            for product_html in products_html:
                no_reviews =  product_html.xpath(no_reviews_xpath)
                if no_reviews:
                    continue
                product_url = self.extract_xpath(product_html,
                                                 product_url_xpath)
                product_url = get_full_url(response.url, product_url)
                request = Request(product_url, callback=self.parse_product)
                request.meta['category'] = category
                yield request

            next_page_url = self.extract_xpath(response, next_page_url_xpath)
            if next_page_url:
                next_page_url = get_full_url(response.url, next_page_url)
                request = Request(next_page_url, callback=self.parse_sub_category)
                request.meta['category'] = category
                yield request

    def _parse_reviews(self, response, product=None):
        review_list_xpath = "//ul[contains(@class, 'reviews-content')]/li"
        rating_string_xpath = ".//div[@class='rating']/div/@class"
        author_xpath = ".//div[@class='rating']/following::strong[1]/text()"
        date_xpath = ".//div[@class='rating']/following::small[1]/text()"
        title_xpath = './/h3/text()'
        summary_xpath = './/article/p[not(@class)]/text()'
        pros_xpath = ".//div[contains(@class, 'review-features') and " \
                     "contains(@class, 'review-pros')]/text()"
        cons_xpath = ".//div[contains(@class, 'review-features') and " \
                     "contains(@class, 'review-cons')]/text()"

        review_list = response.xpath(review_list_xpath)

        if not product:
            product = response.meta['product']

        for review_selector in review_list:
            rating = ''
            rating_string = self.extract_xpath(review_selector,
                                               rating_string_xpath)
            rating_match = re.match(self.rating_regex, rating_string)
            if rating_match:
                rating = rating_match.group(1)
            title = self.extract_xpath(review_selector, title_xpath)
            date = self.extract_xpath(review_selector, date_xpath)
            if date:
                date = date
            author = self.extract_xpath(review_selector, author_xpath)
            summary = self.extract_all_xpath(review_selector, summary_xpath)
            pros = self.extract_all_xpath(review_selector, pros_xpath)
            cons = self.extract_all_xpath(review_selector, cons_xpath)

            review = ReviewItem.from_product(product=product, author=author, summary=summary,
                                             date=date, pros=pros, cons=cons, title=title,
                                             rating=rating, tp='USER', scale=5)
            yield review

    def parse_product(self, response):
        """
        Parse an individual product page with the aim of creating 1 ProductItem,
        2 ProductIdItems and multiple ReviewItems.
        :param response:
        :return:
        """
        category = response.meta['category']
        review_url_xpath = "//ul[contains(@class, 'reviews-content-remaining')]/@data-href"
        brand_xpath = "//meta[@property='product:brand']/@content"
        _product = extruct_helper.product_items_from_microdata(response, category)
        if not _product:
            request = self._retry(response.request)
            yield request
            return

        product = _product.get('product')
        if not product["ProductManufacturer"]:
            product["ProductManufacturer"] = self.extract_xpath(response,
                                                                brand_xpath)

        mediamarkt_id = self.product_id(product, kind=self.kind,
                                        value=product['source_internal_id'])

        product_ids = _product.get('product_ids', [])

        yield product
        yield mediamarkt_id
        for product_id in product_ids:
            yield product_id

        for review in self._parse_reviews(response, product):
            yield review

        review_url = self.extract_xpath(response, review_url_xpath)
        if review_url:
            review_url = get_full_url(response.url, review_url)
            request = Request(review_url, callback=self._parse_reviews)
            request.meta['product'] = product
            yield request