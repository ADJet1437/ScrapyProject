# -*- coding: utf8 -*-
__author__ = 'leonardo'

from alascrapy.spiders.base_spiders.amazon import AmazonCSV

class AmazonFRCsv(AmazonCSV):
    name = 'amazon_fr_csv'
    country_code = 'fr'
    asin_kind='amazon_fr_id'
    endpoint="webservices.amazon.fr"
    start_urls = ['http://alatest.com']

    schema = {'asin':0,
              'name': 4,
              'image': [5,7, 6],
              'url': [26, 31],
              'manufacturer': 1,
              'price': [-3, 22],
              'mpn': 19,
              'ean': 9,
              'salesrank': 12,
              'nodes': [{'node': 13,
                         'node_path': 15},
                        {'node': 14,
                         'node_path': 16}],
              'parent_asin': -2}

    def feeds_xpath(self, category):
        feed_path = "//Feed/Filename[%s]/.."
        conditions = """contains(text(), '%s') and
                        contains(text(), '_%s.csv') and
                        contains(text(), '_leguide_')
                     """ % (self.country_code, category)
        return feed_path % conditions