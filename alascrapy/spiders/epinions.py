"""epinions Spider: """

__author__ = 'leonardo'

import re

from scrapy.spiders import Rule
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor

from alascrapy.items import ProductItem, ReviewItem
from alascrapy.spiders.base_spiders.ala_crawl import AlaCrawlSpider


class EpinionsSpider(AlaCrawlSpider):
    name = 'epinions'
    allowed_domains = ['epinions.com']
    start_urls = ['http://www.epinions.com/offc-Supplies-All--acco_brands',
                  'http://www.epinions.com/offc-Supplies-All--23991858_acco_brands',
                  'http://www.epinions.com/offc-Supplies-All--smead'
                  ]

    review_list_url_re = re.compile('/review/[^/]+$')
    review_url_re = re.compile('/review/[^/]+/content_\d+$')
    page_url = re.compile('~\d+')

    rules = [Rule(LxmlLinkExtractor(
                  allow=page_url,
                  unique=True,
                  restrict_xpaths='//*[@id="tableFooter"]')),
             Rule(LxmlLinkExtractor(
                  allow=review_list_url_re,
                  unique=True,
                  restrict_xpaths='//*[@class="productReviews"]/a')),
             Rule(LxmlLinkExtractor(
                  allow=review_url_re,
                  unique=True,
                  restrict_xpaths='//*[@class="review_title"]'),
                  callback='parse_review'),
             Rule(LxmlLinkExtractor(
                  allow=review_url_re,
                  unique=True,
                  restrict_xpaths='//*[@class="productReviews"]/a'),
                  callback='parse_review')
            ]

    def parse_review(self, response):
        product_name_xpath = '//*[@itemprop="name"]'
        pic_url_xpath = '//*[@itemprop="image"]'
        breadcrumbs_xpath = '//*[@class="breadcrumb"]//text()'
        category_leaf_xpath = '//*[@class="search_box"]//input[@name="tax_name"]/@value'

        review_summary_xpath = '//*[@itemprop="reviewBody"]/text()'
        review_pros_xpath = '//*[contains(@class,"user_review_summary")]//b[contains(text(),"Pros")]/parent::h3/text()'
        review_cons_xpath = '//*[contains(@class,"user_review_summary")]//b[contains(text(),"Cons")]/parent::h3/text()'
        review_verdict_xpath = '//*[contains(@class,"user_review_summary")]//b[contains(text(),"The Bottom Line")]/parent::h3/text()'
        review_title_xpath = '//*[@id="single_review_area"]//*[@itemprop="name"]'
        review_rating_xpath = '//*[@id="single_review_area"]//meta[@itemprop="ratingValue"]/@content'
        review_author_xpath = '//*[@id="single_review_area"]//a[@rel="author"]/text()'
        review_date_xpath = '//*[@id="single_review_area"]//meta[@itemprop="datePublished"]/@content'

        category_path = self.extract_all(response.xpath(breadcrumbs_xpath))

        product = ProductItem()

        product['TestUrl'] = response.url
        product['OriginalCategoryName'] = category_path

        product["ProductName"] = \
            self.extract(response.xpath(product_name_xpath))

        product["PicURL"] = \
            self.extract(response.xpath(pic_url_xpath))

        review = ReviewItem()
        review["SourceTestScale"] = "5"
        review["DBaseCategoryName"] = "USER"
        review["TestUrl"] = response.url
        review["ProductName"] = product["ProductName"]

        review["SourceTestRating"] = self.extract(response.xpath(review_rating_xpath))
        review["TestDateText"] = self.extract(response.xpath(review_date_xpath))
        review["Author"] = self.extract(response.xpath(review_author_xpath))
        review["TestTitle"] = self.extract(response.xpath(review_title_xpath))

        review["TestPros"] = self.extract_all(response.xpath(review_pros_xpath))
        review["TestCons"] = self.extract_all(response.xpath(review_cons_xpath))
        review["TestVerdict"] = self.extract_all(response.xpath(review_verdict_xpath))
        review["TestSummary"] = self.extract_all(response.xpath(review_summary_xpath))

        yield product
        yield review
