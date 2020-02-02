# -*- coding: utf8 -*-
__author__ = 'leo'

from alascrapy.spiders.samsung_uk import SamsungUkSpider

class SamsungBeSpider(SamsungUkSpider):
    name = 'samsung_be'
    allowed_domains = ['samsung.com']
    start_urls = ['http://reviews.be.samsung.com/7463-nl_be/allreviews.htm']
