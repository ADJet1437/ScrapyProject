# -*- coding: utf8 -*-
__author__ = 'leo'

from alascrapy.spiders.samsung_uk import SamsungUkSpider


class SamsungInSpider(SamsungUkSpider):
    name = 'samsung_in'
    allowed_domains = ['samsung.com']
    start_urls = ['http://reviews.in.samsung.com/7463-en_in/allreviews.htm']
