# -*- coding: utf8 -*-
__author__ = 'leo'

from alascrapy.spiders.samsung_uk import SamsungUkSpider


class SamsungFrSpider(SamsungUkSpider):
    name = 'samsung_fr'
    allowed_domains = ['samsung.com']
    start_urls = ['http://reviews.fr.samsung.com/7463-fr_fr/allreviews.htm']
