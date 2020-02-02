__author__ = 'leonardo'

import re

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider

from alascrapy.lib.generic import get_full_url
from alascrapy.lib.selenium_browser import SeleniumBrowser, uses_selenium
from alascrapy.items import CategoryItem, ProductItem

class VodafoneESSpider(AlaSpider):
    name = 'vodafone_es'
    start_urls = ['http://www.vodafone.es/tienda/particulares/es/catalogo-moviles/',
                  'http://www.vodafone.es/tienda/particulares/es/catalogo-moviles/prepago/']

    product_name_re = re.compile('precio\s(.*)\|', re.IGNORECASE)

    def parse(self, response):
        product_page_xpath = "//li[contains(@class, 'parentTerminal')]//a[contains(@class, 'btn') and not(contains(@href, 'movil/tarjeta'))]/@href"

        category = CategoryItem()
        category['category_path'] = "Cell Phones"
        yield category

        with SeleniumBrowser(self, response,
                             no_images=False, no_css=False) as browser:
            selector = browser.get(response.url)
            product_urls = self.extract_list_xpath(selector, product_page_xpath)
            for product_url in product_urls:
                product_url = get_full_url(response.url, product_url)
                request = self.selenium_request(product_url,
                                                callback=self.parse_product)
                request.meta['category'] = category
                yield request

    @uses_selenium
    def parse_product(self, response):
        color_url_xpath = "//fieldset[contains(@class, 'color-picker')]/ul/li/a/@href"
        size_id_xpath = "//fieldset[contains(@class, 'size-picker')]//input/@id"
        single_size_xpath = "//fieldset[contains(@class, 'size-picker')]//input[@id='%s']/following-sibling::label[1]"

        with SeleniumBrowser(self, response, no_images=False, no_css=False) as browser:
            selector = browser.get(response.url)
            color_urls = self.extract_list_xpath(selector, color_url_xpath)
            for color_url in color_urls:
                color_url = get_full_url(response.url, color_url)
                selector = browser.get(color_url)
                size_ids = self.extract_list_xpath(selector, size_id_xpath)

                for size_id in size_ids:
                    selector = browser.click(single_size_xpath % size_id)
                    for item in self._parse_product(response, browser,
                                                    selector):
                        yield item

    def _parse_product(self, response, browser, selector):
        category = response.meta['category']
        product_name_xpath = "//meta[@name='title']/@content"
        pic_xpath = "//meta[@property='og:image']/@content"
        manufacturer_xpath = "//meta[@name='search_phone_manufacturer']/@content"
        source_internal_id_xpath = "//input[contains(@id, 'idSapNoOutlet')]/@value"
        product_url = browser.browser.current_url
        _product_name = self.extract_xpath(selector, product_name_xpath)
        match = re.search(self.product_name_re, _product_name)
        if match:
            product_name = match.group(1)
        else:
            raise Exception("Could not extract product name %s" % product_url)

        pic_url = self.extract_xpath(selector, pic_xpath)
        manufacturer = self.extract_xpath(selector, manufacturer_xpath)
        source_internal_id = self.extract_xpath(selector, source_internal_id_xpath)

        if not source_internal_id:
            raise Exception("Could not extract sii %s" % product_url)

        product = ProductItem.from_response(response, category=category, product_name=product_name,
                                            source_internal_id=source_internal_id,
                                            manufacturer=manufacturer, pic_url=pic_url, url=product_url)
        yield product

        vodafone_id = self.product_id(product, kind='SAPContrato',
                                      value=source_internal_id)
        yield  vodafone_id




