# -*- coding: utf8 -*-
__author__ = 'leo'

from alascrapy.spiders.samsung_uk import SamsungUkSpider


class SamsungNoSpider(SamsungUkSpider):
    name = 'samsung_no'
    allowed_domains = ['samsung.com']
    start_urls = ['http://reviews.no.samsung.com/7463-no_no/allreviews.htm']
