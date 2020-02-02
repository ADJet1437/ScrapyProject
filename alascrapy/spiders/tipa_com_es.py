# -*- coding: utf8 -*-
from alascrapy.spiders.tipa_com import TipaSpider


class TipaComESSpider(TipaSpider):
    name = 'tipa_com_es'
    start_urls = ['http://www.tipa.com/spanish/XXVII_tipa_awards_2017.html',
                  'http://www.tipa.com/spanish/XXVI_tipa_awards_2016.html',
                  'http://www.tipa.com/spanish/XXV_tipa_awards_2015.html',
                  'http://www.tipa.com/spanish/XXIV_tipa_awards_2014.html']
