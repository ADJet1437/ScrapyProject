# -*- coding: utf8 -*-
__author__ = 'leonardo'

from alascrapy.spiders.base_spiders.amazon import AmazonCSV

class AmazonITCsv(AmazonCSV):
    name = 'amazon_it_csv'
    country_code = 'it'
    asin_kind = 'amazon_it_id'
    endpoint = "webservices.amazon.it"
    start_urls = ['http://alatest.com']

    schema = {'asin': 0,
              'name': 4,
              'image': [5, 6, 7],
              'url': [23, 28],
              'manufacturer': 1,
              'price': [19, 24],
              'mpn': 17,
              'ean': 9,
              'salesrank': 12,
              'nodes': [{'node': 13,
                         'node_path': 15},
                        {'node': 14,
                         'node_path': 16}]}
