__author__ = 'leonardo'

from alascrapy.spiders.samsung_uk import SamsungUkSpider

class SamsungBrSpider(SamsungUkSpider):
    name = 'samsung_br'
    allowed_domains = ['samsung.com']
    start_urls = ['http://reviews.br.samsung.com/7463-pt_br/allreviews.htm']
