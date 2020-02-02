__author__ = 'leonardo'

from alascrapy.spiders.base_spiders.amazon import AmazonReviewsSpider
from alascrapy.lib.generic import date_format

class AmazonComReviewsSpider(AmazonReviewsSpider):
    name = 'amazon_com_reviews'
    start_url_format = "https://www.amazon.com/product-reviews/%s/ref=cm_cr_dp_see_all_btm?ie=UTF8&showViewpoints=1&reviewerType=all_reviews&sortBy=recent"
    amazon_kind = 'amazon_com_id'
    date_format = 'on %B %d, %Y'
    language = 'en'
