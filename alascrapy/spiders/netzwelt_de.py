# -*- coding: utf8 -*-
from datetime import datetime
import dateparser
import alascrapy.lib.extruct_helper as extruct_helper

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import CategoryItem


class Netzwelt_deSpider(AlaSpider):
    name = 'netzwelt_de'
    allowed_domains = ['netzwelt.de']
    start_urls = ['https://www.netzwelt.de/testberichte/index.html']

    def __init__(self, *args, **kwargs):
        super(Netzwelt_deSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):
        category_xpath = "//ul/li/a[contains(@title,'Testberichte')]/@href"
        category_urls = self.extract_list(response.xpath(category_xpath))
        for category_url in category_urls:
            category_url = get_full_url(response, category_url)
            yield response.follow(url=category_url,
                                  callback=self.parse_category)

    def parse_category(self, response):
        product_xpath = "//div[@data-product-id and " \
                        "not(.//span/text()='Upcoming')]//a/@href"
        product_urls = self.extract_list(response.xpath(product_xpath))
        for product_url in product_urls:
            yield response.follow(url=product_url, callback=self.parse_review)

    def parse_review(self, response):
        date_xpath = "//meta[@name='date']/@content"
        date_text = self.extract(response.xpath(date_xpath))
        date = (dateparser.parse(date_text)).date()
        if date and date < self.stored_last_date.date():
            return

        product_xpaths = {
            "source_internal_id": "//script/@data-post-id"
        }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)

        # Category
        category_path_xpath = "(//ul[contains(@itemtype, 'BreadcrumbList')]" \
                              "//*[@itemprop='name'])" \
                              "[position()<last()]/text()"
        category = CategoryItem()
        category['category_path'] = self.extract(response.xpath(category_path_xpath))
        # product's OriginalCategoryName should always
        # match category_path of the corresponding category item
        product['OriginalCategoryName'] = category['category_path']

        yield category

        # get review microdata
        microdata_items = extruct_helper.\
            get_microdata_extruct_items(response.text)
        review_microdata_item = None
        for item in microdata_items:
            if item['type'] == "https://schema.org/Product":
                review_microdata_item = item.get('properties', {}).get('review')
                break

        # extract review information from review microdata
        if review_microdata_item:
            review = extruct_helper.review_microdata_extruct(
                review_microdata_item, product, 'PRO')
            review['ProductName'] = \
                review_microdata_item.get('properties', {})\
                .get('itemReviewed')
        else:
            return

        if not review.get('ProductName'):
            product_name_xpath = "//title/text()"
            product_name = self.extract(response.xpath(product_name_xpath))
            product_name = product_name.replace(' - NETZWELT', '')
            review['ProductName'] = product_name

        # Assign the product name to product item
        product['ProductName'] = review.get('ProductName')

        yield product

        review['TestPros'] = self.extract_all(response.xpath(
            "//div[contains(@class,'fazit')]//li[contains(@class,'pro')]/text()"), '; ')
        review['TestCons'] = self.extract_all(response.xpath(
            "//div[contains(@class,'fazit')]//li[contains(@class,'con')]/text()"), '; ')

        yield review
