# -*- coding: utf8 -*-
from alascrapy.spiders.tipa_com import TipaSpider


class TipaComDESpider(TipaSpider):
    name = 'tipa_com_de'
    #  award for 2014 is not available for tipa in german
    start_urls = ['http://www.tipa.com/german/XXVII_tipa_awards_2017.html',
                  'http://www.tipa.com/german/XXVI_tipa_awards_2016.html',
                  'http://www.tipa.com/german/XXV_tipa_awards_2015.html']
