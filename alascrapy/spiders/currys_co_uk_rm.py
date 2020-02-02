__author__ = 'leonardo'
import re

from alascrapy.spiders.base_spiders.rm_spider import RMSpider
from alascrapy.lib.selenium_browser import SeleniumBrowser, uses_selenium
from alascrapy.items import ReviewItem


class CurrysUKRMSpider(RMSpider):
    name = 'currys_co_uk_rm'
    allowed_domains = ['currys.co.uk']

    source_internal_id_re = re.compile("sku:(\d+)")

    @uses_selenium
    def parse(self, response):
        #Must use only product_page
        category_xpaths = { "category_leaf": "(//div[@class='breadcrumb']//a/span)[last()]//text()"
                          }
        category_path_xpath = "(//div[@class='breadcrumb']//a/span)//text()"
        product_xpaths = { "PicURL": "(//*[@property='og:image'])[1]/@content",
                           "ProductName": "//h1[contains(@class, 'page-title')]/span//text()",
                           "ProductManufacturer": "//h1[contains(@class,'page-title')]/span[@itemprop='brand']/text()"
                         }

        category = self.init_item_by_xpaths(response, "category", category_xpaths)
        category["category_path"] = self.extract_all(
            response.xpath(category_path_xpath), separator=' | '
        )

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product["OriginalCategoryName"] = category["category_path"]
        product["source_internal_id"] = None

        source_internal_id_xpath = "//meta[@itemprop='identifier']/@content"
        source_internal_id =  self.extract(response.xpath(source_internal_id_xpath))
        match = re.match(self.source_internal_id_re, source_internal_id)
        if match:
            product["source_internal_id"] = match.group(1)
        yield category
        yield product
        yield self.get_rm_kidval(product, response)

        reviews_xpath="//a[contains(text(),' customer reviews')]"

        with SeleniumBrowser(self, response) as browser:
            browser.get(response.url)
            selector = browser.click(reviews_xpath)

            for review in self._parse_reviews(selector, browser, product):
                yield review



    def _parse_reviews(self, selector, browser, product):
        review_container_xpath = "//article[contains(@id, 'review_')]"

        author_xpath = ".//h4[@class='attribution-name']/text()"
        rating_xpath = ".//div[@class='overall_score_stars']/@title"
        pros_xpath = ".//dd[@class='pros']/text()"
        cons_xpath = ".//dd[@class='cons']/text()"
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

            review['TestPros'] = self.extract_all(review_container.xpath(pros_xpath),
                                                  separator= ' ; ')

            review['TestCons'] = self.extract_all(review_container.xpath(cons_xpath),
                                                  separator= ' ; ')

            if review['TestPros'] and review['TestCons']:
                yield review

        next_page = selector.xpath(next_page_xpath)
        if next_page:
            next_page_selector = browser.click(next_page_xpath)
            for review in self._parse_reviews(next_page_selector, browser, product):
                yield review
