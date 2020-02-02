__author__ = 'leonardo'

from urlparse import urlparse
import re

from alascrapy.spiders.base_spiders.rm_spider import RMSpider
from alascrapy.spiders.base_spiders.bazaarvoice_spider import BazaarVoiceSpider
from alascrapy.lib.selenium_browser import SeleniumBrowser, uses_selenium
from alascrapy.items import ProductIdItem


class RicheroundsRMSpider(RMSpider, BazaarVoiceSpider):
    name = 'richersounds_rm'
    allowed_domains = ['richersounds.com']

    source_internal_id_re = re.compile("/(.*)$")

    @uses_selenium
    def parse(self, response):
        #Must use only product_page
        product_xpaths = { "PicURL": "(//*[@property='og:image'])[1]/@content",
                           "ProductName": "//h1/span[@itemprop='name']/text()",
                           "ProductManufacturer": "(//h1/span[@itemprop='name']/text())[1]"
                         }


        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        parsed_url = urlparse(response.url)

        match = re.search(self.source_internal_id_re, parsed_url.path)
        if match:
            product["source_internal_id"] = match.group(1)

            product_id = ProductIdItem()
            product_id['source_internal_id'] = product["source_internal_id"]
            product_id['ProductName'] = product["ProductName"]
            product_id['ID_kind'] = "richersounds_id"
            product_id['ID_value'] = product["source_internal_id"]
            yield product_id
            yield product
            yield self.get_rm_kidval(product, response)

            reviews_xpath="//h4/a[contains(@href,'review')]"

            with SeleniumBrowser(self, response) as browser:
                browser.get(response.url)
                selector = browser.click(reviews_xpath)

                response.meta['browser'] = browser
                response.meta['product'] = product
                response.meta['product_id'] = product_id
                response.meta['_been_in_decorator'] = True

                for review in self.parse_reviews(response, selector=selector):
                    yield review