__author__ = 'leonardo'

from alascrapy.spiders.base_spiders.amazon import AmazonReviewsSpider

class AmazonFrReviewsSpider(AmazonReviewsSpider):
    name = 'amazon_fr_reviews'
    start_url_format = "https://www.amazon.fr/product-reviews/%s/ref=cm_cr_dp_see_all_btm?ie=UTF8&showViewpoints=1&sortBy=recent"
    date_format = 'le %d %B %Y'
    amazon_kind = 'amazon_fr_id'
    language = 'fr'
