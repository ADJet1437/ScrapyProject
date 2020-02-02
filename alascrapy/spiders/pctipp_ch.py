import re

from scrapy.http import Request

from alascrapy.items import ProductItem, ProductIdItem, ReviewItem, CategoryItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import date_format
from alascrapy.lib.generic import get_base_url, get_full_url


class PCtippSpider(AlaSpider):
    name = 'pctipp_ch'
    allowed_domains = ['pctipp.ch']

    # Ideally we want to start from category pages. However, many old reviews
    # potentially required by our clients are not categorized
    # TODO: Also scrape through category pages? As not all reviews are available through http://www.pctipp.ch/tests/
    start_urls = ['http://www.pctipp.ch/tests/']

    def parse(self, response):

        review_xpath = "//div[@class='post-content']/h2/a/@href|" \
                       "//ul[contains(@class, 'post-list2')]//li/a/@href"

        next_page_xpath = "//li[@class='next']/a/@href"

        # enable this if we start parsing from category pages
        '''
        # first page
        if 'category' not in response.meta:
            regex_pattern = '.*/([^/]+)(?:/)?$'
            regex_result = re.search(regex_pattern, response.url)
            if not regex_result:
                return

            category = CategoryItem()
            category_name = regex_result.group(1)
            category['category_url'] = response.url
            category['category_leaf'] = category_name
            category['category_path'] = category_name
            yield category

            if self.should_skip_category(category):
                return
        else:
            category = response.meta['category']
        '''

        review_urls = self.extract_list(response.xpath(review_xpath))
        for review_url in review_urls:
            review_url = get_full_url(response, review_url)
            request = Request(review_url, callback=self.parse_review)
            #request.meta['category'] = category
            yield request

        next_page_url = self.extract(response.xpath(next_page_xpath))
        if next_page_url:
            next_page_url = get_full_url(response, next_page_url)
            next_page_request = Request(next_page_url, callback=self.parse)
            #next_page_request.meta['category'] = category
            yield next_page_request

    def parse_review(self, response):

        product_picture_xpath = "//div[@class='article-content']//*[@class='img-holder']/a/@href"
        internal_id_xpath = "//*[@id='article_id']/@value"

        review_title_xpath = "//div[@class='article']/h1/text()"
        author_xpath = "//div[@class='meta']/*[@class='author']/text()"
        date_xpath = "//div[@class='meta']/*[@class='date']/text()"
        summary_xpath = "//div[@class='intro']//text()"

        last_page_xpath = "//div[@class='paging']//li[@class='last']/a/@href"

        end_of_review_xpaths = {"TestVerdict": "//*[text()='Fazit']/following-sibling::p[1]//text()|"
                                               "//*[contains(text(),'Fazit')]/following-sibling::text()[1]|"
                                               "//div[*[@class='product-info']]/text()[1]",
                                "ProductName": "//*[@class='product-info']//*[@*='itemreviewed']/text()",
                                "TestPros": "//*[@class='product-info']//*[@class='positive']/dd/text()",
                                "TestCons": "//*[@class='product-info']//*[@class='negative']/dd/text()",
                                "SourceTestRating": "//*[@class='product-info']//*[@class='stars']/img/@alt"
                                }

        # TODO: disable category parsing in review page if we start collecting reviews from category pages
        category_name_xpath = "//div[@class='breadcrumbs']//li/a/text()"
        category_url_xpath = "//div[@class='breadcrumbs']//li[last()]/a/@href"
        category_name = self.extract_all(response.xpath(category_name_xpath), separator="/")
        if category_name:
            category = CategoryItem()
            extracted_url = self.extract(response.xpath(category_url_xpath))
            category['category_url'] = get_full_url(response, extracted_url)
            category['category_leaf'] = category_name
            category['category_path'] = category_name
            yield category

            if self.should_skip_category(category):
                return
        else:
            self.logger.error('Failed to get category info. Source: {}, url: {}: '.format(self.name, response.url))

        product = ProductItem()
        product_id = ProductIdItem()
        review = ReviewItem()

        product['TestUrl'] = response.url

        # In case we do not find a better product name on last page of the review
        review_title = self.extract(response.xpath(review_title_xpath))
        product['ProductName'] = review_title

        pic_partial_url = self.extract(response.xpath(product_picture_xpath))
        product['PicURL'] = get_full_url(get_base_url(response.url), pic_partial_url)

        product['source_internal_id'] = self.extract(response.xpath(internal_id_xpath))
        #product['OriginalCategoryName'] = response.meta['category']['category_path']
        if category_name:
            product['OriginalCategoryName'] = category_name

        product_id['source_internal_id'] = product['source_internal_id']
        product_id['ProductName'] = product['ProductName']
        product_id['ID_kind'] = 'pctipp_ch_id'
        product_id['ID_value'] = product['source_internal_id']

        yield product_id

        self.set_product(review, product)
        review['TestTitle'] = review_title
        review['DBaseCategoryName'] = "PRO"
        review['SourceTestScale'] = "5"

        review['TestSummary'] = self.extract(response.xpath(summary_xpath))
        extracted_author = self.extract(response.xpath(author_xpath))
        if extracted_author.startswith('von '):
            review["Author"] = extracted_author[4:]
        elif extracted_author != 'von':
            review["Author"] = extracted_author

        extracted_date = self.extract(response.xpath(date_xpath))
        # some of the date texts have (Last updated: <date>) at the end, strip it
        formatted_date = date_format(extracted_date.split(' ')[0], "%d.%m.%Y")
        # This check is for the case the date format is changed
        if not formatted_date:
            formatted_date = date_format(extracted_date, "%d.%m.%Y")
        review['TestDateText'] = formatted_date

        last_page_url = self.extract(response.xpath(last_page_xpath))

        if last_page_url:
            last_page_url = get_full_url(response, last_page_url)

            last_page_request = Request(last_page_url, callback=self.parse_review_last_page)
            last_page_request.meta['product'] = product
            last_page_request.meta['review'] = review
            last_page_request.meta['xpaths'] = end_of_review_xpaths

            yield last_page_request
        else:
            for item in self.parse_end_of_review_xpaths(response, end_of_review_xpaths, product, review):
                yield item

    def parse_review_last_page(self, response):

        product = response.meta['product']
        review = response.meta['review']
        xpaths = response.meta['xpaths']

        for item in self.parse_end_of_review_xpaths(response, xpaths, product, review):
            yield item

    def parse_end_of_review_xpaths(self, selector, xpaths, product, review):
        product_name = self.extract(selector.xpath(xpaths['ProductName']))
        if product_name:
            product['ProductName'] = product_name
            review['ProductName'] = product_name

        review['TestVerdict'] = self.extract(selector.xpath(xpaths['TestVerdict']))
        review['TestPros'] = self.extract(selector.xpath(xpaths['TestPros']))
        review['TestCons'] = self.extract(selector.xpath(xpaths['TestCons']))

        rating_text = self.extract(selector.xpath(xpaths['SourceTestRating']))
        review['SourceTestRating'] = rating_text.split(' ')[0]

        if product_name or review['TestPros'] or review['TestCons'] or review['SourceTestRating'] or review['TestVerdict']:
            yield product
            yield review
