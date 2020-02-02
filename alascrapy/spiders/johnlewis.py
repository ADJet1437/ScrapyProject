__author__ = 'leonardo'

from scrapy.http import Request

from alascrapy.spiders.base_spiders.bazaarvoice_spider import BazaarVoiceSpider
from alascrapy.items import CategoryItem, ProductIdItem
from alascrapy.lib.generic import get_full_url

class JohnLewisSpider(BazaarVoiceSpider):
    name = 'johnlewis'
    start_urls = ['https://www.johnlewis.com/']
    source_id = 49000080
    custom_settings = {'COOKIES_ENABLED': True}

    bv_subdomain = "johnlewis.ugc.bazaarvoice.com"
    bv_site_locale = "7051redes-en_gb"

    def parse(self, response):
        categories_xpath = "//span[@class='inner' and " \
                           "(contains(text(), 'Electrical') or contains(text(), 'Beauty'))]/../.." \
                           "//div[contains(@class, nn-flyout-col) and " \
                           "not(contains(@class, 'nn-col-higlighted'))]" \
                           "/ul[@class='first']/li/a"
        category_url_xpath = "./@href"

        categories = response.xpath(categories_xpath)

        for category_sel in categories:
            category_url = self.extract(category_sel.xpath(category_url_xpath))
            category_url = get_full_url(response, category_url)
            request = Request(category_url, callback=self.parse_category)
            yield request

    def parse_category(self, response):
        is_leaf_xpath ="//*[@id='product-grid']"
        category_path_xpath = "//div[@id='breadcrumbs']//li[not(@class)]//text()"
        category_leaf_xpath = "//div[@id='breadcrumbs']//li[@class='last']//text()"
        if response.xpath(is_leaf_xpath):
            next_page_xpath = "(//li[@class='next']/a)[1]/@href"

            category = response.meta.get('category', None)
            if not category:
                category = CategoryItem()
                category['category_url'] = response.url
                category['category_leaf'] = self.extract(
                    response.xpath(category_leaf_xpath))
                category['category_path'] = self.extract_all(
                    response.xpath(category_path_xpath), separator=' | ')
                category['category_path'] = '%s | %s' % (category['category_path'],
                                                         category['category_leaf'])
                yield category

            if self.should_skip_category(category):
                return

            products_xpath = "//div[@class='result-row']/article"
            product_url_xpath = "./a[contains(@class,'product-link')]/@href"
            product_rating_xpath = "./p[@class='inline-ratings']"

            products = response.xpath(products_xpath)
            for product in products:
                has_reviews = self.extract(
                    product.xpath(product_rating_xpath))

                if has_reviews:
                    product_url = self.extract(product.xpath(product_url_xpath))
                    product_url = get_full_url(response, product_url)
                    request = Request(product_url, callback=self.parse_product)
                    request.meta['category'] = category
                    yield request

            next_page_url = self.extract(response.xpath(next_page_xpath))
            if next_page_url:
                next_page_url = get_full_url(response, next_page_url)
                request = Request(next_page_url, callback=self.parse_category)
                request.meta['category'] = category
                yield request
        else:
            level = response.meta.get('level', 0)
            if level < 2:
                # Right now we can only hard code special cases, as there is no general way to get all the categories
                category_leaf = self.extract(response.xpath(category_leaf_xpath))
                if 'food processors' in category_leaf.lower():
                    subcat_url_xpath = "(//section[ contains(@class, " \
                                       "'lt-nav-container-links') and header[not(contains(., 'Offers'))] ])//li/a/@href"
                else:
                    subcat_url_xpath = "(//section[contains(@class, " \
                                       "'lt-nav-container-links') and header[not(contains(., 'Offers'))] ])[1]//li/a/@href"
                subcat_urls = self.extract_list(response.xpath(subcat_url_xpath))
                for subcat_url in subcat_urls:
                    subcat_url = get_full_url(response, subcat_url)
                    request = Request(subcat_url, callback=self.parse_category)
                    response.meta['level'] = level+1
                    yield request

    def parse_product(self, response):
        category = response.meta['category']
        product_xpaths = \
            { "ProductName": "//h1[@id='prod-title']/span[@itemprop='name']/text()",
              "PicURL": "//ul[@class='wrapper']//img[@itemprop='image']/@src",
              "source_internal_id": "//*[@itemprop='productID']/@content",
              "ProductManufacturer": "//*[@itemprop='brand']//text()"
            }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        
        if not product['source_internal_id']:
            return

        product['OriginalCategoryName'] = category['category_path']
        product["TestUrl"] = response.url
        if product["PicURL"][0:2] == '//':
            product["PicURL"] = "http:" + product["PicURL"]
        yield product

        product_id = ProductIdItem()
        product_id['source_internal_id'] = product["source_internal_id"]
        product_id['ProductName'] = product["ProductName"]
        product_id['ID_kind'] = "johnlewis_id"
        product_id['ID_value'] = product["source_internal_id"]
        yield product_id

        mpn_xpath = "//div[@class='tab-content']//dt[contains(text(),'Manufacturer Part Number')]/following-sibling::dd/text()"
        mpn_alt_xpath = "//div[@class='tab-content']//dt[contains(text(),'MPN')]/following-sibling::dd/text()"
        mpn_value = self.extract(response.xpath(mpn_xpath))
        if not mpn_value:
            mpn_value = self.extract(response.xpath(mpn_alt_xpath))
        if mpn_value:
            mpn = self.product_id(product, kind='MPN', value=mpn_value)
            yield mpn

        request = self.start_reviews(response, product, filter_other_sources=False)
        request.meta['product'] = product
        yield request
