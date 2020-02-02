__author__ = 'leonardo'
import dateparser
import re
from alascrapy.spiders.base_spiders.amazon import AmazonReviewsSpider
from alascrapy.lib.generic import  get_full_url, date_format
from scrapy.http import Request

class AmazonItReviewsSpider(AmazonReviewsSpider):
    name = 'amazon_it_reviews'
    start_url_format = "http://www.amazon.it/product-reviews/%s/ref=cm_cr_dp_see_all_btm?ie=UTF8&showViewpoints=1&sortBy=recent"
    date_format = '%d %B %Y'
    amazon_kind = 'amazon_it_id'
    language = 'it'

    def _format_date(self, raw_review, date_xpath):
        date = self.extract_xpath(raw_review, date_xpath)
        date = date.replace("il ","",1)
        date = date_format(date, self.date_format, languages=[self.language])
        return date