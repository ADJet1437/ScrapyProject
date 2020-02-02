#!/usr/bin/env python

import re

from scrapy.http import Request

from string import letters, punctuation
from alascrapy.items import CategoryItem, ProductItem, ProductIdItem, ReviewItem
from alascrapy.spiders.base_spiders.ala_sitemap_spider import AlaSitemapSpider

import alascrapy.lib.extruct_helper as extruct_helper

class TweakersReviewsSpider(AlaSitemapSpider):
    name = 'tweakers_reviews'
    sitemap_urls = ['https://tweakers.net/sitemap_index.xml']
    sitemap_follow = ['pricewatch']
    sitemap_rules = [('pricewatch', 'parse_product')]
    download_delay = 2.2

    # We do not need the method to get product urls of different categories
    # as we are now using sitemap
    '''
    def parse(self, response):
        product_url_xpath = "//tr[@class='largethumb']//p[contains(@class, 'ellipsis')]//a[@title]/@href"
        product_urls = self.extract_list(response.xpath(product_url_xpath))

        if not product_urls:
            request = self._retry(response.request)
            yield request
            return

        for product_url in product_urls:
            product_url = get_full_url(response, product_url)
            request = Request(product_url, callback=self.parse_product)
            yield request

        next_page_xpath = "//a[@class='next']/@href"
        next_page = self.extract(response.xpath(next_page_xpath))
        if next_page:
            request = Request(next_page, callback=self.parse)
            yield request
    '''

    def parse_product(self, response):
        product = ProductItem()
        product_name_xpath = "//*[@itemprop='name']/a/text()"
        pic_url_xpath = "//div[@class='imageCarousel']//img/@src"
        manufacturer_xpath = "//td[@class='spec-index-column'][text()='Merk']/following-sibling::td//text()"
        sii_xpath = "//td[@class='spec-index-column'][text()='Tweakers ID']/following-sibling::td//text()"
        product['TestUrl'] = response.url
        product['ProductName'] = self.extract(response.xpath(product_name_xpath))
        if not product['ProductName']: #blocked
            request = self._retry(response.request)
            yield request
            return

        category_path_xpath = "//li[@id='tweakbaseBreadcrumbCategory']/a/text()"
        category_path = self.extract(response.xpath(category_path_xpath))
        if category_path:
            category = CategoryItem()
            category['category_path'] = category_path
            product['OriginalCategoryName'] = category_path

            if self.should_skip_category(category):
                return

            yield category

        product['PicURL'] = self.extract(response.xpath(pic_url_xpath))
        product['ProductManufacturer'] = self.extract(response.xpath(manufacturer_xpath))
        product['source_internal_id'] = self.extract(response.xpath(sii_xpath))
        yield product

        tweakers_kind = ProductIdItem()
        tweakers_kind['source_internal_id'] = product['source_internal_id']
        tweakers_kind['ProductName'] = product["ProductName"]
        tweakers_kind['ID_kind'] = "tweakers_id"
        tweakers_kind['ID_value'] = product["source_internal_id"]
        yield tweakers_kind

        eans_xpath = "//td[@class='spec-index-column'][text()='EAN']/following-sibling::td/span/text()"
        eans = self.extract_list(response.xpath(eans_xpath))
        for ean in eans:
            tweakers_kind = ProductIdItem()
            tweakers_kind['source_internal_id'] = product["source_internal_id"]
            tweakers_kind['ProductName'] = product["ProductName"]
            tweakers_kind['ID_kind'] = "EAN"
            try:
                tweakers_kind['ID_value'] = int(ean)
                yield tweakers_kind
            except ValueError, e:
                continue

        skus_xpath = "//td[@class='spec-index-column'][text()='SKU']/following-sibling::td/span/text()"
        skus = self.extract_list(response.xpath(skus_xpath))
        for sku in skus:
            tweakers_kind = ProductIdItem()
            tweakers_kind['source_internal_id'] = product["source_internal_id"]
            tweakers_kind['ProductName'] = product["ProductName"]
            tweakers_kind['ID_kind'] = "SKU"
            tweakers_kind['ID_value'] = sku
            yield tweakers_kind

        review_link_xpath = "//li[@id='tab_select_reviews']/a/@href"
        review_link = self.extract(response.xpath(review_link_xpath))
        if review_link:
            # TODO: add parameters to the link so reviews are sort by date
            request = Request(review_link, callback=self.parse_review, headers={'Referer': None})
            request.meta['product'] = product
            yield request

# "//div/div[@class='authorContainer']/div[@class='reactieHeader']/a[@class='username']//text()"
    def parse_review(self, response):

        product = response.meta['product']

        expert_review_xpath = "//div[@id='tab:reviews']/div/div[@itemscope]"
        expert_url_xpath = ".//div[@class='bottomline']/h3/a/@href"
        expert_title_xpath = ".//div[@class='bottomline']/h3/a/text()"
        expert_summary_xpath = ".//div[@class='bottomline']/p/text()"
        expert_pros_xpath = ".//ul[@class='positivePointsList']//li//text()"
        expert_cons_xpath = ".//ul[@class='negativePointList']//li//text()"

        expert_review = response.xpath(expert_review_xpath)
        if expert_review:
            url = self.extract(expert_review.xpath(expert_url_xpath))
            title = self.extract(expert_review.xpath(expert_title_xpath))
            summary = self.extract(expert_review.xpath(expert_summary_xpath))
            pros = self.extract_all(expert_review.xpath(expert_pros_xpath), " ; ")
            cons = self.extract_all(expert_review.xpath(expert_cons_xpath), " ; ")

            micordata_items = extruct_helper.get_microdata_extruct_items(response.text)
            expert_reviews = list(extruct_helper.get_reviews_microdata_extruct(micordata_items, product, 'PRO',
                                                                               url=url, pros=pros, cons=cons)
                                  )

            if len(expert_review) == 1:
                pro_review = expert_reviews[0]
                pro_review["SourceTestScale"] = "5"
                if not pro_review.get('TestSummary'):
                    pro_review['TestSummary'] = summary
                if not pro_review.get('TestTitle'):
                    pro_review['TestTitle'] = title
                yield pro_review
            elif len(expert_review) >= 1:
                self.logger.error('More than 1 expert reviews found for product {0}'.format(response.url))

        testSummary_xpath = ".//div[@class='bottomline']/p/text()"
        author_xpath = ".//a[@class='username']/text()"
        testDateText_xpath = ".//span[@class='date']/text()"
        testPros_xpath = ".//ul[@class='positivePointsList']//li/text()"
        testCons_xpath = ".//ul[@class='negativePointList']//li/text()"
        sourceTestRating_xpath = ".//div[@class='scoreEmblem']/span/text()"

        divs = response.xpath("//div[@id='tab:reviews']/div/div")
        for div in divs.xpath("./div[not(@*)]"):
            review = ReviewItem()
            review["TestUrl"] = response.url
            review["DBaseCategoryName"] = "USER"
            review["SourceTestScale"] = "5"
            review["ProductName"] = product["ProductName"]
            review["TestTitle"] = product["ProductName"]
            review["TestSummary"] = self.extract(div.xpath(testSummary_xpath))
            review["TestPros"] = self.extract_all(div.xpath(testPros_xpath), " ; ")
            review["TestCons"] = self.extract_all(div.xpath(testCons_xpath), " ; ")
            review["Author"] = self.extract(div.xpath(author_xpath))
            review["TestDateText"] = self.extract(div.xpath(testDateText_xpath))

            review["SourceTestRating"] = self.extract(div.xpath(sourceTestRating_xpath))
            if review["SourceTestRating"] != '' :
                review["SourceTestRating"] = self.clear_score(review["SourceTestRating"])

            if review["Author"] != '':
                yield review

        next_page_xpath = "//a[@class='next']/@href"
        next_page = self.extract(response.xpath(next_page_xpath))
        if next_page:
            request = Request(next_page, callback=self.parse_review)
            request.meta['product'] = product
            yield request

    def clear_score(self, score):
        score = score.strip(letters)
        score = score.strip(punctuation)
        return score
