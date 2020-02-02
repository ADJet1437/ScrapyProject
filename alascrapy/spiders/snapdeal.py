"""office_depot Spider: """
from datetime import datetime

from scrapy.spiders import Rule
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_crawl import AlaCrawlSpider
from alascrapy.lib.selenium_browser import SeleniumBrowser
from alascrapy.items import ProductItem, CategoryItem, ReviewItem

__author__ = 'leonardo'

class SnapdealSpider(AlaCrawlSpider):
    name = 'snapdeal'
    download_delay = 2
    start_urls = ['http://www.snapdeal.com/page/sitemap']


    def __init__(self, *a, **kw):
        AlaCrawlSpider.__init__(self, *a, **kw)
        self.browser = SeleniumBrowser(self)

    def process_category_link(value):
        return value+"?sort=plrty&"

    rules = [ Rule(LxmlLinkExtractor(
                unique=True,
                allow=['/products/mobiles-mobile-phones'],
                #,
                #       '/products/mobiles-tablets',
                #       '/products/cameras-digital-cameras',
                #       '/products/cameras-digital-slrs'
                restrict_xpaths=['//*[@class="ht180"]//li//*'],
                process_value=process_category_link
              ), callback="parse_category")
            ]

    def parse_category(self, response):
        category_path_xpath='//*[@class="containerBreadcrumb"]//span/text()'
        category_leaf_xpath='//*[@class="active-bread"]/text()'

        clickable_element = '//*[contains(@class,"list-view-lang")]'
        loading_icon_xpath='//*[@id="ajax-loader-icon" and @class="mar_20per_left"]'

        product_list_xpath = '//*[@id="prodDetails"]/@href'

        category_xpath = self.extract_all(response, category_path_xpath,'|')

        if category_xpath not in self.skip_categories:
            category = CategoryItem()
            category["category_path"]=category_xpath
            category["category_leaf"]=self.extract(response, category_leaf_xpath)
            category["category_url"]=response.url
            yield category

            wait_for = EC.element_to_be_clickable((By.XPATH,clickable_element))
            selector = self.browser.get(response, wait_for)

            wait_for = EC.invisibility_of_element_located((By.XPATH,loading_icon_xpath))
            selector = self.browser.scroll_until_the_end(2000, wait_for)

            products = selector.xpath(product_list_xpath)

            for product in products:
                product_url = product.extract()
                request = Request(product_url, callback=self.parse_product)
                request.meta['category'] = category
                yield request


    def parse_product(self, response):
        category = response.meta['category']
        product_name_xpath='//*[@class="productTitle"]//*[@itemprop="name"]/text()'
        brand_xpath = '//*[@itemprop="brand"]//*[@itemprop="name"]/text()'
        pic_url_xpath = '//*[@class="mainImageSlider"]//*[@itemprop="image"]/@src'
        source_internal_id_xpath='//*[@id="pppid"]/text()'

        product = ProductItem()
        product["source_internal_id"] = self.extract(response.xpath(source_internal_id_xpath))
        product["ProductName"] = self.extract(response.xpath(product_name_xpath))
        product["OriginalCategoryName"] = category['category_path']
        product["PicURL"] = self.extract(response.xpath(pic_url_xpath))
        product["ProductManufacturer"] = self.extract(response.xpath(brand_xpath))
        product["TestUrl"] = response.url

        for review in self.parse_reviews(response, product):
            yield review

        yield product


    def parse_reviews(self, response, product):
        reviews_xpath = '//*[@class="pr-review-wrap"]'
        next_page_xpath = '//*[@class="pr-pagination-top"]//*[@class="pr-page-next"]/a'
        review_elements = response.xpath(reviews_xpath)

        for review_element in review_elements:
            yield self.parse_review(review_element, product)

        next_page = self.extract(response.xpath(next_page_xpath))
        if next_page:
            ec_condition = EC.element_to_be_clickable((By.XPATH, next_page_xpath))
            self.browser.get(response, ec_condition)

            ec_condition = EC.presence_of_all_elements_located((By.XPATH, '//*[@class="pr-contents-wrapper"]'))
            selector = self.browser.click(next_page_xpath, ec_condition)
            for review in self.parse_reviews(selector, product):
                yield review

    def parse_review(self, response, product):
        author_xpath = './/*[@class="prReviewAuthorProfileLnk"]/span/text()'
        rating_xpath = './/*[@class="pr-rating pr-rounded"]/text()'
        title_xpath = './/*[@class="pr-review-rating-headline"]/text()'
        verdict_xpath = './/*[@class="pr-review-bottom-line-wrapper"]/text()'
        date_xpath = './/*[contains(@class,"pr-review-author-date")]/text()'
        summary_xpath = './/*[@class="pr-comments"]'

        review = ReviewItem()
        review["source_internal_id"] = product["source_internal_id"]
        review["ProductName"] = product["ProductName"]
        review["SourceTestRating"] = self.extract(response.xpath(rating_xpath))
        extracted_date = self.extract(response.xpath(date_xpath))
        review["TestDateText"] = datetime.strptime(extracted_date, "%d/%m/%Y").strftime('%Y-%m-%d')
        review["TestSummary"] = self.extract(response.xpath(summary_xpath))
        review["TestVerdict"] =  self.extract(response.xpath(verdict_xpath))
        review["Author"] = self.extract(response.xpath(author_xpath))
        review["DBaseCategoryName"] = "USER"
        review["TestTitle"] = self.extract(response.xpath(title_xpath))
        review["TestUrl"] = product["TestUrl"]
        return review


