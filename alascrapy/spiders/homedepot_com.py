from datetime import datetime

import js2xml
from scrapy import Selector

__author__ = 'jim'

from scrapy.http import Request

from alascrapy.items import ProductItem, CategoryItem, ProductIdItem, ReviewItem
from alascrapy.lib.generic import get_full_url
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils

class HomedepotComSpider(AlaSpider):
    name = 'homedepot_com'
    start_urls = ['http://www.homedepot.com/c/site_map']

    def parse(self, response):
        categories_xpath = '//div[contains(@class,"transparentBorder")]//ul[contains(@class,"linkList")]' \
                           '//a[contains(@href,"/b/")]/@href'

        categories = self.extract_list(response.xpath(categories_xpath))
        for category in categories:
            if 'http://' not in category:
                category = 'http://'+category
            yield Request(category+'?Ns=P_Top_Rated_Sort|1', callback=self.parse_category)
            
    def parse_category(self, response):
        reviewed_products = self.extract_list(response.xpath('//div[@id="products"]//a[@class="reviews"]/@href'))
        
        if reviewed_products:
            category = None

            if "category" in response.meta:
                category = response.meta['category']

            if not category:
                category = CategoryItem()
                category['category_path'] = self.extract_all(response.xpath('//ul[@id="headerCrumb"]//a/text()'), " ; ")
                category['category_leaf'] = self.extract(response.xpath('//ul[@id="headerCrumb"]/li[last()]/a/text()'))
                category['category_url'] = response.url
                yield category
                
            if not self.should_skip_category(category):
                for product in reviewed_products:
                    product = product.strip('#customer_reviews')
                    request = Request(get_full_url(response, product), callback=self.parse_product)
                    request.meta['category'] = category
                    yield request
                
                next_page = self.extract(response.xpath('//a[@title="Next"]/@href'))
                if next_page:
                    request = Request(get_full_url(response, next_page), callback=self.parse)
                    request.meta['category'] = category
                    yield request

    def parse_product(self, response):
        category = response.meta['category']
        productid = None
        product = ProductItem()
        
        product['TestUrl'] = response.url
        product['OriginalCategoryName'] = category['category_path']
        name = self.extract(response.xpath('//h1[@class="product_title"]/text()'))
        product['PicURL'] = self.extract(response.xpath('//img[@id="mainImage"]/@src'))
        product['source_internal_id'] = self.extract(response.xpath('//span[@id="product_internet_number"]/text()'))
        manu = self.extract(response.xpath('//span[@itemprop="brand"]/text()'))
        mpn = self.extract(response.xpath('//span[@itemprop="model"]/text()'))
        if manu:
            product["ProductManufacturer"] = manu
            name = manu + ' ' + name
            if mpn:
                name = manu + ' ' + mpn
        product['ProductName'] = name
        yield product
        
        if mpn:
            productid = ProductIdItem()
            productid['ProductName'] = product["ProductName"]
            productid['source_internal_id'] = product['source_internal_id']
            productid['ID_kind'] = "MPN"
            productid['ID_value'] = mpn
            yield productid

        response.meta['product'] = product
        if productid:
            response.meta['product_id'] = productid

        last_user_review = incremental_utils.get_latest_user_review_date(
            self.mysql_manager, self.spider_conf['source_id'],
            productid["ID_kind"], productid['ID_value'])

        response.meta['last_user_review'] = last_user_review

        yield Request(
            'http://homedepot.ugc.bazaarvoice.com/1999aa/{0}/reviews.djs?format=embeddedhtml&page=1&sort=submissionTime'.format(
                product["source_internal_id"]
            ), callback=self.parse_reviews, meta=response.meta, errback=self.errback)

    def errback(self, failure):
        self.logger.error(repr(failure))

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
