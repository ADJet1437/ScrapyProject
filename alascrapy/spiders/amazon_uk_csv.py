# -*- coding: utf8 -*-
from alascrapy.spiders.base_spiders.amazon import AmazonCSV

class AmazonUKCsv(AmazonCSV):
    name = 'amazon_uk_csv'
    country_code = 'uk'
    asin_kind='amazon_uk_id'
    start_urls = ['http://alatest.com']
    endpoint="webservices.amazon.co.uk"

    schema = {'asin':0,
              'manufacturer': 1,
              'name': 4,
              'image': [27,26,10],
              'ean': 12,
              'mpn': 20,
              'price': [5, 6],
              'url': [9, 23],
              'salesrank': 15,
              'nodes': [{'node': 16,
                         'node_path': 18},
                        {'node': 17,
                         'node_path': 19}]}