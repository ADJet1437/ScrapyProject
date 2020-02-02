
# -*- coding: utf8 -*-

__author__ = 'liu'

from canon_nl import CanonNlSpider

class CanonDeSpider(CanonNlSpider):
    name = 'canon_de'
    sitemap_urls = ['https://www.canon.de/sitemap.xml']
    sitemap_rules = [('/product_finder/', 'parse_product'),
                     ('//www.canon.de/printers/', 'parse_product'),
                     ('//www.canon.de/cameras/', 'parse_product'),
                     ('//www.canon.de/scanners/', 'parse_product'),
                     ]
    # bazzarvoice set up
    bv_base_params = {'passkey': 'tsvlsbctitvzy6hhyik3zno77',
                      'display_code': '18238_1_0-de_de',
                      'content_locale':'de_DE'}


