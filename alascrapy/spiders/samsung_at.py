# -*- coding: utf8 -*-
__author__ = 'leo'

from alascrapy.spiders.samsung_uk import SamsungUkSpider


class SamsungAtSpider(SamsungUkSpider):
    name = 'samsung_at'
    allowed_domains = ['samsung.com']
    start_urls = ['http://reviews.at.samsung.com/7463-de_at/allreviews.htm']
