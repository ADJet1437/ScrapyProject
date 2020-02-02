__author__ = 'leonardo'

from alascrapy.spiders.samsung_uk import SamsungUkSpider

class SamsungChSpider(SamsungUkSpider):
    name = 'samsung_ch'
    allowed_domains = ['samsung.com']
    start_urls = ['http://reviews.ch.samsung.com/7463-de_ch/allreviews.htm']
