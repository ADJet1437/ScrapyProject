# -*- coding: utf8 -*-
from alascrapy.spiders.tipa_com import TipaSpider


class TipaComFRSpider(TipaSpider):
    name = 'tipa_com_fr'
    start_urls = ['http://www.tipa.com/french/XXVII_tipa_awards_2017.html',
                  'http://www.tipa.com/french/XXVI_tipa_awards_2016.html',
                  'http://www.tipa.com/french/XXV_tipa_awards_2015.html',
                  'http://www.tipa.com/french/XXIV_tipa_awards_2014.html']
