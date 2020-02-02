__author__ = 'leo, frank'

from datetime import datetime
import json
import re
from scrapy.http import Request

from alascrapy.lib.generic import get_full_url, date_format
from alascrapy.items import CategoryItem, ReviewItem, ProductIdItem, ProductItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider

import alascrapy.lib.dao.incremental_scraping as incremental_utils

class KiesKeurigNlSpider(AlaSpider):
    name = 'kieskeurig_nl'
    allowed_domains = ['kieskeurig.nl']
    start_urls = ['https://www.kieskeurig.nl/']
    product_url_re = re.compile('/(\w+)/product/([\w-]+)')

    def parse(self, response):
        sub_category_urls = self.extract_list(response.xpath('//h3/a/@href'))
        for sub_category_url in sub_category_urls:
            sub_category_url = get_full_url(response, sub_category_url)
            yield Request(url=sub_category_url, callback=self.parse)

        if not sub_category_urls:
            category_urls = self.extract_list(response.xpath(
                    '//div[@class="cat-tile"]/a/@href'))
            for category_url in category_urls:
                category_url = get_full_url(response, category_url)
                yield Request(url=category_url, callback=self.parse_category)

    def parse_category(self, response):
        category = response.meta.get('category', None)

        if not category:
            category = CategoryItem()
            category["category_path"] = self.extract_all(response.xpath(
                    '//ul[contains(@class,"crumbpath")]//li//text()'), ' | ')
            category["category_leaf"] = self.extract(response.xpath(
                    '//ul[contains(@class,"crumbpath")]//li[last()]//text()'))
            category["category_url"] = response.url
            yield category

        if not self.should_skip_category(category):
            product_url_xpath = "//div[@id='products']//article[@data-pid and .//div[contains(@class, 'product-tile__rating')]/span[@class='label']]/a/@href"
            product_urls = self.extract_list_xpath(response, product_url_xpath)
            for product_url in product_urls:
                match = re.search(self.product_url_re, product_url)
                if match:
                    product_url = "/%s/product/" \
                                  "%s/specificaties" % (match.group(1),
                                                        match.group(2))
                    product_url = get_full_url(response, product_url)
                    request = Request(product_url, callback=self.parse_product)
                    request.meta['category'] = category
                    yield request

            next_page = self.extract(response.xpath('//link[@rel="next"]/@href'))
            if next_page:
                next_page = get_full_url(response, next_page)
                request = Request(next_page, callback=self.parse_category)
                request.meta['category'] = category
                yield request

    def parse_product(self, response):
        if 'kieskeurig.nl' not in response.url:
            return #offsite middleware is not filtering all requests

        review_url_xpath = "//a[contains(@class, 'rating') and ./span[@class='label']/text()]/@href"
        product = ProductItem()

        product['TestUrl'] = response.url
        product["OriginalCategoryName"] = response.meta['category']['category_path']
        product['ProductName'] = self.extract(response.xpath('//@data-compare-title'))
        product['PicURL'] = self.extract(response.xpath('//@data-compare-image'))
        product['source_internal_id'] = self.extract(response.xpath('//@data-compare-product-id'))

        if not product['ProductName']:
            raise Exception("Could not scrape product in %s" % response.url)

        yield product

        mpn = self.extract(response.xpath('//dt[contains(text(),"Partnumber")]/following-sibling::dd[1]/text()'))
        if mpn and mpn > '-':
            mpns = mpn.split(', ')
            for mpn in mpns:
                mpn_id = ProductIdItem()
                mpn_id['ProductName'] = product["ProductName"]
                mpn_id['source_internal_id'] = product['source_internal_id']
                mpn_id['ID_kind'] = "MPN"
                mpn_id['ID_value'] = mpn
                yield mpn_id

        ean = self.extract(response.xpath('//dt[contains(text(),"EAN")]/following-sibling::dd[1]/text()'))
        if ean:
            eans = ean.split(', ')
            for ean in eans:
                ean_id = ProductIdItem()
                ean_id['ProductName'] = product["ProductName"]
                ean_id['source_internal_id'] = product['source_internal_id']
                ean_id['ID_kind'] = "EAN"
                ean_id['ID_value'] = ean
                yield ean_id

        review_url = self.extract_xpath(response, review_url_xpath)
        if review_url:
            review_url = get_full_url(response, review_url)

            latest_review_date = incremental_utils.get_latest_user_review_date_by_sii(self.mysql_manager,
                                                                                      self.spider_conf['source_id'],
                                                                                      product['source_internal_id'])
            request = Request(review_url, callback=self.parse_reviews_prep)
            request.meta['product'] = product
            request.meta['review_url'] = review_url
            request.meta['latest_review_date'] = latest_review_date
            yield request

    # sort the reviews by date (newest first)
    def parse_reviews_prep(self, response):
        sort_by_date_xpath = "//a[@class='js-ga-tracking' and contains(text(), 'nieuwste eerst')]/@data-url"
        sort_by_date_url = self.extract(response.xpath(sort_by_date_xpath))
        if not sort_by_date_url:
            return

        sort_by_date_url = get_full_url(response, sort_by_date_url)
        request = Request(sort_by_date_url, callback=self.parse_reviews, meta=response.meta)
        yield request

    def parse_reviews(self, response):
        product = response.meta['product']
        review_url = response.meta['review_url']
        rating_xpath = ".//div[contains(@class, 'rating')]/span[@class='label']/text()"
        title_xpath = ".//div[@class='title']/h2/text()"
        summary_xpath = './/div[contains(@class,"reviews-single__text")]/text()'
        author_xpath = './/span[@class="author"]/text()'
        pros_xpath = ".//div[@class='pros']/ul/li/text()"
        cons_xpath = ".//div[@class='cons']/ul/li/text()"
        next_page_xpath = "//a[contains(@class, 'load-more-reviews')]/@data-load-more"
        reviews = response.xpath("//div[@class='reviews-single']")

        if not reviews:
            return

        for review in reviews:
            user_review = ReviewItem()
            user_review['DBaseCategoryName'] = "USER"
            user_review['ProductName'] = product['ProductName']
            user_review['source_internal_id'] = product['source_internal_id']
            user_review['TestUrl'] = review_url
            date = self.extract(review.xpath('.//span[@class="date"]/text()'))
            user_review['TestDateText'] = date_format(date, '%d-%m-%Y')

            user_review['SourceTestRating'] = self.extract_xpath(review, rating_xpath)
            if user_review['SourceTestRating']:
                user_review['SourceTestScale'] = 10
            user_review['Author'] = self.extract_xpath(review, author_xpath)
            user_review['TestTitle'] = self.extract_all_xpath(review,
                                                              title_xpath)
            user_review['TestSummary'] = self.extract_all_xpath(review,
                                                                summary_xpath)
            user_review['TestPros'] = self.extract_all_xpath(review,
                                                             pros_xpath,
                                                             separator=' ; ')
            user_review['TestCons'] = self.extract_all_xpath(review,
                                                             cons_xpath,
                                                             separator=' ; ')

            yield user_review

        # only check the last review of a page as we may miss a few reviews from time to time
        # due to the errors of 'load'
        latest_review_date = response.meta.get('latest_review_date')
        if latest_review_date and datetime.strptime(user_review['TestDateText'], '%Y-%m-%d') < latest_review_date:
            return

        next_page_json = self.extract_xpath(response, next_page_xpath)
        if next_page_json:
            next_page = json.loads(next_page_json)
            next_page_url = next_page['source']
            next_page_url = get_full_url(response, next_page_url)
            request = Request(next_page_url, callback=self.parse_reviews, meta=response.meta)
            yield request

