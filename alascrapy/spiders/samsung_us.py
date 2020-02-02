from scrapy.spiders import Rule
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.http import Request
from scrapy.http import Response
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from alascrapy.spiders.base_spiders.bazaarvoice_spider import BazaarVoiceSpider
from alascrapy.spiders.base_spiders.ala_crawl import AlaCrawlSpider
from alascrapy.lib.selenium_browser import SeleniumBrowser, uses_selenium
from alascrapy.items import ProductItem, CategoryItem, ProductIdItem
from alascrapy.lib.generic import get_full_url


class SamsungUsSpider(AlaCrawlSpider, BazaarVoiceSpider):
    name = 'samsung_us'
    start_urls = ['http://www.samsung.com/us/']

    #TODO: Category pages are ajax requested now!
    # here is how the API looks like: 
    # http://www.samsung.com/us/search/api/productfinder/s/_/N-10Z11Zhv1rp?No=0&Nrpp=24&Ns=IsGenericProduct|1||IsCPO|0||N0002101_FeaturedSortOrder|0&Nu=ProdFinderFamilyID
    # Probably easier to 'hardcode' category urls regexes and query the sitemap.xml. This way we land on product page directly...

    #def process_category_link(value):
    #    category_url_re = "(http://www.samsung.com/us/[\w\-]+/([\w\-]+))"
    #    match = re.search(category_url_re, value)
    #    if match:
    #        #if not "accessories" in match.group(2):
    #        if "cell-phones" in match.group(2):
    #            value=match.group(1)+"/all-products"
    #        else:
    #            return None
    #    return value

    rules = [ Rule(LxmlLinkExtractor(
                unique=True,
                restrict_xpaths=['//li[@data-category="Shop"]//li[@class="mid" and @data-category!="Shop Samsung" and @data-category!="Accessories"]/a'],
              ),callback="parse_category"),
              Rule(LxmlLinkExtractor(
                unique=True,
                restrict_xpaths=['//li[@data-category="Shop"]//li[@class="mid" and @data-category="Accessories"]//li/a'],
              ),callback="parse_category_all")
            ]

    def parse_category(self, response):
        all_products_xpath = "//*[@data-link_cat='see all']/@href"
        all_products_url = self.extract(response.xpath(all_products_xpath))
        all_products_url = get_full_url(response, all_products_url)
        if all_products_url:
            request = Request(all_products_url, callback=self.parse_category_all)
            yield request

    def parse_category_all(self, response):
        product_url_xpath='//*[@class="product-title"]/a/@href'
        product_urls = response.xpath(product_url_xpath).extract()
        for product_relative_url in product_urls:
            product_url = get_full_url(response, product_relative_url)
            request = self.selenium_request(url=product_url,
                                            callback=self.parse_product)
            yield request

    @uses_selenium
    def parse_product(self, response):
        review_page_xpath = '//*[@class="reviews"]/a[@class="button alt"]//@href'

        category_xpath = '//*[@data-link_cat="top nav" and @data-link_position="top nav 2"]/text()'
        category_url = '//*[@data-link_cat="top nav" and @data-link_position="top nav 2"]/@href'
        category = CategoryItem()
        category["category_leaf"] = self.extract(response.xpath(category_xpath))
        category["category_path"] = category["category_leaf"]
        category["category_url"] = self.extract(response.xpath(category_url))
        yield category

        product_name_xpath='//*[@class="product-title"]/text()'
        pic_url_xpath = '//meta[@property="og:image"]/@content'
        source_internal_id_xpath='//*[@class="serial"]/text()'

        if self.should_skip_category(category):
            return

        product = ProductItem()
        product["source_internal_id"] = self.extract(response.xpath(source_internal_id_xpath))
        product["ProductName"] = self.extract(response.xpath(product_name_xpath))
        product["OriginalCategoryName"] = category['category_path']
        product["PicURL"] = self.extract(response.xpath(pic_url_xpath))
        product["ProductManufacturer"] = "Samsung"
        product["TestUrl"] = response.url
        yield product

        product_id = ProductIdItem()
        product_id['source_internal_id'] = product["source_internal_id"]
        product_id['ProductName'] = product["ProductName"]
        product_id['ID_kind'] = "MPN"
        product_id['ID_value'] = product["source_internal_id"]
        yield product_id

        review_count_xpath = "//*[@class='lockup-container']//*[@itemprop='reviewCount']"
        review_count = self.extract(response.xpath(review_count_xpath))

        if review_count:
            sort_button_xpath = "//*[@id='BVRRDisplayContentSelectBVFrameID_textfield']"
            newest_option_xpath = "//ul[@class='BVRRStyledSelectList' and not(contains(@style,'display: none;'))]/li[text()='Newest']"
            select_xpath = "//*[@id='BVRRDisplayContentSelectBVFrameID']"
            reviews_url = self.extract(response.xpath(review_page_xpath))
            reviews_url = get_full_url(response, reviews_url)

            ec_condition = EC.element_to_be_clickable((By.ID,'BVRRDisplayContentSelectBVFrameID_textfield'))


            with SeleniumBrowser(self, response) as browser:
                selector = browser.get(reviews_url, timeout=5)
                selector = browser.click(sort_button_xpath, timeout=1)
                selector = browser.click(newest_option_xpath)

                request = Request(reviews_url)
                request.meta['product']=product
                request.meta['product_id']=product_id
                request.meta['browser'] = browser
                request.meta['_been_in_decorator'] = True

                response = Response(str(reviews_url))
                response.request = request

                for review in self.parse_reviews(response, selector=selector):
                    yield review

