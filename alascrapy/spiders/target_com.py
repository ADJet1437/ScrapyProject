__author__ = 'jim'

import re

from scrapy.http import Request

from alascrapy.items import ProductItem, CategoryItem, ReviewItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format
from alascrapy.lib.selenium_browser import SeleniumBrowser


class TargetComSpider(AlaSpider):
    name = 'target_com'
    allowed_domains = ['target.com']
    start_urls = ['http://www.target.com/c/more/-/N-5xsxf']

    def parse(self, response):
        sub_category_urls = self.extract_list(response.xpath(
                '//ul[@class="innerCol"]/li/a[contains(@href,"/c/")]/@href'))

        for sub_category_url in sub_category_urls:
            request_url = sub_category_url.split('#')
            yield Request(url=get_full_url(response, request_url[0]), callback=self.parse_sub_category)

    def parse_sub_category(self, response):
        category_urls = self.extract_list(response.xpath(
                '//div[@id="leftNavShopLinks"]//ul/li/a[contains(@href,"/c/")]/@href'))

        for category_url in category_urls:
            request_url = category_url.split('#')
            with SeleniumBrowser(self, response) as browser:
                selector = browser.get(get_full_url(response, request_url[0]))
                for item in self.parse_category(browser, selector):
                    yield item

    def parse_category(self, browser, selector):
        path = self.extract_all(selector.xpath('//div[@id="breadCrumb"]/*/text()'))
        products = selector.xpath('//ul[@class="tileRow"]')

        if path and products:
            category = None

            if not category:
                category = CategoryItem()
                category['category_path'] = path
                category['category_leaf'] = self.extract(selector.xpath(
                        '//div[@id="breadCrumb"]/span[@class="curr"]/text()'))
                category['category_url'] = browser.browser.current_url
                yield category

            if not self.should_skip_category(category):
                product_urls = self.extract_list(products.xpath(
                        './li[descendant::a[@title="reviews"]]//a[contains(@name,"prodTitle")]/@href'))
                for product_url in product_urls:
                    product_url = product_url.split('#')
                    request_url = get_full_url(browser.browser.current_url, product_url[0])
                    request_url = request_url.replace('intl.target.com', 'www.target.com')
                    product_selector = browser.get(request_url+'&selectedTab=item-guestreviews-link')
                    for item in self.parse_product(browser, product_selector, category):
                        yield item

    def parse_product(self, browser, selector, category):
        reviews = selector.xpath(
                '//div[contains(@class,"js-reviews--review-list")]'
                '/div[not(descendant::div[@class="reviews--syndicated"])]')
        if reviews:
            product = ProductItem()

            product['TestUrl'] = browser.browser.current_url
            product['OriginalCategoryName'] = category['category_path']
            product['ProductName'] = self.extract(selector.xpath('//span[@itemprop="name"]/text()'))
            product['PicURL'] = self.extract(selector.xpath('//meta[@name="twitter:image:src"]/@content'))
            yield product

            for review in reviews:
                user_review = ReviewItem()
                user_review['DBaseCategoryName'] = "USER"
                user_review['ProductName'] = product['ProductName']
                user_review['TestUrl'] = product['TestUrl']
                date = self.extract(review.xpath('.//@data-timestamp'))
                user_review['TestDateText'] = date_format(date, '')
                rating = self.extract(review.xpath('.//h3/text()'))
                rate_match = re.findall(r'([^<>]+) out of', rating)
                if rate_match:
                    user_review['SourceTestRating'] = rate_match[0]
                user_review['Author'] = self.extract(review.xpath('.//div[@class="reviews--author"]/text()'))
                user_review['TestTitle'] = self.extract(review.xpath(
                        './/div[@class="reviews--primaryPost--title"]/text()'))
                user_review['TestSummary'] = self.extract_all(review.xpath(
                        './/span[contains(@class,"js-reviews--review-text")][not(contains(@class,"hide"))]/text()'))
                yield user_review
