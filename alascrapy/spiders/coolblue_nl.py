__author__ = 'leo'
import json
import re
from scrapy.http import Request

from alascrapy.lib.generic import get_full_url, date_format, strip, dateparser
from alascrapy.items import CategoryItem, ReviewItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider

import alascrapy.lib.extruct_helper as extruct_helper
import alascrapy.lib.dao.incremental_scraping as incremental_utils


class CoolBlueNlSpider(AlaSpider):
    name = 'coolblue_nl'
    start_urls = ['https://www.coolblue.nl/ons-assortiment']
    product_url_re = re.compile('//[^/]+/product/(\d+)')
    locale = 'nl'

    # Disable canonical link check
    custom_settings = {'DOWNLOADER_MIDDLEWARES': {
                        'alascrapy.middleware.forbidden_requests_middleware.ForbiddenRequestsMiddleware': 80,
                        'alascrapy.middleware.proxy_middleware.ProxyMiddleware': 111,
                        'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 115,
                        'alascrapy.middleware.user_agent_middleware.RotateUserAgentMiddleware': 120,
                        'alascrapy.middleware.redirect_middleware.ConfigurableRedirectMiddleware': 130,
                        'alascrapy.middleware.offsite_middleware.OffsiteMiddleware': 135,
                        'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': None,
                        'alascrapy.middleware.amazon_auth_middleware.AmazonAuthMiddleware': 140}}

    def parse(self, response):
        root_category_xpath = "//div[@class='product-category-navigation--content']"
        root_category_name_xpath = ".//h2[contains(@class, 'product-category-navigation--group-title')]/text()"

        middle_cat_xpath = ".//li[contains(@class, 'product-category-navigation--item')]"
        middle_cat_name_xpath = ".//h3[@class='product-category-navigation--title']/text()"

        leaf_category_xpath = ".//li[@class='category-navigation--item']"
        leaf_name_xpath = "./a/text()"
        leaf_url_xpath = "./a/@href"

        root_categories = response.xpath(root_category_xpath)
        for root_category in root_categories:
            root_category_name = self.extract_xpath(root_category,
                                                    root_category_name_xpath)

            middle_cats = root_category.xpath(middle_cat_xpath)
            for middle_cat in middle_cats:
                middle_cat_name = self.extract_xpath(middle_cat,
                                                     middle_cat_name_xpath)

                leaf_categories = middle_cat.xpath(leaf_category_xpath)
                for leaf in leaf_categories:
                    leaf_name = self.extract_xpath(leaf, leaf_name_xpath)
                    leaf_url = self.extract_xpath(leaf, leaf_url_xpath)
                    leaf_url = get_full_url(response, leaf_url)

                    category_path = "%s | %s | %s" % (root_category_name,
                                                      middle_cat_name,
                                                      leaf_name)

                    category = CategoryItem()
                    category['category_path'] = category_path
                    category['category_url'] = leaf_url
                    yield category

                    if not self.should_skip_category(category):
                        request = Request(leaf_url, self.parse_category, dont_filter=True)
                        request.meta['category'] = category
                        yield request

    def parse_category(self, response):
        product_url_xpath = "//a[@class='product__title js-product-title']/@href"
        product_urls = self.extract_list_xpath(response, product_url_xpath)

        # There can be even lower levels if product urls are not found in category page
        if not product_urls:
            sub_category_xpath = "//div[@class='ec-visual-link']"
            sub_category_name_xpath = ".//div[@class='ec-visual-link__title']/text()"
            sub_category_url_xpath = "./a/@href"

            sub_categories = response.xpath(sub_category_xpath)
            for sub_cat in sub_categories:
                sub_category_name = self.extract_xpath(sub_cat, sub_category_name_xpath)
                sub_category_url = self.extract_xpath(sub_cat, sub_category_url_xpath)

                if not (sub_category_name and sub_category_url):
                    return

                sub_category_url = get_full_url(response, sub_category_url)
                category_path = "%s | %s" % (response.meta['category']['category_path'],
                                             sub_category_name)

                category = CategoryItem()
                category['category_path'] = category_path
                category['category_url'] = sub_category_url
                yield category

                if not self.should_skip_category(category):
                    request = Request(sub_category_url, self.parse_category)
                    request.meta['category'] = category
                    yield request

            return

        category = response.meta['category']

        for product_url in product_urls:
            product_url = get_full_url(response, product_url)
            request = Request(product_url, callback=self.parse_product)
            request.meta['category'] = category
            yield request

        next_page = self.extract(response.xpath('//a[contains(@class, "js-next")]/@href'))
        if next_page:
            next_page = get_full_url(response, next_page)
            request = Request(next_page, callback=self.parse_category)
            request.meta['category'] = category
            yield request

    def parse_product(self, response):
        category = response.meta['category']
        review_url_xpath = "//div[@class='product-page--title-links']//a[@class='review-rating--reviews-link']/@href"
        match = re.search(self.product_url_re, response.url)
        if match:
            source_internal_id = match.group(1)
        else:
            self.logger.error('Failed to get source internal id for product at: {}'.format(response.url))
            return

        json_ld = extruct_helper.extract_json_ld(response.text, 'Product')
        if not json_ld:
            request = self._retry(response.request)
            yield request
            return

        product = extruct_helper.product_item_from_product_json_ld(json_ld)
        product['TestUrl'] = response.url
        product['source_internal_id'] = source_internal_id
        product['OriginalCategoryName'] = category['category_path']
        yield product

        review_url = self.extract_xpath(response, review_url_xpath)
        if review_url:
            review_url = get_full_url(response, review_url) + '?sorteer=date%20desc'
            request = Request(review_url, callback=self.parse_reviews)
            request.meta['product'] = product
            yield request

    def parse_reviews(self, response):
        product = response.meta['product']
        rating_xpath = ".//*[@class='review--header-rating']/text()"
        title_xpath = ".//h3[contains(@class, 'review--header-title')]/text()"
        summary_xpath = ".//div[contains(@class, 'review--description')]//text()"
        header_xpath = ".//div[@class='review--header-review-info']//text()"
        date_xpath =  ".//div[@class='review--header-review-info']/time/@datetime"

        pros_xpath = ".//li[contains(@class, 'pros-and-cons-pro')]//*[@class!='is-visually-hidden']/text()"
        cons_xpath = ".//li[contains(@class, 'pros-and-cons-con')]//*[@class!='is-visually-hidden']/text()"

        next_page_xpath = "//a[@rel='next']/@href"
        reviews = response.xpath("//li[contains(@class, 'reviews__list-item')]")

        last_user_review = incremental_utils.get_latest_user_review_date_by_sii(
            self.mysql_manager, self.spider_conf['source_id'],
            product["source_internal_id"]
        )

        for review in reviews:
            date = self.extract_xpath(review, date_xpath)
            if date:
                date = date_format(date, '')
                current_user_review = dateparser.parse(date,
                                                       date_formats=['%Y-%m-%d'])
                if current_user_review < last_user_review:
                    return

            title = self.extract_xpath(review, title_xpath)
            rating = self.extract_xpath(review, rating_xpath)
            splitted = rating.split('/')
            if splitted:
                rating = splitted[0]

            summary = self.extract_all_xpath(review, summary_xpath)
            pros = self.extract_all_xpath(review, pros_xpath, separator=' ; ')
            cons = self.extract_all_xpath(review, cons_xpath, separator=' ; ')
            author = ''
            header = self.extract_all_xpath(review, header_xpath)
            if header:
                author = header.split('|')
                author = strip(author[0])

            user_review = ReviewItem.from_product(product=product, tp='USER', rating=rating,
                                                  title=title, date=date, summary=summary,
                                                  pros=pros, cons=cons, author=author, scale=10)
            yield user_review

        next_page_url = self.extract_xpath(response, next_page_xpath)
        if next_page_url:
            next_page_url = get_full_url(response, next_page_url)
            request = Request(next_page_url, callback=self.parse_reviews)
            request.meta['product'] = product
            yield request
