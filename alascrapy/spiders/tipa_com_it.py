# -*- coding: utf8 -*-
from alascrapy.spiders.tipa_com import TipaSpider


class TipaComITSpider(TipaSpider):
    name = 'tipa_com_it'
    # Other award years are not available for tipa in italian
    start_urls = ['http://www.tipa.com/italian/XXVII_tipa_awards_2017.html'
                  ]
