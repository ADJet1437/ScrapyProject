__author__ = 'leonardo'
import re
from scrapy.http import Request

from alascrapy.spiders.base_spiders.bazaarvoice_spiderAPI5_5 import BazaarVoiceSpiderAPI5_5
from alascrapy.items import CategoryItem, ProductItem
from alascrapy.lib.generic import get_full_url, strip
from alascrapy.lib.selenium_browser import SeleniumBrowser, uses_selenium


class SibaSESpider(BazaarVoiceSpiderAPI5_5):
    name = 'siba_se'
    start_urls = ['http://www.siba.se/']
    bv_base_params = {'passkey': 'q0y51ewk3209bocndd176bpga',
                      'display_code': '16232-sv_se',
                      'content_locale': 'no_NO,sv_SE'}

    sii_re = re.compile("-(\d+)$")
    name_re = re.compile("(.*)-\s*Art.nr:")

    def parse(self, response):
        top_subcategories_xpath = "//div[@class='big-menu']//h2/a/@href"
        category_home_urls = self.extract_list(
            response.xpath(top_subcategories_xpath))

        for category_home_url in category_home_urls:
            category_home_url = get_full_url(response, category_home_url)
            request = self.selenium_request(category_home_url,
                              callback=self.parse_category_home)
            yield request

    @uses_selenium
    def parse_category_home(self, response):
        categories_xpath = "//ul[@class='product-nav']//a/@href"
        category_urls = self.extract_list(
            response.xpath(categories_xpath))

        for category_url in category_urls:
            category_url = get_full_url(response, category_url)
            request = self.selenium_request(category_url,
                                            callback=self.parse_category_home)
            yield request

        if not category_urls:
            for request in self.parse_category(response):
                yield request

    def call_products(self, response, selector, category):
        products_xpath = "//div[@product-id]"
        product_url_xpath = ".//h2/a/@href"
        product_rating_xpath = ".//span[@class='bv-rating-label']/text()"
        bv_id_xpath = "substring-after(.//div[@class='ratings']/@id, 'product-rating-')"
        products = selector.xpath(products_xpath)
        for product in products:
            # reviewCount for a product on page is with pattern '(42)'
            reviewCount = self.extract_xpath(product, product_rating_xpath)
            if reviewCount and reviewCount != '(0)':
                product_url = self.extract_xpath(product, product_url_xpath)
                product_url = get_full_url(response, product_url)
                bv_id = self.extract_xpath(product, bv_id_xpath)
                request = Request(product_url, callback=self.parse_product)
                request.meta['category'] = category
                request.meta['bv_id'] = bv_id
                yield request

    @uses_selenium
    def parse_category(self, response):
        category = response.meta.get('category', None)
        if not category:
            category_path_xpath = "//ul[@id='breadcrumb']/li[contains(@class, 'level-')]//text()"
            category = CategoryItem()
            category['category_url'] = response.url
            category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
            yield category

        if self.should_skip_category(category):
            return

        has_next_page = True
        with SeleniumBrowser(self, response) as browser:
            selector = browser.get(response.url)
            while has_next_page:
                for request in self.call_products(response, selector, category):
                    yield request

                next_page_xpath = "//a[contains(@class, 'nextBTN')]/@href"
                next_page = self.extract_xpath(selector, next_page_xpath)
                has_next_page = bool(next_page)
                if next_page:
                    next_page = get_full_url(response, next_page)
                    selector =  browser.get(next_page)



    def parse_product(self, response):
        category = response.meta['category']
        category_path_xpath = "//ul[@id='breadcrumb']/li[contains(@class, 'level-') and ./a]/a/text()"

        if not category:
            category = self.extract_all(response.xpath(category_path_xpath), ' | ')

        product_name = self.extract(response.xpath("//div[@class='product-title']/h2/text()"))
        name_match = re.search(self.name_re, product_name)
        if name_match:
            product_name = strip(name_match.group(1))

        match = re.search(self.sii_re, response.url)
        if not match:
            raise Exception("Cant extract source_internal_id")
        product_internal_id = match.group(1)

        product_pic_url = self.extract_xpath(response,
                                             "//meta[@property='og:image']/@content")

        product = ProductItem.from_response(
            response,
            category=category,
            product_name=product_name,
            source_internal_id=product_internal_id,
            url=response.url,
            pic_url=product_pic_url
        )
        yield product

        for review in self.call_review(response, product=product):
            yield review
