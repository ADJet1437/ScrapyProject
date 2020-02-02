__author__ = 'leonardo'

from alascrapy.spiders.samsung_uk import SamsungUkSpider

class SamsungCaSpider(SamsungUkSpider):
    name = 'samsung_ca'
    allowed_domains = ['samsung.com']
    start_urls = ['http://reviews.ca.samsung.com/7463-en_ca/allreviews.htm']
