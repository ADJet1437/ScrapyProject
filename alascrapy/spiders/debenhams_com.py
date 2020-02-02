__author__ = 'leonardo'

from scrapy.http import Request

from alascrapy.spiders.base_spiders.bazaarvoice_spider import BazaarVoiceSpider
from alascrapy.items import CategoryItem, ProductIdItem
from alascrapy.lib.generic import get_full_url


class JohnLewisSpider(BazaarVoiceSpider):
    name = 'debenhams_com'
    start_urls = ['http://www.debenhams.com']
    source_id = 49000082

    bv_subdomain = "debenhams.ugc.bazaarvoice.com"
    bv_site_locale = "9364redes3-en_gb"

    def parse(self, response):
        electrical_categories_url_xpath = \
            "//li[contains(@class, 'menu-l1-li') and ./a/text()='Electricals']" \
            "//li[@class='menu-l2-li' and not(contains(./div/text(), 'sale')) and not(contains(./div/text(), 'brand'))]" \
            "//li[@class='menu-l3-li']/a/@href"

        beauty_categories_url_xpath = \
            "//li[contains(@class, 'menu-l1-li') and ./a/text()='Beauty']" \
            "//li[@class='menu-l2-li' and contains(./div/text(), 'category')]//li[@class='menu-l3-li']/a/@href"

        category_urls = self.extract_list(response.xpath(electrical_categories_url_xpath))
        category_urls.extend(self.extract_list(response.xpath(beauty_categories_url_xpath)))

        for category_url in category_urls:
            category_url = get_full_url(response, category_url)
            request = Request(category_url, callback=self.parse_category)
            yield request

    def parse_category(self, response):
        next_page_xpath = "//*[@rel='next']/@href"
        sub_category_xpath = "//div[@id='subCategorycategories']//a/@href"

        sub_cat_urls = self.extract_list(response.xpath(sub_category_xpath))

        if sub_cat_urls:
            for sub_cat_url in sub_cat_urls:
                sub_cat_url = get_full_url(response, sub_cat_url)
                request = Request(sub_cat_url, callback=self.parse_category)
                yield request
        else:
            product_url_xpath = "//div[@class='description']/a/@href"
            product_urls = self.extract_list(response.xpath(product_url_xpath))

            for product_url in product_urls:
                product_url = get_full_url(response, product_url)
                request = Request(product_url, callback=self.parse_product)
                yield request

            next_page_url = self.extract(response.xpath(next_page_xpath))
            if next_page_url:
                next_page_url = get_full_url(response, next_page_url)
                request = Request(next_page_url, callback=self.parse_category)
                yield request

    def parse_product(self, response):
        category_path_xpath = "//span[contains(@class, 'breadcrumb')]/a/text()"

        category = CategoryItem()
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath),
                                                     separator=' | ')
        yield category
        if self.should_skip_category(category):
            return

        product_xpaths = {"ProductName": "//h1/text()",
                          "PicURL": "//meta[@property='og:image']/@content",
                          "ProductManufacturer": "//meta[@property='brand']/@content",
                          "source_internal_id": "//meta[@property='product_number']/@content"
                          }

        product = self.init_item_by_xpaths(response, "product", product_xpaths)

        if not product['source_internal_id']:
            return

        product['OriginalCategoryName'] = category['category_path']
        yield product

        product_id = ProductIdItem()
        product_id['source_internal_id'] = product["source_internal_id"]
        product_id['ProductName'] = product["ProductName"]
        product_id['ID_kind'] = "debenhams_id"
        product_id['ID_value'] = product["source_internal_id"]
        yield product_id

        request = self.start_reviews(response, product, filter_other_sources=False)
        request.meta['product'] = product
        yield request
