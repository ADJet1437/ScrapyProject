import re
from scrapy.http import Request

from alascrapy.spiders.base_spiders.bazaarvoice_spider import BazaarVoiceSpider
from alascrapy.items import CategoryItem, ProductIdItem
from alascrapy.lib.generic import get_full_url


class XeroxUsSpider(BazaarVoiceSpider):
    name = 'xerox_us'
    start_urls = ['http://www.office.xerox.com/digital-printing-equipment/enus.html']
    source_id = 10000476
    bv_subdomain = "xerox.ugc.bazaarvoice.com"
    bv_site_locale = "7352alt-en_us"

    def parse(self, response):
        top_subcategories_xpath = "//li[contains(@class,'xrx_category_head_menu_category')]//a/@href"
        category_home_urls = self.extract_list(
            response.xpath(top_subcategories_xpath))

        for category_home_url in category_home_urls:
            category_home_url = get_full_url(response, category_home_url)
            request = Request(category_home_url, callback=self.parse_category)
            yield request


    def parse_category(self, response):
        products_xpath = "//*[contains(@class,'xrx_product_wrapper')]"
        product_url_xpath = ".//*[contains(@class, 'xrx_padding_image')]/a/@href"
        has_reviews_xpath = ".//*[contains(@class,'xrx_bazaarvoice_avg_rating_image') \
            and not(contains(text(),'(0)'))]"

        products = response.xpath(products_xpath)
        for product in products:
            has_reviews = self.extract(product.xpath(has_reviews_xpath))

            if has_reviews:
                product_url = self.extract(product.xpath(product_url_xpath))
                product_url = get_full_url(response, product_url)
                request = Request(product_url, callback=self.parse_product)
                yield request

    def parse_product(self, response):
        category_url_xpath = "//*[contains(@class,'xrx_path_web_navigation')]//a[not(@class='xrx_disable_link')][last()]/@href"
        category_leaf_xpath = "//*[contains(@class,'xrx_path_web_navigation')]//a[not(@class='xrx_disable_link')][last()]/text()"
        category_path_xpath = "//*[contains(@class,'xrx_path_web_navigation')]//a[not(@class='xrx_disable_link')]/text()"

        category = CategoryItem()
        category_url = self.extract(response.xpath(category_url_xpath))
        category['category_url'] = get_full_url(response, category_url)
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')

        if self.should_skip_category(category):
            return
        yield category

        sii_url_xpath = "//li[@id='xrx_bnrv4_header_country_selector']/a/@href"
        #TODO: fix more than one MPN
        product_xpaths = \
            { "ProductName": "//div[@class='xrx_contain_text_hero_banner']/h3/text()",
              "PicURL": "//*[@class='xrx_hero_image_specs']/img/@src"
            }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)

        sii_url = self.extract_xpath(response, sii_url_xpath)
        sii_re = "product=([^&;]+)"

        sii_match = re.search(sii_re, sii_url)
        if not sii_match:
            raise Exception("Can't extract sii")

        product['source_internal_id'] = sii_match.group(1)
        product['PicURL'] = get_full_url(response, product['PicURL'])
        product['OriginalCategoryName'] = category['category_path']
        product['ProductManufacturer'] = "Xerox" # a bit of a wild guess here ;)
        product["TestUrl"] = response.url
        yield product

        product_id = ProductIdItem()
        product_id['source_internal_id'] = product["source_internal_id"]
        product_id['ProductName'] = product["ProductName"]
        product_id['ID_kind'] = "MPN"
        product_id['ID_value'] = product["source_internal_id"]
        yield product_id

        request = self.start_reviews(response, product)
        yield request
