# -*- coding: utf8 -*-
__author__ = 'leo'

from alascrapy.spiders.samsung_uk import SamsungUkSpider


class SamsungPTSpider(SamsungUkSpider):
    name = 'samsung_pt'
    allowed_domains = ['samsung.com']
    start_urls = ['http://reviews.pt.samsung.com/7463-pt_pt/allreviews.htm']
