# coding:utf-8

from scrapy.http import Request
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_query_parameter, get_full_url
from alascrapy.lib.selenium_browser import SeleniumBrowser
from alascrapy.items import CategoryItem, ProductItem, ReviewItem


class RadRonSpider(AlaSpider):
    name = 'radron'
    allowed_domains = ['radron.se']
    start_urls = ['http://www.radron.se/tester/']

    custom_settings = {'COOKIES_ENABLED': True,
                       'DOWNLOADER_MIDDLEWARES':
                           {'alascrapy.middleware.user_agent_middleware.RotateUserAgentMiddleware': None}}

    @staticmethod
    def login_selenium(browser):
        username_xpath = "//input[@type='text' and @placeholder='Användarnamn']"
        password_xpath = "//input[@placeholder='Lösenord']"
        login_button = "//ul[@class='quick-navigation']//a[contains(@href, 'logga-in')]"
        browser.get("http://www.radron.se/")
        browser.click_link(login_button)
        browser.write_in_field(username_xpath, "134544386")
        browser.write_in_field(password_xpath, "11820")
        browser.click("//a[contains(@id, 'LoginButton')]")
        return browser.browser.get_cookies()


    def parse(self, response):
        cookies = response.meta.get('cookies', None)
        if not cookies:
            with SeleniumBrowser(self, response,
                                 no_images=False, no_css=False) as browser:
                cookies = self.login_selenium(browser)

        cat_url_xpath = "//footer[@class='report-category__footer']/a/@href"
        cat_urls = self.extract_list_xpath(response, cat_url_xpath)
        for cat_url in cat_urls:
            cat_url = get_full_url(response, cat_url)
            request = Request(cat_url, callback=self.parse_category_leafs)
            request.meta['cookies'] = cookies
            yield request


    def parse_category_leafs(self, response):
        cookies = response.meta['cookies']

        parent_category_xpath = "//h1[@class='content__heading']/text()"
        category_xpath = "//li[@class='link-list__item']"
        category_url_xpath = "./a/@href"
        category_name_xpath = ".//span/text()"

        parent_category = self.extract_xpath(response, parent_category_xpath)
        categories = response.xpath(category_xpath)

        for _category in categories:
            category_name = self.extract_xpath(_category, category_name_xpath)
            category_url = self.extract_xpath(_category, category_url_xpath)
            category_url = get_full_url(response, category_url)

            category = CategoryItem()
            category['category_path'] = "%s | %s" % (parent_category, category_name)
            category['category_leaf'] = category_name
            yield category

            request = Request(category_url, cookies=cookies,
                              callback=self.parse_category)
            request.meta['category'] = category
            request.meta['cookies'] = cookies
            yield request

    def is_not_logged(self, response):
        not_logged_xpath = "//*[@class='icon-kort-kop']"
        not_logged = response.xpath(not_logged_xpath)
        return bool(not_logged)

    def parse_category(self, response):
        is_not_logged = self.is_not_logged(response)
        if is_not_logged:
            raise Exception("Not Logged: %s" % response.url)

        products_xpath = "//table[@class='products-list']//tr/td[@class='product__image']/parent::tr"
        product_url_xpath = "./td[3]/a/@href"

        products = response.xpath(products_xpath)
        cookies = response.meta['cookies']
        for product in products:
            product_url = self.extract_xpath(product, product_url_xpath)
            product_url = response.url + product_url

            request = Request(product_url, cookies=cookies,
                              callback=self.parse_review)
            request.meta['category'] = response.meta['category']
            yield request


    def parse_review(self, response):
        is_not_logged = self.is_not_logged(response)
        if is_not_logged:
            raise Exception("Not Logged: %s" % response.url)

        product_model_xpath = "//tr[contains(@class, 'model')]/td[@colspan=0]/text()"
        product_manu_xpath = "//tr[contains(@class, 'manufacturer')]/td[@colspan=0]/text()"
        product_pic_url_xpath = "//td[@class='compare-table__image']//img/@src"

        test_date_xpath = "//span[@class='push-property' and contains(text(), 'Datum')]/../following-sibling::td/text()"
        rating_xpath = "//div[@class='c-big-rating__num']/text()"

        category = response.meta['category']

        source_internal_id = get_query_parameter(response.url, 'products')
        product_model = self.extract_xpath(response ,product_model_xpath)
        manufacturer = self.extract_xpath(response, product_manu_xpath)
        product_name = "%s %s" % (manufacturer, product_model)
        pic_url = self.extract_xpath(response, product_pic_url_xpath)
        pic_url = get_full_url(response, pic_url)
        product = ProductItem.from_response(response, category=category,
                                            source_internal_id=source_internal_id,
                                            product_name=product_name, url=response.url,
                                            manufacturer=manufacturer, pic_url=pic_url)
        yield product

        review_verdict = self.build_verdict(response)
        test_date = self.extract_xpath(response, test_date_xpath)

        rating = self.extract_xpath(response, rating_xpath)

        review = ReviewItem.from_product(product=product, tp='PRO', rating=rating,
                                         scale='100', date=test_date, verdict=review_verdict)
        yield review


    def build_verdict(self, response):
        product_result_xpath="//tr[contains(@class,'prop-rating') and contains(@class,'level-0')]"
        product_results = response.xpath(product_result_xpath)
        attribute_label = "./td[@class='compare-table__property']//text()"
        attribute_value = "./td//div[@class='c-rating__num']/text()"

        verdict = []
        labels = set()
        for product_result in product_results:
            label = self.extract_all_xpath(product_result, attribute_label)
            value = self.extract_all_xpath(product_result, attribute_value)
            if label and value and not label in labels:
                verdict.append('%s: %s' % (label, value))
            labels.add(label)
        verdict_str = " ; ".join(verdict)
        return verdict_str

