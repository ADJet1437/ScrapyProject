# -*- coding: utf8 -*-
__author__ = 'leo'

from alascrapy.spiders.samsung_uk import SamsungUkSpider


class SamsungSeSpider(SamsungUkSpider):
    name = 'samsung_se'
    allowed_domains = ['samsung.com']
    start_urls = ['http://reviews.se.samsung.com/7463-sv_se/allreviews.htm']
