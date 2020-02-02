from datetime import datetime
from scrapy import Selector
from scrapy.http import Request

from alascrapy.lib.generic import get_full_url
from alascrapy.items import CategoryItem, ProductIdItem, ReviewItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import js2xml
import alascrapy.lib.dao.incremental_scraping as incremental_utils

class PanasonicComSpider(AlaSpider):
    name = 'panasonic_com'
    start_urls = ['http://shop.panasonic.com/']

    def parse(self, response):
        subcategories_xpath = "//ul[@class='level-2']/li/a/@href"
        category_urls = self.extract_list(
            response.xpath(subcategories_xpath))

        for category_url in category_urls:
            request = Request(category_url, callback=self.parse_category)
            yield request


    def parse_category(self, response):
        products_xpath = "//*[@class='product-tile-cont']"
        product_url_xpath = ".//a[@class='name-link']/@href"
        product_rating_xpath = ".//*[@class='reviews_stock_cont']\
            /*[@class='BVInlineRatings']"
        next_page_xpath = "((//*[@class='results-count'])[1]\
            /ul/li[@class='current-page']\
            /following-sibling::li/a)[1]/@href"

        home_category_xpath = "//div[@class='breadcrumb']//*[@class='breadcrumb-home']/text()"
        category_leaf_xpath = "//div[@class='breadcrumb']//*[@class='breadcrumb-last']/text()"
        category_path_xpath = "//div[@class='breadcrumb']//*[@class='breadcrumb-span-h']/a/text()"


        if 'category' in response.meta:
            category = response.meta['category']
        else:
            category = CategoryItem()
            category['category_url'] = response.url
            category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))

            home_category = self.extract(response.xpath(home_category_xpath))
            middle_path = self.extract_all(response.xpath(category_path_xpath), ' | ')
            category['category_path'] = "%s | %s | %s" % \
                (home_category, middle_path, category['category_leaf'])

            if self.should_skip_category(category):
                return
            yield category

        products = response.xpath(products_xpath)

        for product in products:
            has_reviews = self.extract(
                product.xpath(product_rating_xpath))

            if has_reviews:
                product_url = self.extract(product.xpath(product_url_xpath))
                request = Request(product_url, callback=self.parse_product)
                request.meta['category'] = category
                yield request

        next_page = self.extract(response.xpath(next_page_xpath))
        if next_page:
            request = Request(next_page, callback=self.parse_category)
            request.meta['category'] = category
            yield request

    def parse_product(self, response):
        category = response.meta['category']
        product_xpaths = \
            { "ProductName": "//*[contains(@class,'pdp-prod-name')]//text()",
              "PicURL": "//img[@class='primary-image']/@src",
              "source_internal_id": "//*[@itemprop='productID']/text()"
            }
        picurl_alt_xpath = "//img[@class='primary-image']/@data-src"
        product = self.init_item_by_xpaths(response, "product", product_xpaths)

        product['OriginalCategoryName'] = category['category_path']
        product["ProductManufacturer"] = "Panasonic"
        product["TestUrl"] = response.url
        if not product["PicURL"]:
            product["PicURL"] = self.extract(response.xpath(picurl_alt_xpath))

        yield product

        product_id = ProductIdItem()
        product_id['source_internal_id'] = product["source_internal_id"]
        product_id['ProductName'] = product["ProductName"]
        product_id['ID_kind'] = "MPN"
        product_id['ID_value'] = product["source_internal_id"]
        yield product_id

        response.meta['product'] = product
        response.meta['product_id'] = product_id

        last_user_review = incremental_utils.get_latest_user_review_date(
            self.mysql_manager, self.spider_conf['source_id'],
            product_id["ID_kind"], product_id['ID_value'])

        response.meta['last_user_review'] = last_user_review
        response.meta['incremental'] = True

        yield Request('http://panasonic.reviews.bazaarvoice.com/9203-en_us/{0}/reviews.djs?format=embeddedhtml&page=1&sort=submissionTime'.format(
            product["source_internal_id"]
        ), callback=self.parse_reviews, meta=response.meta)

    """
        Callback to parse a review given the selector where it is contained.
        The response must have the product item as a meta argument,
        because the baazarvoice template does not include product name. 
    """

    def parse_review(self, response, review_selector):
        product = response.meta['product']

        review = ReviewItem()
        date_xpath = './/meta[@itemprop="datePublished"]/@content'
        alt_date_xpath = './/*[contains(@class,"BVRRReviewDate")]/span[@class="value-title"]/@title'
        author_xpath = './/*[contains(@class,"BVRRNickname")]/text()|.//meta[@itemprop="author"]/@content'
        rating_xpath = './/*[contains(@class,"BVRRRatingNumber")]//text()'
        scale_xpath = './/*[contains(@class,"BVRRRatingRangeNumber")]//text()'
        pros_xpath = './/*[contains(@class,"BVRRReviewProTags") and contains(@class,"BVRRValue")]//text()'
        alt_pros_xpath = '(.//*[contains(@class,"BVRRTagsPrefix") and ' \
                         'contains(text(),"Pro")]/following-sibling::*[contains(@class,"BVRRTags")])[1]//text()'
        cons_xpath = './/*[contains(@class,"BVRRReviewConTags") and contains(@class,"BVRRValue")]//text()'
        alt_cons_xpath = '(.//*[contains(@class,"BVRRTagsPrefix") and ' \
                         'contains(text(),"Cons")]/following-sibling::*[contains(@class,"BVRRTags")])[1]//text()'
        summary_xpath = './/*[contains(@class,"BVRRReviewText")]//text()'
        title_xpath = './/*[contains(@class,"BVRRReviewTitle")]/text()'

        review['DBaseCategoryName'] = 'USER'
        if 'source_internal_id' in product:
            review['source_internal_id'] = product['source_internal_id']
        review['ProductName'] = product['ProductName']
        review['TestUrl'] = product['TestUrl']
        review['TestDateText'] = self.extract(review_selector.xpath(date_xpath))
        if not review['TestDateText']:
            review['TestDateText'] = self.extract(review_selector.xpath(alt_date_xpath))
        review['Author'] = self.extract(review_selector.xpath(author_xpath))
        review['SourceTestRating'] = self.extract(review_selector.xpath(rating_xpath))
        review['SourceTestScale'] = self.extract(review_selector.xpath(scale_xpath))
        review['TestPros'] = self.extract_all(review_selector.xpath(pros_xpath))
        if not review['TestPros']:
            review['TestPros'] = self.extract_all(review_selector.xpath(alt_pros_xpath))
        review['TestCons'] = self.extract_all(review_selector.xpath(cons_xpath))
        if not review['TestCons']:
            review['TestCons'] = self.extract_all(review_selector.xpath(alt_cons_xpath))
        review['TestSummary'] = self.extract_all(review_selector.xpath(summary_xpath))
        review['TestTitle'] = self.extract_all(review_selector.xpath(title_xpath))
        return review

    def parse_reviews(self, response):
        treeBVRRSourceID = js2xml.parse(response.body).xpath('//property[@name="BVRRSourceID"]/string/text()')[0]
        innerHtmlSelector = Selector(text=treeBVRRSourceID)

        next_page_xpath = '(//*[contains(@class,"BVRRNextPage")])[1]/a/@data-bvjsref'
        last_user_review = response.meta.get('last_user_review', None)
        incremental = response.meta.get('incremental', True)

        review_list_xpath = '//*[contains(@class,"BVRRContentReview")]'
        from_another_product_xpath = ".//*[contains(@class,'BVDI_SU BVDI_SUAttribution')]"
        from_another_source_xpath = ".//*[contains(@class, 'BVRRSyndicatedContentAttribution')]"

        review_list = innerHtmlSelector.xpath(review_list_xpath)
        for idx, review_selector in enumerate(review_list):
            from_another_source = review_selector.xpath(from_another_source_xpath)
            from_another_product = review_selector.xpath(from_another_product_xpath)
            review = self.parse_review(response, review_selector)
            if not from_another_product and not from_another_source:
                yield review

            if last_user_review and incremental:
                current_user_review = datetime.strptime(review['TestDateText'], '%Y-%m-%d')
                if current_user_review < last_user_review:
                    return

        next_page_url = self.extract(innerHtmlSelector.xpath(next_page_xpath))
        next_page_url = get_full_url(response.url, next_page_url)
        if next_page_url:
            request = Request(next_page_url, callback=self.parse_reviews)
            request.meta['last_user_review'] = last_user_review
            request.meta['product'] = response.meta['product']
            request.meta['product_id'] = response.meta['product_id']
            yield request