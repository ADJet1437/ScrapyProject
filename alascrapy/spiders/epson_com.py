from urlparse import urlparse, parse_qs

from scrapy.http import Request

from alascrapy.spiders.base_spiders.bazaarvoice_spiderAPI5_5 import BazaarVoiceSpiderAPI5_5
from alascrapy.items import CategoryItem, ProductIdItem
from alascrapy.lib.selenium_browser import SeleniumBrowser, uses_selenium
from alascrapy.lib.generic import get_full_url

#TODO

class EpsonComSpider(BazaarVoiceSpiderAPI5_5):
    name = 'epson_com'
    start_urls = ['https://www.epson.com/']

    def parse():
        category_url_xpath = "//li/a[starts-with(@href, '/c/')]/@href"
        categories_urls = self.extract_list_xpathr(response,  '#reviews')
        request = Request

    def parse_product(self, response):
        products_xpath = "//*[@class='product-block']"
        product_url_xpath = ".//*[@class='product-details']/h3/a/@href"
        next_page_xpath = "//*[@class='btm-pagination']//li[@class='next']"

        products = response.xpath(products_xpath)

        for product in products:
            product_url = self.extract(product.xpath(product_url_xpath))
            product_url = get_full_url(response, product_url)
            request = self.selenium_request(url=product_url,
                                            callback=self.parse_product)
            yield request

        next_page = self.extract(response.xpath(next_page_xpath))
        if next_page:
            next_page = get_full_url(response, next_page)
            request = Request(next_page, callback=self.parse)
            yield request

    @uses_selenium
    def parse_product(self, response):
        has_reviews_xpath = "//script[contains(text(), '#reviews')]"

        category_url_xpath = "//p[@id='breadcrumb']/a[last()]/@href"
        category_leaf_xpath = "//p[@id='breadcrumb']/a[last()]/text()"
        category_path_xpath = "//p[@id='breadcrumb']/a[position()>2]/text()"

        category = CategoryItem()
        category_url = self.extract(response.xpath(category_url_xpath))
        category['category_url'] = get_full_url(response, category_url)
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')

        reviews_xpath = "(//*[@id='BVRRRatingSummaryLinkReadID']/a)[1]"

        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = \
            { "ProductName": "//*[@id='title-hd']/h1/text()",
              "PicURL": "//*[@class='image-wrapper']//img/@src"
            }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        parsed_url = urlparse(response.url)
        query_params = parse_qs(parsed_url[4])

        product['source_internal_id'] = query_params['sku'][0]
        product['PicURL'] = get_full_url(response, product['PicURL'])
        product['OriginalCategoryName'] = category['category_path']
        product["ProductManufacturer"] = "Epson"
        product["TestUrl"] = response.url
        yield product

        product_id = ProductIdItem()
        product_id['source_internal_id'] = product["source_internal_id"]
        product_id['ProductName'] = product["ProductName"]
        product_id['ID_kind'] = "MPN"
        product_id['ID_value'] = product["source_internal_id"]
        yield product_id

        with SeleniumBrowser(self, response) as browser:
            browser.get(response.url, timeout=10)
            selector = browser.click(reviews_xpath, timeout=10)

            response.meta['browser'] = browser
            response.meta['product'] = product
            response.meta['product_id'] = product_id
            response.meta['_been_in_decorator'] = True
            for review in self.parse_reviews(response, selector, incremental=True):
                yield review