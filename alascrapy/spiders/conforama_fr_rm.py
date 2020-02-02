__author__ = 'leonardo'
import re

from alascrapy.spiders.base_spiders.rm_spider import RMSpider
from alascrapy.spiders.base_spiders.bazaarvoice_spider import BazaarVoiceSpider
from alascrapy.lib.selenium_browser import SeleniumBrowser, uses_selenium
from alascrapy.items import ProductIdItem


class ConforamaFRRMSpider(RMSpider, BazaarVoiceSpider):
    name = 'conforama_fr_rm'
    allowed_domains = ['conforama.fr']

    source_internal_id_re = re.compile("sku:(\d+)")

    @uses_selenium
    def parse(self, response):
        #Must use only product_page
        category_xpaths = { "category_leaf": "//div[@id='breadcrumb']/a[@class='home']/following-sibling::a[last()-1]/text()"
                          }
        category_path_xpath = "//div[@id='breadcrumb']/a[@class='home']/following-sibling::a/text()"

        product_xpaths = { "PicURL": "(//*[@property='og:image'])[1]/@content",
                           "source_internal_id": "//form[@id='productSheet']/@data-product",
                           "ProductName": "//div[@itemprop='name']/h1/text()",
                           "ProductManufacturer": "//*[@class='nameBrand']/text()"
                         }
        category_path_selector = response.xpath(category_path_xpath)
        category_path_selector = category_path_selector[:-1]

        category = self.init_item_by_xpaths(response, "category", category_xpaths)
        category["category_path"] = self.extract_all(category_path_selector, separator=' | ')
        print category

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product["OriginalCategoryName"] = category["category_path"]

        product_id = ProductIdItem()
        product_id['source_internal_id'] = product["source_internal_id"]
        product_id['ProductName'] = product["ProductName"]
        product_id['ID_kind'] = "conforama_fr_id"
        product_id['ID_value'] = product["source_internal_id"]
        yield product_id

        yield category
        yield product
        yield self.get_rm_kidval(product, response)

        reviews_xpath="//a[@id='rating']"

        with SeleniumBrowser(self, response) as browser:
            browser.get(response.url)
            selector = browser.click(reviews_xpath)

            response.meta['browser'] = browser
            response.meta['product'] = product
            response.meta['product_id'] = product_id
            response.meta['_been_in_decorator'] = True            

            for review in self.parse_reviews(response, selector=selector):
                yield review