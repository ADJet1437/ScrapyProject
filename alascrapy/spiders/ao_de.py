__author__ = 'leonardo, frank'

from alascrapy.spiders.ao_com import AoComSpider


class AODE(AoComSpider):
    name = 'ao_de'
    allowed_domains = ['ao.de']
    start_urls = ['http://www.ao.de/']

    brand_xpath = '//span[@class="details" and text()="Marke"]/following::span/text()'
    review_url_prefix = 'http://www.ao.de/p/reviews/'
