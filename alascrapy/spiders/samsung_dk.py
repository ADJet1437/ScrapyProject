# -*- coding: utf8 -*-
__author__ = 'leo'

from alascrapy.spiders.samsung_uk import SamsungUkSpider

class SamsungDKSpider(SamsungUkSpider):
    name = 'samsung_dk'
    allowed_domains = ['samsung.com']
    start_urls = ['http://reviews.dk.samsung.com/7463-da_dk/allreviews.htm']
