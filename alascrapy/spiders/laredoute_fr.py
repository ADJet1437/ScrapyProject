__author__ = 'jim'

from scrapy.http import Request

from alascrapy.items import ProductItem, CategoryItem
from alascrapy.lib.selenium_browser import SeleniumBrowser, uses_selenium
from alascrapy.spiders.base_spiders.bazaarvoice_spiderAPI5_5 import BazaarVoiceSpiderAPI5_5
from alascrapy.lib.generic import get_full_url

#TODO Migrate to apiv5.5
class LaredouteFrSpider(BazaarVoiceSpiderAPI5_5):
    name = 'laredoute_fr'
    allowed_domains = ['laredoute.fr']
    start_urls = ['http://www.laredoute.fr/pplp/100/cat-74779.aspx',
                  'http://www.laredoute.fr/pplp/100/cat-74925.aspx']

    def parse(self, response):
        sub_category_urls = self.extract_list(response.xpath('//li[@data-cerberus]/a[@id]/@href'))
        for sub_category_url in sub_category_urls:
            sub_category_url = get_full_url(response, sub_category_url)
            request = Request(url=sub_category_url, callback=self.parse_sub_category)
            yield request

    def parse_sub_category(self, response):
        category_urls = self.extract_list(response.xpath('//li[@class="level3"]/a/@href'))
        for category_url in category_urls:
            category_url = get_full_url(response, category_url)
            with SeleniumBrowser(self, response) as browser:
                selector = browser.get(category_url+'||reviews*299|reviews*298')
                for item in self.parse_category(browser, selector):
                    yield item

    def parse_category(self, browser, selector):
        products = selector.xpath('//article')

        if products:
            category = CategoryItem()
            category['category_path'] = self.extract_all(selector.xpath('//ol/li//span/text()'), ' > ')
            category['category_leaf'] = self.extract(selector.xpath('//ol/li[last()]//span/text()'))
            category['category_url'] = browser.browser.current_url
            yield category

            if not self.should_skip_category(category):
                for product in products:
                    product_url = self.extract(product.xpath('.//div[@class="content"]/a/@href'))
                    product_url = get_full_url(browser.browser.current_url, product_url)
                    request = self.selenium_request(url=product_url, callback=self.parse_product)
                    request.meta['category'] = category
                    yield request

    @uses_selenium
    def parse_product(self, response):
        category = response.meta['category']

        product = ProductItem()
        product['TestUrl'] = response.url
        product['OriginalCategoryName'] = category['category_path']
        product["ProductManufacturer"] = self.extract(response.xpath('//a[@class="brand"]/text()'))
        product['PicURL'] = self.extract(response.xpath('//meta[@property="og:image"]/@content'))
        product['source_internal_id'] = self.extract(response.xpath('//div[@id="pdpFRdivMain"]/@data-productid'))
        mpn = self.extract(response.xpath(
            '//dt[@data-cerberus="txt_pdp_sizetitle"]/parent::dl/dd[not(contains(text(),"Taille"))]/text()'))
        if mpn:
            product['ProductName'] = product["ProductManufacturer"] + ' ' + mpn
            product_id = self.product_id(product)
            product_id['ID_kind'] = "MPN"
            product_id['ID_value'] = mpn
            yield product_id
        else:
            name = self.extract(response.xpath('//h2[@itemprop="name"]/text()'))
            product['ProductName'] = product["ProductManufacturer"] + ' ' + name
        yield product

        review_url = self.extract(response.xpath('//a[@class="read-reviews"]/@href'))
        review_url = get_full_url(response, review_url)
        with SeleniumBrowser(self, response) as browser:
            selector = browser.get(review_url, timeout=10)

            response.meta['browser'] = browser
            response.meta['product'] = product
            response.meta['_been_in_decorator'] = True

            for review in self.parse_reviews(response, selector, incremental=True):
                yield review
