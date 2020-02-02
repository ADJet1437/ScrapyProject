# -*- coding: utf8 -*-
__author__ = 'leo'

from alascrapy.spiders.samsung_uk import SamsungUkSpider


class SamsungNZSpider(SamsungUkSpider):
    name = 'samsung_nz'
    allowed_domains = ['samsung.com']
    start_urls = ['http://reviews.nz.samsung.com/9810-en_nz/allreviews.htm']
