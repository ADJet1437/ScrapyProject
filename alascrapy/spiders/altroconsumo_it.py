# -*- coding: utf8 -*-
from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url
from alascrapy.items import CategoryItem, ProductItem, ReviewItem
from alascrapy.lib.selenium_browser import SeleniumBrowser, uses_selenium


class AltroConsumoSpider(AlaSpider):
    name = 'altroconsumo_it'
    allowed_domains = ['altroconsumo.it']
    start_urls = ['http://www.altroconsumo.it/nt/test/elenco']

    user = "info@alatest.com"
    password = "alascore1234"

    def login_selenium(self, browser):
        browser.get("https://login.altroconsumo.it/", timeout=10)
        browser.write_in_field("//input[@id='Identification']", self.user)
        browser.write_in_field("//input[@id='Password']", self.password)
        browser.click("//input[@id='LoginButton']")

    def parse(self, response):
        next_page_xpath = "//div[@class='pager'][last()]//span[contains(text(),'Avanti')]/parent::a/@href"
        category_url_xpath = "//div[@class='contentWrapper']//a"

        categories = response.xpath(category_url_xpath)
        for category_sel in categories:
            category_name = self.extract(category_sel.xpath("./text()"))
            category_url = self.extract(category_sel.xpath("./@href"))
            category_url = get_full_url(response, category_url)

            category = CategoryItem()
            category['category_leaf'] = category_name
            category['category_path'] = category_name
            category['category_url'] =  category_url
            yield category

            if not self.should_skip_category(category):
                request = self.selenium_request(category_url, callback=self.parse_category)
                request.meta['category'] = category
                yield request

        next_page_url = response.xpath(next_page_xpath)
        if next_page_url:
            next_page_url = get_full_url(response, next_page_url)
            request = Request(next_page_url, callback=self.parse)
            yield request

    @uses_selenium
    def parse_category(self, response):
        all_products_xpath = "//a[@data-selector='INTRO_Link']/@href"
        all_products_url = self.extract(response.xpath(all_products_xpath))
        all_products_url = get_full_url(response.url, all_products_url)

        if all_products_url:
            request = self.selenium_request(all_products_url, callback=self.parse_category)
            request.meta['category'] = response.meta["category"]
            yield request
            return

        with SeleniumBrowser(self, response,
                             no_css=False, no_images=False) as browser:
            self.login_selenium(browser)
            products_div_xpath = "//section[contains(@class,'js-listing--desktop')]"
            #products_div = response.xpath(products_div_xpath)
            #if products_div:
            for item in self.parse_product_list_div(response, browser):
                yield item


    def parse_product_list_div(self, response, browser):
        products_xpath = "//article[@data-selector='LIST_Item']"
        next_page_url_xpath = "//li[@class='pagination__item--next']/a"
        product_url_xpath = ".//a[@data-selector='LIST_Item_TitleLink']/@href"
        not_tested_xpath = ".//span[@data-selector='ProductScore_NotTested']"

        selector = browser.get(response.url, timeout=10)
        login_url_xpath = "//*[@data-selector='login']//a[contains(text(), 'Entra')]/@href"
        login_url = self.extract(selector.xpath(login_url_xpath))
        if login_url:
            selector = browser.get(login_url, timeout=10)

        category = response.meta['category']
        while True:
            products = selector.xpath(products_xpath)
            for product in products:
                not_tested = product.xpath(not_tested_xpath)
                if not_tested:
                    continue

                product_url = self.extract(product.xpath(product_url_xpath))
                product_url = get_full_url(response, product_url)
                for item in self.parse_review_from_div(category, browser, product_url):
                    yield item

            if browser.is_displayed(next_page_url_xpath):
                selector = browser.click_link(next_page_url_xpath, timeout=10)
            else:
                break

    def parse_review_from_div(self, category, browser, url):
        selector = browser.get(url, timeout=10)
        login_url_xpath = "//*[@data-selector='login']//a[contains(text(), 'Entra')]/@href"
        login_url = self.extract(selector.xpath(login_url_xpath))
        if login_url:
            selector = browser.get(login_url, timeout=10)

        award_xpath = "//div[contains(@class, 'quality-label-wrapper')]"

        product_xpaths = { "PicURL": "//a[@class='carousel__link']/@href",
                           "ProductName": "//div[contains(@class, 'product-info')]/h1/text()"
                         }

        review_xpaths = { "TestSummary": "//div[@data-selector='PR_OurOpinion_Text']/*[not(self::a)]/text()",
                          "SourceTestRating": "//span[@class='quality-badge__value']/text()",
                          "TestPros": "//li[@data-selector='PR_Pros']/text()",
                          "TestCons": "//li[@data-selector='PR_Cons']/text()",
                          "TestVerdict": "//*[@class='quality-badge__info']/text()"
                        }

        summary_alt_xpath = "//div[@data-type='PsfProductDetailController']//div[@class='grid-wrap']/div[contains(@class,'grid-col')][2]//text()"

        product = ProductItem()
        product["ProductName"] = self.extract(selector.xpath(product_xpaths["ProductName"]))
        product["PicURL"] = self.extract(selector.xpath(product_xpaths["PicURL"]))
        product["OriginalCategoryName"] = category['category_path']
        product["TestUrl"] = browser.browser.current_url

        review = ReviewItem()
        review["DBaseCategoryName"] = "PRO"
        review["TestUrl"] = product["TestUrl"]
        review["TestSummary"] = self.extract_all(selector.xpath(review_xpaths["TestSummary"]))
        if not review["TestSummary"]:
            review["TestSummary"] = self.extract_all(selector.xpath(summary_alt_xpath))
        review["ProductName"] = product["ProductName"]
        review["TestTitle"] = product["ProductName"]

        review["SourceTestRating"] = self.extract(selector.xpath(review_xpaths["SourceTestRating"]))
        review["TestPros"] = self.extract_all(selector.xpath(review_xpaths["TestPros"]), separator=" ; ")
        review["TestCons"] = self.extract_all(selector.xpath(review_xpaths["TestCons"]), separator=" ; ")
        review["TestVerdict"] = self.extract_all(selector.xpath(review_xpaths["TestVerdict"]))

        award = selector.xpath(award_xpath)
        if award:
            review['award'] = self.extract_all(award.xpath(".//text()"))
            badge_text = self.extract_all(award.xpath("./@data-selector"))
            # Save the image of the award from the page and return us the hosted address of the image
            review['AwardPic'] = browser.screenshot_element(award_xpath,
                                                            self.spider_conf['source_id'],
                                                            badge_text)
        yield product
        yield review
