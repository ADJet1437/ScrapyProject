# -*- coding: utf8 -*-
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import re


class M3IdgSE(AlaSpider):
    name = 'm3_se'
    allowed_domains = ['m3.idg.se']
    start_urls = [
        'https://m3.idg.se/2.30149/tester---de-senaste-testerna-fran-m3']

    def parse(self, response):
        review_urls_xpath = "//span/a/@href | //ul[@class = 'dateList']"\
            "/li/a/@href"
        review_urls = self.extract_list(response.xpath(review_urls_xpath))

        for review_url in review_urls:
            yield response.follow(review_url,
                                  callback=self.parse_review_product)

    def parse_review_product(self, response):
        product = self.parse_product(response)
        review = self.parse_review(response)

        if product["source_internal_id"]:
            yield product
        if review["source_internal_id"]:
            yield review

    def get_product_name(self, response):
        product_name = response.url
        product_name = product_name.split('/')[-1]
        productname = product_name.replace('-', ' ')
        return productname

    def parse_product(self, response):
        product_xpaths = {
            'PicURL': '//meta[@property="og:image"]/@content',
            'source_internal_id': "substring-after(//div[@id='articlePage-1']"
            "/@data-article-id, '.')",
            "OriginalCategoryName": "//p[@class='articleTeaser']/span/a/text()"
        }

        product = self.init_item_by_xpaths(response, 'product', product_xpaths)
        if not product['OriginalCategoryName']:
            product['OriginalCategoryName'] = self.extract(response.xpath(
                '//a[@class="articleLabel"][last()]//text()'
            ))

        product["ProductName"] = self.get_product_name(response)

        return product

    def parse_review(self, response):
        review_xpaths = {
            'TestTitle': '//meta[@property="og:title"]/@content',
            'Author': '//div[@class="articleAuthor"]/p/a/span/text()',
            'source_internal_id': "substring-after(//div[@id='articlePage-1']"
            "/@data-article-id, '.')",
            'TestSummary': '//meta[@name="description"]/@content',
            'TestPros': '//img[@alt="plus"]/ancestor::figure/'
            'following-sibling::p[1]//text()',
            'TestCons': '//img[@alt="minus"]/ancestor::figure/'
            'following-sibling::p[1]//text()'
        }

        review = self.init_item_by_xpaths(response, 'review', review_xpaths)

        test_date_xpath = '//div[@class="articlePreHeader articleTop"]'\
            '/span[@class="articleDate"]/text()'
        test_date = self.extract(response.xpath(test_date_xpath))
        test_date = test_date.split(' ')[0]
        review['TestDateText'] = test_date

        review["ProductName"] = self.get_product_name(response)

        text = response.text
        rating = re.findall(r'"ratingValue":"(.*?)"', text)
        if rating:
            rating = rating[0]
            review['SourceTestRating'] = rating
            review['SourceTestScale'] = 10

        if not review['Author']:
            author = self.extract(response.xpath(
                '(//div[@class="authorBio"]//h6//text())[1]'))
            review['Author'] = author
        review['DBaseCategoryName'] = 'PRO'
        return review
