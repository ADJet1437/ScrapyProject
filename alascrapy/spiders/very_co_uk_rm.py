# -*- coding: utf8 -*-

import re

from alascrapy.spiders.base_spiders.rm_spider import RMSpider
from alascrapy.lib.generic import date_format
from alascrapy.lib.selenium_browser import SeleniumBrowser, uses_selenium
from alascrapy.items import ReviewItem, ProductIdItem


class NextDomesticAppliancesRMSpider(RMSpider):
    name = 'very_co_uk_rm'
    allowed_domains = ['very.co.uk']

    source_internal_id_re = re.compile("/(\d+)\.prd")

    @uses_selenium
    def parse(self, response):
        #Must use only product_page
        category_xpaths = { "category_leaf": "//*[@id='moreFrom-catLink']/a/text()",
                            "category_path": "//*[@id='moreFrom-catLink']/a/text()"
                          }


        product_xpaths = { "PicURL": "(//li[@class='productImageItem'])[1]//img/@src",
                           "ProductName": "//h1[@class='productHeading']//text()",
                           "ProductManufacturer": "//h1[@class='productHeading']/text()"
                         }

        category = self.init_item_by_xpaths(response, "category",
                                           category_xpaths)
        product = self.init_item_by_xpaths(response, "product", product_xpaths)

        match = re.search(self.source_internal_id_re, response.url)
        if match:
            product['source_internal_id'] = match.group(1)
        product["OriginalCategoryName"] = category["category_path"]
        yield category
        yield product
        yield self.get_rm_kidval(product, response)

        mpn_value = self.extract(response.xpath("//span[@id='productMPN']/text()"))
        if mpn_value:
            mpn = ProductIdItem()
            mpn['source_internal_id'] = product["source_internal_id"]
            mpn['ProductName'] = product["ProductName"]
            mpn['ID_kind'] = "MPN"
            mpn['ID_value'] = mpn_value
            yield mpn

        ean_value = self.extract(response.xpath("//span[@id='productEAN']/text()"))
        if ean_value:
            ean = ProductIdItem()
            ean['source_internal_id'] = product["source_internal_id"]
            ean['ProductName'] = product["ProductName"]
            ean['ID_kind'] = "EAN"
            ean['ID_value'] = ean_value
            yield ean

        with SeleniumBrowser(self, response) as browser:
            selector = browser.get(response.url)
            for review in self._parse_reviews(selector, browser, product):
                yield review

    def _parse_reviews(self, selector, browser, product):
        review_container_xpath = "//div[@itemprop='review']"

        author_xpath = ".//meta[@itemprop='name']/@content"
        title_xpath = ".//p[@itemprop='name']/text()"
        summary_xpath = ".//*[@itemprop='reviewBody']/text()"
        rating_xpath = ".//*[@itemprop='ratingValue']/text()"
        pros_xpath = ".//p[@class='pluck-review-full-review-pro']/text()"
        cons_xpath = ".//p[@class='pluck-review-full-review-con']/text()"
        test_date_xpath = ".//time[@itemprop='datePublished']/@datetime"
        next_page_xpath = "//a[@title='Next']"
        review_containers = selector.xpath(review_container_xpath)

        for review_container in review_containers:
            review = ReviewItem()
            review['DBaseCategoryName'] = "USER"
            review['ProductName'] = product['ProductName']
            review['source_internal_id'] = product['source_internal_id']
            review['TestUrl'] = product['TestUrl']
            review['Author'] = self.extract(review_container.xpath(author_xpath))
            review["TestTitle"] = self.extract(review_container.xpath(title_xpath))
            review["TestSummary"] = self.extract(review_container.xpath(summary_xpath))
            review["SourceTestRating"] = self.extract(review_container.xpath(rating_xpath))

            date_text = self.extract(review_container.xpath(test_date_xpath))
            review["TestDateText"] = date_format(date_text[0:-6], "%Y-%m-%dT%H:%M:%S")

            review['TestPros'] = self.extract(review_container.xpath(pros_xpath))
            review['TestCons'] = self.extract(review_container.xpath(cons_xpath))

            yield review

        next_page = selector.xpath(next_page_xpath)
        if next_page:
            next_page_selector = browser.click(next_page_xpath)
            for review in self._parse_reviews(next_page_selector, browser, product):
                yield review
