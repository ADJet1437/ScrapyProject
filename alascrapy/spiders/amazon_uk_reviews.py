__author__ = 'leonardo'

from alascrapy.spiders.base_spiders.amazon import AmazonReviewsSpider

class AmazonUkReviewsSpider(AmazonReviewsSpider):
    name = 'amazon_uk_reviews'
    start_url_format = "https://www.amazon.co.uk/product-reviews/%s/ref=cm_cr_dp_see_all_btm?ie=UTF8&showViewpoints=1&sortBy=recent"
    date_format = 'on %d %B %Y'
    amazon_kind = 'amazon_uk_id'
    language = 'en'

