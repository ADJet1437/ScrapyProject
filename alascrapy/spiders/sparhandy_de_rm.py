# -*- coding: utf8 -*-
__author__ = 'leonardo'

import re

from alascrapy.spiders.base_spiders.rm_spider import RMSpider
from alascrapy.lib.selenium_browser import SeleniumBrowser, uses_selenium
from alascrapy.items import ReviewItem

class SparhandyDERMSpider(RMSpider):
    name = 'sparhandy_de_rm'
    allowed_domains = ['sparhandy.de']

    rating_dict = {'einsnull': 1,
                   'zweinull': 2,
                   'dreinull': 3,
                   'viernull': 4,
                   'funfnull': 5}

    rating_re = re.compile("bewertung (.+)")
    date_re = re.compile("Kundenmeinung von (.+)")

    @uses_selenium
    def parse(self, response):
        category_xpaths = { "category_leaf": "(//a[@class='klickpfad'])[last()]//text()"
                          }

        category_path_xpath = "//a[@class='klickpfad']/text()"
        product_xpaths = { "PicURL": "//div[@id='big_handy_img']/img/@src",
                           "ProductName": "//h1/span[@itemprop='name']/text()",
                           "ProductManufacturer": "//h1/span[@itemprop='brand']//text()"
                         }

        category = self.init_item_by_xpaths(response, "category", category_xpaths)
        category["category_path"] = self.extract_all(
            response.xpath(category_path_xpath), separator=' | '
        )

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product["OriginalCategoryName"] = category["category_path"]
        product["ProductName"] = "%s %s" % (product["ProductManufacturer"],
                                            product["ProductName"])

        yield category
        yield product
        yield self.get_rm_kidval(product, response)

        reviews_xpath = "//a[@id='ekomi_button']"
        all_reviews_button = "//span[@id='lade_bewertungen']"

        with SeleniumBrowser(self, response) as browser:
            browser.get(response.url)
            browser.click(reviews_xpath)
            selector = browser.click(all_reviews_button)

            for review in self._parse_reviews(selector, browser, product):
                yield review

    def _parse_reviews(self, selector, browser, product):
        ratings_xpath = "//div[@id='bewertungen']/div[contains(@class, 'bewertung')]/@class"
        dates_xpath = "//div[@id='bewertungen']/i/text()"
        summaries_xpath = "//div[@id='bewertungen']/text()"

        ratings = self.extract_list(selector.xpath(ratings_xpath))
        dates = self.extract_list(selector.xpath(dates_xpath))
        summaries =  self.extract_list(selector.xpath(summaries_xpath))
        summaries_index = 0
        for index, rating in enumerate(ratings):
            review = ReviewItem()
            review['DBaseCategoryName'] = "USER"
            review['ProductName'] = product['ProductName']
            review['TestUrl'] = product['TestUrl']

            rating_match = re.match(self.rating_re, rating)
            if rating_match:
                rating_key = rating_match.group(1)
                review['SourceTestRating'] = self.rating_dict[rating_key]


            date = dates[index]
            date_match = re.match(self.date_re, date)
            if date_match:
                review['TestDateText'] = date_match.group(1)

            while True:
                summary = summaries[summaries_index]\
                    .replace(u'\xa0',' ')\
                    .strip(" \t\n\r")
                summaries_index = summaries_index + 1
                if summary:
                    review['TestSummary'] = summary
                    break

            print review
            yield review