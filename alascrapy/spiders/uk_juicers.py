# -*- coding: utf8 -*-

import re

from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import date_format, dateparser
from alascrapy.items import CategoryItem, ReviewItem
from alascrapy.lib.generic import get_full_url

import alascrapy.lib.extruct_helper as extruct_helper
import alascrapy.lib.dao.incremental_scraping as incremental_utils


class UkJuicersSpider(AlaSpider):
    name = 'uk_juicers'
    locale = 'en_GB'
    start_urls = ['http://www.ukjuicers.com/juicers',
                  'http://www.ukjuicers.com/blenders',
                  'http://www.ukjuicers.com/dehydrators',
                  'http://www.ukjuicers.com/healthy-kitchen/spiralizers',
                  'http://www.ukjuicers.com/healthy-kitchen/food-processors'
                  ]

    def parse(self, response):
        category_name_xpath = '(//h1[1])/text()'
        products_xpath = "//ul[@class='products']/li"
        next_page_xpath = "(//*[@rel='next'])[1]/@href"
        product_url_xpath = "./a/@href"
        has_review_xpath = ".//ul[contains(@title, 'Average Rating')]"

        category = response.meta.get('category', '')
        if not category:
            category = CategoryItem()
            category['category_url'] = response.url
            category['category_leaf'] = self.extract(response.xpath(category_name_xpath))
            category['category_path'] = category['category_leaf']
            yield category

        products = response.xpath(products_xpath)
        for product in products:
            has_reviews = self.extract(product.xpath(has_review_xpath))

            if has_reviews:
                product_url = self.extract(product.xpath(product_url_xpath))
                product_url = get_full_url(response, product_url)
                request = Request(product_url, callback=self.parse_product)
                request.meta['category'] = category
                yield request

        next_page_url = self.extract(response.xpath(next_page_xpath))
        if next_page_url:
            next_page_url = get_full_url(response, next_page_url)
            request = Request(next_page_url, callback=self.parse)
            request.meta['category'] = category
            yield request

    def parse_product(self, response):
        review_url_xpath = "//div[@class='reviews']/p[@class='links ftr']/a/@href"

        _product = extruct_helper.product_items_from_microdata(response, response.meta['category'])
        if not _product:
            request = self._retry(response.request)
            yield request
            return

        product = _product.get('product')
        yield product

        product_ids = _product.get('product_ids')
        for product_id in product_ids:
            yield product_id

        review_url = self.extract(response.xpath(review_url_xpath))
        if review_url:
            review_url = get_full_url(response, review_url)
            last_user_review = incremental_utils.get_latest_user_review_date_by_sii(
                self.mysql_manager, self.spider_conf['source_id'],
                product["source_internal_id"]
            )

            request = Request(url=review_url, callback=self.parse_review)
            request.meta['product'] = product
            request.meta['last_user_review'] = last_user_review
            yield request

    def parse_review(self, response):
        review_xpath = "//ul[@class='comments']/li"
        title_xpath = "./p[@class='hdr']/text()"
        summary_xpath = "./p[@class='msg']/text()"
        rating_xpath = "./ul[contains(@class, 'rating')]/@title"
        date_and_author_xpath = "./p[@class='auth']/text()"
        next_page_xpath = "//div[@class='pg']/a[@class='n']/@href"

        product = response.meta['product']
        last_user_review = response.meta['last_user_review']

        for review in response.xpath(review_xpath):
            date_and_author = self.extract_xpath(review, date_and_author_xpath)
            if date_and_author.startswith('Reviewed'):
                date_and_author = date_and_author[len('Reviewed'):]
            date_and_author = date_and_author.split(',')[0]
            splitted = date_and_author.split('by')
            date = splitted[0].strip()
            if len(splitted) > 1:
                author = splitted[1].strip()

            if date:
                date = date_format(date, '')
                current_user_review = dateparser.parse(date,
                                                       date_formats=['%Y-%m-%d'])
                if current_user_review < last_user_review:
                    return

            title = self.extract_xpath(review, title_xpath)
            rating = self.extract_xpath(review, rating_xpath)
            splitted = rating.split(' out')
            if splitted:
                rating = splitted[0]

            summary = self.extract_all_xpath(review, summary_xpath)

            user_review = ReviewItem.from_product(product=product, tp='USER', rating=rating,
                                                  title=title, date=date, summary=summary,
                                                  author=author, scale=5)
            yield user_review

        next_page_url = self.extract(response.xpath(next_page_xpath))
        if next_page_url:
            next_page_request = Request(url=get_full_url(response, next_page_url),
                                        callback=self.parse_review, meta=response.meta)
            yield next_page_request
