from scrapy.http import Request

from alascrapy.spiders.base_spiders.bazaarvoice_spiderAPI5_5 import BazaarVoiceSpiderAPI5_5
from alascrapy.items import CategoryItem, ProductItem
from alascrapy.lib.generic import get_full_url


class CanonUsSpider(BazaarVoiceSpiderAPI5_5):
    name = 'canon_us'
    start_urls = ['https://www.usa.canon.com/internet/portal/us/home/products']
    custom_settings = {'MAX_SELENIUM_REQUESTS': 3}
    bv_base_params = {'passkey': 'b86nnnq12y162hppr4mbxp4x7',
                      'display_code': '3798-en_us',
                      'content_locale': 'en_US'}

    def parse(self, response):
        top_subcategories_xpath = "id('RIBBONID')/div/div/div/div/div/div[2]/ul/li/a/@href"
        category_home_urls = self.extract_list(
            response.xpath(top_subcategories_xpath))

        for category_home_url in category_home_urls:
            category_home_url = get_full_url(response, category_home_url)
            request = Request(category_home_url, callback=self.parse_category_home)
            yield request


    def parse_category_home(self, response):
        categories_xpath = "//ul[starts-with(@id,'categoryFacetList_')]/li[contains(@class,'singleFacet')]/a/@href"

        category_urls = self.extract_list(
            response.xpath(categories_xpath))

        for category_url in category_urls:
            category_url = get_full_url(response, '/shop/en/catalog/' + category_url)
            request = Request(category_url, callback=self.parse_category)
            yield request

    def parse_category(self, response):
        products_xpath = "//div[contains(@class,'product_info')]"
        product_url_xpath = ".//div[contains(@class,'product_name')]/a/@href"
        product_rating_xpath = ".//div[contains(@class,'product_rating')]/text()[2]"

        products = response.xpath(products_xpath)
        for product in products:
            # reviewCount for a product on page is with pattern '(42)'
            reviewCount = self.extract(product.xpath(product_rating_xpath))
            if reviewCount and reviewCount != '(0)':
                product_url = self.extract(product.xpath(product_url_xpath))
                product_url = get_full_url(response, product_url)
                request = Request(product_url, callback=self.parse_product)
                yield request

        #TODO: Pagination

    def parse_product(self, response):
        category_url_xpath = "id('widget_breadcrumb')/ul/li[last()-1]/a/@href"
        category_leaf_xpath = "id('widget_breadcrumb')/ul/li[last()-1]/a/text()"
        category_path_xpath = "id('widget_breadcrumb')/ul/li/a/text()"

        category = CategoryItem()
        category_url = self.extract(response.xpath(category_url_xpath))
        category['category_url'] = get_full_url(response, category_url)
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')

        if self.should_skip_category(category):
            return
        yield category

        product_name = self.extract(response.xpath("//h1/span[@itemprop='name']/text()"))
        product_internal_id = self.extract(response.xpath("//input[starts-with(@id, 'ProductInfoPartNumber_')]/@value"))

        product_url = self.extract(response.xpath("//link[@rel='canonical']/@href"))
        product_pic_url = get_full_url(response,self.extract(response.xpath("id('productMainImage')/@src")))

        product = ProductItem.from_response(
            response,
            category=category,
            product_name=product_name,
            source_internal_id=product_internal_id,
            url=product_url,
            manufacturer='Canon',
            pic_url=product_pic_url
        )
        yield product

        mpn = self.extract_xpath(response, "//input[@id='product_sku_da']/@value")
        product_id = self.product_id(product, "MPN", mpn)
        yield product_id

        for review in self.call_review(response, product=product):
            yield review
