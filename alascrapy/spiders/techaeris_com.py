# -*- coding: utf8 -*-
import re

from datetime import datetime
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import CategoryItem


class Techaeris_comSpider(AlaSpider):
    name = 'techaeris_com'
    allowed_domains = ['techaeris.com']
    start_urls = ['https://techaeris.com/reviews']

    custom_settings = {
        'COOKIES_ENABLED': True,
    }

    def parse(self, response):
        review_url_xpath = "(//div[contains(@class,'home')]/a/@href) | (//ul[contains(@class,'archive-col-list left')]//a/@href)"
        next_page_xpath = "(//div[@class='pagination']//@href)[last()-1]"

        next_page = self.extract(response.xpath(next_page_xpath))
        if next_page:
            yield response.follow(url=next_page, callback=self.parse)

        # extract all review urls and send a request for each of them
        review_urls = self.extract_list(response.xpath(review_url_xpath))
        for review_url in review_urls:
            yield response.follow(url=review_url, callback=self.parse_product)

    def parse_product(self, response):
        category = self.get_category(response)
        if category:
            yield category
            if self.should_skip_category(category):
                return

        # initialize a product
        # (use regular expression to get source_internal_id)
        source_internal_id_re = r'p=([0-9]+)'
        source_internal_id_xpath = "//link[@rel='shortlink']/@href"
        product_xpaths = {
            "ProductName": "//*[@itemprop='itemReviewed']/meta[@itemprop='name']/@content",
            "PicURL": "(//meta[@property='og:image']/@content)[1]"
        }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['source_internal_id'] = response.xpath(source_internal_id_xpath).re_first(source_internal_id_re)

        # if ProductName is null take the title from another xpath
        if not product["ProductName"]:
            product["ProductName"] = self.extract(response.xpath("//title/text()"))

        # product's OriginalCategoryName should always
        # match category_path of the corresponding category item
        if category:
            product["OriginalCategoryName"] = category['category_path']
        else:
            category_alt_xpath = '//span[@class="post-list-cat"]/text()'
            category_alt = self.extract(response.xpath(category_alt_xpath))
            product["OriginalCategoryName"] = category_alt

        yield product

        # REVIEW
        review_xpaths = {
            "SourceTestRating": "//span[@itemprop='ratingValue']/text()",
            "TestDateText": "//meta[@property='article:published_time']/@content",
            "TestPros": "//div[@class='pros']/ul/li/text()",
            "TestCons": "//div[@class='cons']/ul/li/text()",
            "TestSummary": "//meta[@name='description']/@content",
            "TestVerdict": "//*[text()='Wrap Up']/following::p[1]/text()",
            "Author": "//span[contains(@class,'author-name')]//text()",
            "TestTitle": "//*[@property='og:title']/@content",
        }
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        # format the date
        if review["TestDateText"]:
            review["TestDateText"] = date_format(
                review["TestDateText"],
                "%Y-%m-%d"
            )

        if not review["TestPros"]:
            review["TestPros"] = self.extract(
                response.xpath("//div[@class='rwp-pros']/text()")
            )

        if not review["TestCons"]:
            review["TestCons"] = self.extract(
                response.xpath("//div[@class='rwp-cons']/text()")
            )

        review["DBaseCategoryName"] = "PRO"

        if not review["SourceTestRating"]:
            review["SourceTestRating"] = self.extract(
                response.xpath("//span[@property='ratingValue']/text()")
            )

        review["SourceTestScale"] = self.extract(
            response.xpath("//meta[@itemprop='bestRating']/@content")
        )
        if not review["SourceTestScale"]:
            review["SourceTestScale"] = self.extract(
                response.xpath("//meta[@property='bestRating']/@content")
            )

        review["ProductName"] = product["ProductName"]
        review["source_internal_id"] = product['source_internal_id']
        yield review

    def get_category(self, response):
        """ assign a category name (from the list) to category['category_path'].
        It also initializes category
        """
        category_tags = ('cell phone', 'smartphone', 'speaker', 'speakers',
                         'wireless speaker', 'bluetooth speaker', 'bluetoothspeaker',
                         'bookshelf speakers', 'headphones', 'headset', 'earphones',
                         'earbuds', 'wireless earbuds', 'bluetooth earbuds', 'laptop',
                         'laptops', 'gaming laptop', 'e-reader', 'tablet', 'camera',
                         'tv', 'desktop', 'pc', 'computer', 'gaming pc', 'webcam',
                         'monitor', 'display', 'gaming monitor', 'mouse',
                         'gaming mouse', 'fitness tracker', 'watch', 'wearables',
                         'smart lamp', 'office chair', 'phone case', 'smartphone case',
                         '3d-printer', 'router',  'projector', 'ssd', 'fitnesstracker',
                         'smartwatch', 'fitness tracker', 'drone', 'toys', 'usb hub',
                         'grilling', 'ice maker', 'iring', 'wireless charging',
                         'laser measuring', 'wood cover', 'backpack', 'routers',
                         'mobile')

        tag_xpath = "//meta[@property='article:tag']/@content"
        page_tags = self.extract_list(response.xpath(tag_xpath))
        page_tags = [t.lower() for t in page_tags]

        category_name = ''
        for category_tag in category_tags:
            if category_tag.lower() in page_tags:
                category_name = category_tag
                break

        if category_name:
            category = CategoryItem()
            category['category_path'] = category_name
            return category
