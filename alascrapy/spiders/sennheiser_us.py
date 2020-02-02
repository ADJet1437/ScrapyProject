__author__ = 'leonardo'

import re
import js2xml

from scrapy.http import Request
from scrapy.selector import Selector

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.items import CategoryItem, ProductItem
from alascrapy.lib.generic import get_full_url, parse_float, normalize_price
from alascrapy.lib.selenium_browser import SeleniumBrowser


class SennheiserUsSpider(AlaSpider):
    name = 'sennheiser_us'
    start_urls = ['http://en-us.sennheiser.com/headphones',
                  'http://en-us.sennheiser.com/headsets',
                  'http://en-us.sennheiser.com/loudspeaker-microphone',
                  'http://en-us.sennheiser.com/microphones']

    products_re= re.compile('sennheiser_tracking_data\.products\s*=\s*([^;]+)')
    mpn_re = re.compile('article\sno.\s(\d+)', re.IGNORECASE)
    sii_re = re.compile('/shop/out\?id=(\d+)')
    sii_alt_re = re.compile('/articles/(\d+)\?context=product_teaser')
    #custom_settings = {'COOKIES_ENABLED': True}

    def _parse_cat(self, response, root_cat, cat_xpath, cat_url_xpath,
                   cat_leaf_xpath):
        category_html = response.xpath(cat_xpath)

        for category_sel in category_html:
            category_url = self.extract(category_sel.xpath(cat_url_xpath))
            if category_url:
                category_url = get_full_url(response.url, category_url)

                category = CategoryItem()
                category['category_url'] = category_url
                category['category_leaf'] = self.extract(category_sel.xpath(cat_leaf_xpath))
                category['category_path'] = "%s | %s" % (root_cat,
                                                         category['category_leaf'])
                yield category

                request = Request(category_url, callback=self.parse_category)
                request.meta['category'] = category
                yield request


    def parse(self, response):
        category_xpath = "//a[@class='category-navigation__list__item__link']"
        category_url_xpath = "./@href"
        category_leaf_xpath = ".//text()"

        category_xpath_2 = "//a[@class='product-group__link']"
        category_url_xpath_2 = "./@href"
        category_leaf_xpath_2 = ".//h2/text()"

        root_cat_name_xpath = "//li[@class='breadcrumbs__list__item'][last()]/text()"
        root_cat_name = self.extract_xpath(response, root_cat_name_xpath)

        for item in self._parse_cat(response, root_cat_name, category_xpath,
                                    category_url_xpath, category_leaf_xpath):
            yield item

        for item in self._parse_cat(response, root_cat_name, category_xpath_2,
                                    category_url_xpath_2,
                                    category_leaf_xpath_2):
            yield item

    def extract_product_requests(self, response, selector=None):
        if selector:
            _selector = selector
        else:
            _selector = response

        product_url_xpath = "//h3[@class='product-teaser__headline']//a/@href"
        product_urls = self.extract_list_xpath(_selector, product_url_xpath)
        for product_url in product_urls:
            product_url = get_full_url(response, product_url)
            request = Request(product_url, callback=self.parse_product)
            request.meta['category'] = response.meta['category']
            yield request

    def errback(self, failure):
        error_msg = "Error parsing: %s\nTraceback: %s"

        self.logger.error(error_msg % (str(failure.getErrorMessage()),
                                       str(failure.getTraceback())) )

    def parse_category(self, response):
        category = response.meta['category']
        level = response.meta.get('level', 0)
        if 'aviation' in category['category_url']:
            return

        if 'gaming' in category['category_url'] and level==0:
            subcat_url_xpath = "//a[@class='category-navigation__list__item__link']/@href"
            subcat_urls = self.extract_list_xpath(response, subcat_url_xpath)
            for subcat_url in subcat_urls:
                subcat_url = get_full_url(response, subcat_url)
                request = Request(subcat_url, callback=self.parse_category)
                request.meta['category'] = category
                request.meta['level'] = level+1
                yield request

        for request in self.extract_product_requests(response):
            yield request

        next_page_xpath = "(//*[@rel='next'])[1]/@href"
        next_page_url = self.extract_xpath(response, next_page_xpath)
        if next_page_url:
            next_page_url = get_full_url(response, next_page_url)
            #request = Request(next_page_url, callback=self.parse_cat_javascript,
            #                  headers={'Accept':'application/javascript'})
            request = Request(next_page_url, callback=self.parse_category, meta=response.meta)
            request.meta['category'] = category
            yield request


    def parse_cat_javascript(self, response):
        inner_html_xpath = "//functioncall/function/dotaccessor/object[" \
                      ".//string/text()='#search-results__resultlist']/../../following-sibling::arguments/string/text()"
        next_page_url_xpath = "//functioncall/function/dotaccessor" \
                              "/object[contains(.//string/text(), " \
                              "                 '.search-results__footer') " \
                              "and contains(.//string/text(), '.button')]/../" \
                              "../following-sibling::arguments/string[2]/text()"


        parsed_js = js2xml.parse(response.body)
        inner_htmls = parsed_js.xpath(inner_html_xpath)
        next_page = parsed_js.xpath(next_page_url_xpath)

        for inner_html in inner_htmls:
            inner_html_selector = Selector(text=inner_html)
            for request in self.extract_product_requests(response, inner_html_selector):
                yield request

        if next_page:
            next_page_url = next_page[0]
            next_page_url = get_full_url(response, next_page_url)
            request = Request(next_page_url,
                              callback=self.parse_cat_javascript,
                              headers={'Accept':'application/javascript'})
            request.meta['category'] = response.meta['category']
            yield request


    def _parse_product(self, response, selector=None):
        if not selector:
            selector=response
        category = response.meta['category']
        product_name_xpath = "//h1[@class='product-stage__headline']/text()"
        pic_xpath = "//meta[@property='og:image']/@content"
        price_xpath = "//*[@class='product-stage__price__current']/text()"
        description_xpath = "//div[@class='product-stage__description']/text()"
        product_name = self.extract_xpath(selector, product_name_xpath)
        if not 'sennheiser' in product_name.lower():
            product_name = "Sennheiser %s" % product_name

        pic_url = self.extract_xpath(selector, pic_xpath)
        price = self.extract_xpath(selector, price_xpath)

        mpn=None
        descriptions = self.extract_list_xpath(selector, description_xpath)
        for description in descriptions:
            match = re.search(self.mpn_re, description)
            if match:
                mpn = int(match.group(1))

        if not mpn:
            return

        product = ProductItem.from_response(response, category=category,
                                            product_name=product_name,
                                            source_internal_id=mpn,
                                            manufacturer='Sennheiser', pic_url=pic_url)
        yield product

        if price:
            price = normalize_price(parse_float(price))
            price_pi = self.product_id(product, kind='price', value=price)
            yield price_pi

        if mpn:
            mpn_pi = self.product_id(product, kind='MPN', value=mpn)
            yield mpn_pi
            sennheiser_id_1 = self.product_id(product, kind='sennheiser_id',
                                              value=mpn)
            yield  sennheiser_id_1


    def parse_color_variants(self, response, variant_urls, browser):
        xpath = "//li[contains(@class, 'product-stage__colors__color')]/a[@href='%s']/.."
        for variant_url in variant_urls:
            selector = browser.click(xpath % variant_url)
            for item in self._parse_product(response, selector):
                yield item

    def parse_product(self, response):
        select_xpath = "//*[contains(@class, 'product-stage')]" \
                 "//select[contains(@class, 'select_to')]"

        select_values_xpath = "//*[contains(@class, 'product-stage')]" \
                        "//select[contains(@class, 'select_to')]/option/@value"
        color_variant_url_xpath = "//li[contains(@class, 'product-stage__colors__color')]/a/@href"
        color_variants = self.extract_list_xpath(response,
                                                color_variant_url_xpath)
        select = response.xpath(select_xpath)

        if select or color_variants:
            with SeleniumBrowser(self, response, no_images=False,
                                 no_css=False) as browser:
                browser.get(response.url)
                if select:
                    select_values = self.extract_list_xpath(response,
                                                            select_values_xpath)

                    for value in select_values:
                        if not value:
                            return
                        selector = browser.select_by_value(select_xpath, value)
                        color_variants = self.extract_list_xpath(selector, color_variant_url_xpath)
                        if color_variants:
                            for item in self.parse_color_variants(response,
                                                                  color_variants,
                                                                  browser=browser):
                                yield item
                        else:
                            for item in self._parse_product(response, selector):
                                yield item
                elif color_variants:
                    for item in self.parse_color_variants(response,
                                                          color_variants,
                                                          browser):
                        yield item
        else:
            for item in self._parse_product(response):
                yield item


