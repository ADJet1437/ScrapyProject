"""office_depot Spider: """

__author__ = 'leonardo'

from scrapy.spiders import Rule
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from alascrapy.items import ProductItem, CategoryItem, ProductIdItem
from alascrapy.spiders.base_spiders.bazaarvoice_spider import BazaarVoiceSpider
from alascrapy.spiders.base_spiders.ala_crawl import AlaCrawlSpider



class OfficeDepotSpider(AlaCrawlSpider, BazaarVoiceSpider):
    name = 'officedepot'
    download_delay = 5
    start_urls = ['http://www.officedepot.com/a/site-map/']


    rules = [ Rule(LxmlLinkExtractor(
                  unique=True,
                  allow=['/a/browse/'],
                  restrict_xpaths=['//*[@id="siteMap_groups"]//*',
                                   '//*[@class="cat_all_count"]//*',
                                   '//*[@class="next pg_btn"]//*']
                  )),
              Rule(LxmlLinkExtractor(
                  unique=True,
                  allow='/a/products/',
                  restrict_xpaths="""//*[@class="photo flcl"] |
                                     //*[@class="photo_no_QV flcl"]
                                  """),
                  callback="parse_product")
            ]

    def handle_category(self, response, category_xpath):
        base_url = get_base_url(response)

        categories_raw = response.xpath(category_xpath)
        #ocn = self.extract_all(categories_raw[1:].xpath('./text()'), '|')
        category_url = self.extract(categories_raw[-1:].xpath('./@src'))
        # reading the last element in categories_raw
        category_leaf = self.extract(categories_raw[-1:].xpath('./text()'))
        category_url = urljoin_rfc(base_url,category_url)

        category = CategoryItem()
        category['category_leaf'] = category_leaf
        category['category_path'] = category_leaf # ocn2cn does not contain full category path
        category['category_url']=  category_url
        return category

    def parse_product(self, response):
        review_url = 'http://reviews.officedepot.com/2563/%s/reviews.htm'

        category_xpath = '//div[@id="siteBreadcrumb"]//a'
        product_name_xpath = '//*[@itemprop="name"]/text()'
        officedepot_id_xpath = '//*[@id="basicInfoCustomerSku"]/text()'
        brand_xpath = '//*[@id="attributebrand_namekey"]/text()'
        pic_url_xpath = '//*[@id="mainSkuProductImage"]/@src'

        mpn_xpath = '//*[@id="basicInfoManufacturerSku"]/text()'

        category = self.handle_category(response, category_xpath)

        product = ProductItem()
        product['TestUrl'] = response.url
        product['ProductName'] = self.extract(response.xpath(product_name_xpath))
        product['source_internal_id'] = self.extract(response.xpath(officedepot_id_xpath))
        product['ProductManufacturer'] = self.extract(response.xpath(brand_xpath))
        product['PicURL'] = self.extract(response.xpath(pic_url_xpath))
        product['OriginalCategoryName'] = category['category_path']

        officedepot_id = ProductIdItem()
        officedepot_id['source_internal_id'] = product['source_internal_id']
        officedepot_id['ProductName'] =  product['ProductName']
        officedepot_id['ID_kind'] = 'officedepot_id'
        officedepot_id['ID_value'] = product['source_internal_id']

        mpn = ProductIdItem()
        mpn['source_internal_id'] = product['source_internal_id']
        mpn['ProductName'] =  product['ProductName']
        mpn['ID_kind'] = 'MPN'
        mpn['ID_value'] = self.extract(response.xpath(mpn_xpath))

        request = self.selenium_request(url=review_url % product['source_internal_id'],
                                        callback=self.parse_reviews)
        request.meta['product'] = product
        request.meta['product_id'] = officedepot_id
        yield request

        yield category
        yield officedepot_id
        yield mpn
        yield product
