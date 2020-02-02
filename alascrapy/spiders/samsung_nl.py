# -*- coding: utf8 -*-
__author__ = 'leo'

from alascrapy.spiders.samsung_uk import SamsungUkSpider


class SamsungNlSpider(SamsungUkSpider):
    name = 'samsung_nl'
    allowed_domains = ['samsung.com']
    start_urls = ['http://reviews.nl.samsung.com/7463-nl_nl/allreviews.htm']
