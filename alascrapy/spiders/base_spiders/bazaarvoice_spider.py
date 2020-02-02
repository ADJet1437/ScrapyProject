import re
import js2xml
from datetime import datetime
from scrapy.http import Request
from scrapy.selector import Selector
from alascrapy.items import ReviewItem, CategoryItem, ProductItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, remove_querystring, set_query_parameter
import alascrapy.lib.dao.incremental_scraping as incremental_utils


class BazaarVoiceSpider(AlaSpider):

    FORMAT_URL = "http://{bv_subdomain}/{bv_site_locale}/{source_internal_id}/reviews.djs?format=embeddedhtml&sort=submissionTime"

    headers = {'Referer': '*/*',
               'Accept-Encoding': 'gzip, deflate, sdch',
               'Accept-Language': 'en-US,en;q=0.8',
               'Cache-Control': 'no-cache',
               'Connection': 'keep-alive',
               'Pragma': 'no-cache'}

    def start_reviews(self, site_response, product, filter_other_sources=True,
                      sort=None, dir=None, extra_review_parser=None):
        self.headers['Host'] = self.bv_subdomain
        self.headers['Referer'] = site_response.url

        url_params = {'bv_subdomain': self.bv_subdomain,
                      'bv_site_locale': self.bv_site_locale,
                      'source_internal_id': product['source_internal_id']}
        
        review_url = self.FORMAT_URL.format(**url_params)
        if sort:
            review_url = set_query_parameter(review_url, 'sort', sort)
        if sort and dir:
            review_url = set_query_parameter(review_url, 'dir', dir)
        request = Request(review_url, callback=self.parse_reviews, headers=self.headers)
        request.meta['product'] = product
        request.meta['filter_other_sources'] = filter_other_sources
        request.meta['extra_review_parser'] = extra_review_parser
        return request        

    def parse_reviews(self, response):
        jstree = js2xml.parse(response.body)
        xml = js2xml.pretty_print(jstree)
        html_xpath = "//var[@name='materials']/object/property[@name='BVRRSourceID']/string/text()"
        html = jstree.xpath(html_xpath)
        if html:
            selector = Selector(text=html[0])

        next_page_xpath = '(//*[contains(@class,"BVRRNextPage")])[1]/a/@data-bvjsref'
        review_list_xpath = '//*[contains(@class,"BVRRContentReview")]'
        from_product_url_xpath = ".//div[contains(@class, 'BVDI_SUAttribution')]//a[@class='BVDILink']/@href"
        from_another_source_xpath =".//*[contains(@class,'BVRRSyndicatedContentAttribution')]"

        filter_other_sources = response.meta.get('filter_other_sources', None)
        extra_review_parser = response.meta.get('extra_review_parser', None)
        last_user_review = response.meta.get('last_user_review', None)

        product = response.meta['product']
        if not product["source_internal_id"]:
            raise Exception("BV Product without source_internal_id")
        if not last_user_review:
            last_user_review = incremental_utils.get_latest_user_review_date_by_sii(
                self.mysql_manager, self.source_id, product["source_internal_id"])

        review_list = selector.xpath(review_list_xpath)
        if not review_list:
            return

        for review_selector in review_list:
            skip_review = False
            if filter_other_sources:
                skip_review = review_selector.xpath(from_another_source_xpath)

            from_product_url = self.extract_xpath(review_selector, from_product_url_xpath)
            from_product = True
            if from_product_url:
                from_product = (product["source_internal_id"].lower() in from_product_url.lower())

            review = self._parse_review(product, review_selector, extra_review_parser)

            if last_user_review:
                current_user_review = datetime.strptime(review['TestDateText'], '%Y-%m-%d')
                if last_user_review > current_user_review:
                    return

            if from_product and not skip_review:
                yield review

        next_page_url = self.extract_xpath(selector, next_page_xpath)
        if next_page_url:
            headers = response.request.headers
            request = Request(next_page_url, callback=self.parse_reviews, headers=headers)
            request.meta['product'] = product
            request.meta['last_user_review'] = last_user_review
            request.meta['filter_other_sources'] = filter_other_sources
            request.meta['extra_review_parser'] = extra_review_parser
            yield request


    """
        Parses a review given the selector where it is contained. 
        The product item must be gives as an argument,
        because the baazarvoice template does not include product name.
    """
    def _parse_review(self, product, review_selector, extra_review_parser=None):

        review = ReviewItem()
        date_xpath = './/meta[@itemprop="datePublished"]/@content'
        alt_date_xpath = './/*[contains(@class,"BVRRReviewDate")]/span[@class="value-title"]/@title'
        author_xpath = './/*[contains(@class,"BVRRNickname")]/text()|.//meta[@itemprop="author"]/@content'
        rating_xpath = './/*[contains(@class,"BVRRRatingOverall")]//*[contains(@class,"BVRRRatingNumber")]/text()'
        scale_xpath = './/*[contains(@class,"BVRRRatingOverall")]//*[contains(@class,"BVRRRatingRangeNumber")]//text()'
        pros_xpath = './/*[contains(@class,"BVRRReviewProTags") and contains(@class,"BVRRValue")]//text()'
        alt_pros_xpath = './/*[contains(@class,"BVRRTagsPrefix") and contains(text(),"Pro")]/following-sibling::*[contains(@class, "BVRRTags")][1]//text()'
        cons_xpath = './/*[contains(@class,"BVRRReviewConTags") and contains(@class,"BVRRValue")]//text()'
        alt_cons_xpath = './/*[contains(@class,"BVRRTagsPrefix") and contains(text(),"Cons")]/following-sibling::*[contains(@class, "BVRRTags")][1]//text()'
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
        if review['SourceTestRating']:
            review['SourceTestScale'] = self.extract(review_selector.xpath(scale_xpath))
        review['TestPros'] = self.extract_all(review_selector.xpath(pros_xpath))
        if not review['TestPros']:
            review['TestPros'] = self.extract_all(review_selector.xpath(alt_pros_xpath))
        review['TestCons'] = self.extract_all(review_selector.xpath(cons_xpath))
        if not review['TestCons']:
            review['TestCons'] = self.extract_all(review_selector.xpath(alt_cons_xpath))
        review['TestSummary'] = self.extract_all(review_selector.xpath(summary_xpath))
        review['TestTitle'] = self.extract_all(review_selector.xpath(title_xpath))

        if extra_review_parser:
            try:
                altered_review = extra_review_parser(review_selector, review)
                return altered_review
            except:
                pass

        return review


class BVNoSeleniumSpider(BazaarVoiceSpider):

    parse_BV_product = False
    default_kind = None
    source_internal_id_re = re.compile('https?://[^/]+/[^/]+/([^/]+)/.*')

    def parse(self, response):
        category_level = response.meta.get('category_level', 0)
        sub_categories_xpath = '//div[contains(@class,"BVRRSCategoryHierarchyItemLabel%s")]/a/@href' % category_level
        sub_categories = self.extract_list(response.xpath(sub_categories_xpath))
        if sub_categories:
            for sub_category in sub_categories:
                request = Request(url=sub_category, callback=self.parse)
                request.meta['category_level'] = category_level+1
                yield request
        else:
            category = response.meta.get('category', None)
            if not category:
                category = CategoryItem()
                category_path_xpath = '//div[@class="BVRRSCategoryBreadcrumbNav"]//text()'
                category_level_xpath = '//div[@class="BVRRSCategoryBreadcrumbNav"]/span/text()'
                category['category_path'] = self.extract_all(response.xpath(category_path_xpath))
                category['category_leaf'] = self.extract(response.xpath(category_level_xpath))
                category['category_url'] = response.url
                yield category

            if not self.should_skip_category(category):
                product_xpath = "//div[@class='BVRRSProductsInfo']//div[contains(@id, 'BVRRSExternalProductData')]"
                product_url_xpath = './/a[@class="BVRRSBriefProductAndReviewDetailsLink"]/@href'
                review_url_xpath = ".//a[contains(@href,'/reviews.htm')]/@href"
                products = response.xpath(product_xpath)
                for product in products:
                    review_url = self.extract(product.xpath(review_url_xpath))
                    product_url = self.extract(product.xpath(product_url_xpath))
                    if self.parse_BV_product:
                        request = Request(url=review_url,
                                          callback=self.parse_reviews)
                        request.meta['category'] = category
                        request.meta['product_url'] = product_url
                    else:
                        product_url = remove_querystring(product_url)
                        request = Request(url=product_url,
                                          callback=self.parse_product)
                        request.meta['category'] = category
                        request.meta['review_url'] = review_url
                    yield request

                next_page = self.extract(response.xpath('//a[contains(@title,"Next")]/@href'))
                if next_page:
                    request = Request(url=next_page, callback=self.parse)
                    request.meta['category'] = category
                    request.meta['category_level'] = category_level
                    yield request

    def _parse_product(self, response, brand=None):
        category = response.meta['category']
        product_url = response.meta['product_url']
        product_name_xpath = "//*[@id='BVRRSExternalSubjectTitleProductNameID']/text()"
        brand_xpath = "//*[@id='BVRRSExternalSubjectTitleBrandID']/text()"
        pic_url_xpath = "//*[@id='BVExternalSubjectImageID']//img/@src"
        product = ProductItem()
        product['OriginalCategoryName'] = category['category_path']
        product['TestUrl'] = product_url
        match = re.search(self.source_internal_id_re, response.url)
        if match:
            product['source_internal_id'] = match.group(1)
        product['ProductName'] = self.extract(response.xpath(product_name_xpath))
        if brand:
            product['ProductManufacturer'] = brand
        else:
            product['ProductManufacturer'] = self.extract(response.xpath(brand_xpath))
        product['PicURL'] = self.extract(response.xpath(pic_url_xpath))
        return product

    def parse_reviews(self, response):
        product = response.meta.get('product', None)
        product_id = response.meta.get('product_id', None)
        brand = response.meta.get('brand', None)
        request_parse_product = response.meta.get('parse_product', None)
        parse_product = self.parse_BV_product

        if request_parse_product is not None:
            parse_product = request_parse_product

        if parse_product and not self.default_kind:
            raise Exception("Parsing product from template but kind not defined")

        if not product and parse_product:
            product = self._parse_product(response, brand=brand)
            product_id = self.product_id(product)
            product_id["ID_kind"] = self.default_kind
            product_id['ID_value'] = product['source_internal_id']
            response.meta['product'] = product
            yield product
            yield product_id

        next_page_xpath = '(//*[contains(@class,"BVRRNextPage")])[1]/a/@href'
        last_user_review = response.meta.get('last_user_review', None)
        incremental = response.meta.get('incremental', True)
        if not last_user_review:
            if product_id:
                last_user_review = incremental_utils.get_latest_user_review_date(
                    self.mysql_manager, self.spider_conf['source_id'],
                    product_id["ID_kind"], product_id['ID_value'])

        review_list_xpath = '//*[contains(@class,"BVRRContentReview")]'
        from_another_product_xpath = ".//*[contains(@class,'BVDI_SU BVDI_SUAttribution')]"
        from_another_source_xpath = ".//*[contains(@class, 'BVRRSyndicatedContentAttribution')]"

        review_list = response.xpath(review_list_xpath)
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

            next_page_url = self.extract(response.xpath(next_page_xpath))
            next_page_url = get_full_url(response.url, next_page_url)
            if next_page_url:
                request = Request(url=next_page_url,
                                  callback=self.parse_reviews)
                request.meta['last_user_review'] = last_user_review
                request.meta['product'] = product
                request.meta['product_id'] = product_id
                yield request