__author__ = 'leonardo'

from alascrapy.spiders.base_spiders.amazon import AmazonReviewsSpider

class AmazonDeReviewsSpider(AmazonReviewsSpider):
    name = 'amazon_de_reviews'
    start_url_format = "http://www.amazon.de/product-reviews/%s/ref=cm_cr_dp_see_all_btm?ie=UTF8&showViewpoints=1&sortBy=recent"
    date_format = 'am %d. %B %Y'
    amazon_kind = 'amazon_de_id'
    language = 'de'
