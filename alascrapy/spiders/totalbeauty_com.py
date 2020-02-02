__author__ = 'frank'

from scrapy.http import Request

from alascrapy.items import CategoryItem
from alascrapy.lib.generic import get_full_url, date_format
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider

import alascrapy.lib.dao.incremental_scraping as incremental_utils
import dateparser
import re


class TotalBeautySpider(AlaSpider):
    name = 'totalbeauty_com'
    locale = 'en'

    start_urls = ['http://www.totalbeauty.com/reviews']
    category_url_suffix = '?bt=0&st=0%7cm&kw=&ir='

    def parse(self, response):
        category_xpath = "//ul[@class='column']/li[position() > 1]/a/@href"

        category_urls = self.extract_list(response.xpath(category_xpath))
        for url in category_urls:
            url = get_full_url(response, url)
            url = url + self.category_url_suffix
            request = Request(url=url, callback=self.parse_category)
            yield request

    def parse_category(self, response):
        products_xpath = "//ul[@class='prodList']/li[ div[contains(@class, 'prodName')] ]"
        product_url_xpath = "(.//a[1])/@href"
        has_review_xpath = ".//*[@class='ratingStarSmall']"
        next_page_xpath = "//li[@id='pagNext']/a/@href"

        categories_xpath = "//meta[@name='sales-reviews-cats']/@content"
        category = response.meta.get('category', '')
        if not category:
            # the category we get here is actually parent category
            category = CategoryItem()
            category['category_url'] = response.url
            categories_text = self.extract(response.xpath(categories_xpath))
            if not categories_text:
                categories_xpath = "//div[@id='breadcrumbTitle']//text()"
                categories_text = self.extract_all(response.xpath(categories_xpath))
                # first category is always 'Review',
                # so we get only the rest categories
                categories_text = '|'.join(categories_text.split('/')[1:])
            category['category_path'] = categories_text
            yield category
            if self.should_skip_category(category):
                return

        products = response.xpath(products_xpath)
        if not products:
            return

        for product in products:
            has_review = product.xpath(has_review_xpath)

            # rest of the products are also not reviewed
            if not has_review:
                return

            product_url = self.extract(product.xpath(product_url_xpath))
            product_url = get_full_url(response, product_url)
            request = Request(url=product_url, callback=self.parse_product)
            request.meta['category'] = category
            yield request

        next_page_url = self.extract_xpath(response, next_page_xpath)
        if next_page_url:
            next_page_url = get_full_url(response, next_page_url)
            next_page_request = Request(next_page_url, callback=self.parse_category)
            next_page_request.meta['category'] = category
            yield next_page_request

    def parse_product(self, response):
        product_xpaths = {"PicURL": "//meta[@property='og:image']/@content",
                          "ProductName": "//meta[@property='og:title']/@content",
                          "ProductManufacturer": "//meta[@name='reviews-brand']/@content"
                          }
        source_internal_id_re = r'product/([0-9]+)/'

        editor_review_xpath = "//div[@id='editorReview']"
        editor_review_content_xpaths = {"TestTitle": "//meta[@property='og:title']/@content",
                                        "TestSummary": ".//div[@class='reviewText']/text()",
                                        "Author": "(./div[@id='editorReviewer']//a)[1]/text()",
                                        "TestDateText": ".//*[@class='date']/text()",
                                        "SourceTestRating": ".//*[@class='ratingStarSmall']/text()"
                                        }

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        match = re.search(source_internal_id_re, response.url)
        if match:
            source_internal_id = match.group(1)
            product['source_internal_id'] = source_internal_id
            product_id = self.product_id(product, kind='totalbeauty_internal_id', value=source_internal_id)
            yield product_id

        product['OriginalCategoryName'] = response.meta['category']['category_path']
        yield product

        editor_reviews = response.xpath(editor_review_xpath)
        for editor_review in editor_reviews:
            yield self.parse_review(response, product, editor_review_content_xpaths, 'PRO', editor_review)

        user_review_url = response.url.rstrip('/') + '/reviews'
        request = Request(url=user_review_url, callback=self.parse_user_reviews)
        request.meta['product'] = product
        yield request

    def parse_user_reviews(self, response):
        # Featured reviews are always at the top. We cannot do incremental scraping before finishing
        # parsing all featured reviews, as there may be newer regular reviews following them.
        product = response.meta['product']
        reviews_xpath = "//ul[@class='userlist']/li[@id]"
        user_review_content_xpaths = {"TestTitle": ".//p[@class='reviewTitle']/text()",
                                      "Author": ".//*[@class='reviewedBy']/a/text()",
                                      "SourceTestRating": ".//*[@class='ratingStarSmall']/text()"
                                      }

        review_summary_xpath = ".//div[@class='reviewText']/span[@class='smallContent']/text()"
        review_summary_xpath_part2 = ".//div[@class='reviewText']//span[@class='moreReview']/text()"

        next_page_xpath = "//li[@id='pagNext']/a/@href"

        last_user_review = incremental_utils.get_latest_user_review_date_by_sii(
            self.mysql_manager, self.spider_conf['source_id'],
            product["source_internal_id"]
        )

        review_selectors = response.xpath(reviews_xpath)
        for review_selector in review_selectors:
            is_featured_review = 'featured' in self.extract(review_selector.xpath('./@class')).lower()
            review = self.parse_review(response, product, user_review_content_xpaths, 'USER', review_selector)

            # incremental scraping
            if review.get('TestDateText', '') and not is_featured_review:
                current_user_review = dateparser.parse(review['TestDateText'],
                                                       date_formats=['%Y-%m-%d'])
                if current_user_review < last_user_review:
                    return

            # If we fail to get summary, then an exception will be thrown
            review['TestSummary'] = review_selector.xpath(review_summary_xpath).extract_first()
            summary_part2 = review_selector.xpath(review_summary_xpath_part2).extract_first()
            if summary_part2:
                review['TestSummary'] += summary_part2
            review['TestSummary'] = review['TestSummary'].strip()

            yield review

        next_page_url = self.extract(response.xpath(next_page_xpath))
        if next_page_url:
            next_page_url = get_full_url(response, next_page_url)
            next_page_request = Request(next_page_url, callback=self.parse_user_reviews, meta=response.meta)
            yield next_page_request

    def parse_review(self, response, product, xpaths, review_type, selector=None):
        review = self.init_item_by_xpaths(response, "review", xpaths, selector=selector)
        review["DBaseCategoryName"] = review_type
        review['SourceTestScale'] = 10
        review["ProductName"] = product["ProductName"]
        review["source_internal_id"] = product.get('source_internal_id', None)
        if review.get('TestDateText', ''):
            if review_type == 'PRO':
                review['TestDateText'] = date_format(review['TestDateText'], "%Y-%m-%d")
            else:
                # The user review date is displayed as '(x years, )y months ago(, z weeks ago)' on the website
                datetime = dateparser.parse(review['TestDateText'])
                review['TestDateText'] = datetime.strftime('%Y-%m-01')
        return review
