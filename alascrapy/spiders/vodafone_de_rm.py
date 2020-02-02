# -*- coding: utf8 -*-
__author__ = 'leonardo'

from alascrapy.spiders.base_spiders.rm_spider import RMSpider
from alascrapy.lib.generic import date_format, get_full_url
from alascrapy.lib.selenium_browser import SeleniumBrowser, uses_selenium
from alascrapy.items import ReviewItem

class VodafoneDERMSpider(RMSpider):
    name = 'vodafone_de_rm'
    allowed_domains = ['vodafone.de']

    @uses_selenium
    def parse(self, response):
        category_xpaths = { "category_leaf": "(//ul[@class='ulNavigationBreadcrumb']/li/a)[last()]/text()",
                            "category_path": "(//ul[@class='ulNavigationBreadcrumb']/li/a)[last()]/text()"
                          }

        product_xpaths = { "PicURL": "(//ul[@class='thumbsBox']/li/a)[1]/@href",
                           "ProductName": "//h1[@itemprop='name']/text()"
                         }

        category = self.init_item_by_xpaths(response, "category", category_xpaths)
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product["OriginalCategoryName"] = category["category_path"]
        product["PicURL"] = get_full_url(response.url, product["PicURL"])
        yield category
        yield product
        yield self.get_rm_kidval(product, response)

        reviews_xpath = "//a[@id='tabRating']"

        with SeleniumBrowser(self, response) as browser:
            browser.get(response.url)
            browser.scroll(200) # click auto scroll does not work for some
            selector = browser.click(reviews_xpath)

            for review in self._parse_reviews(selector, browser, product):
                yield review

    def _parse_reviews(self, selector, browser, product):
        review_container_xpath = "//div[@data-review-id]"

        author_xpath = ".//p[@class='pr-review-author-name']/span/text()"
        rating_xpath = ".//span[contains(@class, 'pr-rating')]/text()"
        title_xpath = ".//p[@class='pr-review-rating-headline']"
        test_date_xpath = ".//div[contains(@class, 'pr-review-author-date')]/text()"
        summary_xpath = ".//p[@class='pr-comments']/text()"
        next_page_xpath = "//a[@class='next_page']"
        review_containers = selector.xpath(review_container_xpath)

        for review_container in review_containers:
            review = ReviewItem()
            review['DBaseCategoryName'] = "USER"
            review['ProductName'] = product['ProductName']
            review['TestUrl'] = product['TestUrl']
            review['Author'] = self.extract(review_container.xpath(author_xpath))
            review['SourceTestRating'] = self.extract(review_container.xpath(
                rating_xpath))

            review['TestTitle'] = self.extract(review_container.xpath(title_xpath))
            review['TestSummary'] = self.extract(review_container.xpath(summary_xpath))

            review['TestDateText'] = self.extract(review_container.xpath(test_date_xpath))
            review['TestDateText'] = date_format(review['TestDateText'],
                                                 '%d.%m.%Y')
            yield review

        #next_page = selector.xpath(next_page_xpath) No next page logic yet
        # as there are no products with a second page
        #if next_page:
        #    next_page_selector = browser.click(next_page_xpath)
        #    for review in self._parse_reviews(next_page_selector, browser,
        # product):
        #        yield review
