# -*- coding: utf8 -*-

import re

from alascrapy.spiders.base_spiders.rm_spider import RMSpider
from alascrapy.lib.generic import get_full_url
from alascrapy.lib.selenium_browser import SeleniumBrowser, uses_selenium
from alascrapy.items import ReviewItem


class NextDomesticAppliancesRMSpider(RMSpider):
    name = 'nextdomesticappliances_co_uk_rm'
    allowed_domains = ['nextdomesticappliances.co.uk']

    rating_re = re.compile("(\d) out of \d")

    @uses_selenium
    def parse(self, response):
        #Must use only product_page
        category_xpaths = { "category_leaf": "(//ul[@id='breadcrumb']/li/a)[last()]/text()"
                          }
        category_path_xpath = "//ul[@id='breadcrumb']/li/a/text()"


        product_xpaths = { "PicURL": "//div[@id='productImage']/img/@src",
                           "ProductName": "//div[@typeof='v:Product']/h1/text()",
                           "ProductManufacturer": "//div[@typeof='v:Product']/h1/span[@property='v:brand']/text()"
                         }

        category = self.init_item_by_xpaths(response, "category", category_xpaths)
        category["category_path"] = self.extract_all(response.xpath(category_path_xpath),
                                                     separator=" | ")

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product["PicURL"] = get_full_url(response, product["PicURL"])
        product["OriginalCategoryName"] = category["category_path"]
        product["ProductName"] = "%s %s" % (product['ProductManufacturer'], product["ProductName"])
        yield category
        yield product
        yield self.get_rm_kidval(product, response)

        with SeleniumBrowser(self, response) as browser:
            browser.get(response.url)
            selector = browser.click("//a[@class='reviewLinks']")

            for review in self._parse_reviews(selector, browser, product):
                yield review

    def _parse_reviews(self, selector, browser, product):
        review_container_xpath = "//div[@class='reviewContainer']"

        author_xpath = ".//div[@class='nicknameContainer']/span[1]/text()"
        title_xpath = ".//div[@class='titleContainer']/span/text()"
        summary_xpath = ".//div[@class='reviewTextContainer']/span/text()"
        rating_xpath = ".//div[@class='ratingImageContainer']/img/@title"
        pros_xpath = ".//span[@class='prosConsTitle' and contains(text(), 'Pros')]/following-sibling::span/text()"
        cons_xpath = ".//span[@class='prosConsTitle' and contains(text(), 'Cons')]/following-sibling::span/text()"
        next_page_xpath = "//div[@id='paginationContainer']/a[contains(text(), 'next')]"
        review_containers = selector.xpath(review_container_xpath)

        for review_container in review_containers:
            review = ReviewItem()
            review['DBaseCategoryName'] = "USER"
            review['ProductName'] = product['ProductName']
            review['TestUrl'] = product['TestUrl']
            review['Author'] = self.extract(review_container.xpath(author_xpath))
            review["TestTitle"] = self.extract(review_container.xpath(title_xpath))
            review["TestSummary"] = self.extract(review_container.xpath(summary_xpath))

            rating_text = self.extract(review_container.xpath(rating_xpath))
            match = re.match(self.rating_re, rating_text)
            if match:
                review['SourceTestRating'] = match.group(1)

            pros_text = self.extract(review_container.xpath(pros_xpath))
            if pros_text != 'none':
                review['TestPros'] =  pros_text
            cons_text = self.extract(review_container.xpath(cons_xpath))
            if cons_text != 'none':
                review['TestCons'] = cons_text
            yield review

        next_page = selector.xpath(next_page_xpath)
        if next_page:
            next_page_selector = browser.click(next_page_xpath)
            for review in self._parse_reviews(next_page_selector, browser, product):
                yield review
