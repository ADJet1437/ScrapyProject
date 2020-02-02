# -*- coding: utf8 -*-
__author__ = 'leonardo'

import StringIO
import os
import re
import datetime
from lxml import etree

from alascrapy.spiders.base_spiders.amazon import AmazonCSV
from alascrapy.lib.dao.amazon import get_feed_categories, update_feed_category

class AmazonDECsv(AmazonCSV):
    name = 'amazon_de_csv'
    country_code = 'de'
    asin_kind='amazon_de_id'
    endpoint="webservices.amazon.de"
    start_urls = ['http://alatest.com']
    part_re = re.compile('_delta_(part\d+)_')

    schema = {'asin':0,
              'parent_asin': 1,
              'name': 6,
              'image': [7, 8, 9],
              'url': [34, 41],
              'manufacturer': 3,
              'price': [30, 37],
              'mpn': 12,
              'ean': 11,
              'salesrank': 19,
              'nodes': [{'node': 20,
                         'node_path': 22},
                        {'node': 21,
                         'node_path': 23}]}


    def feeds_xpath(self, category):
        feed_path = "//Feed/Filename[%s]/.."
        conditions = """contains(text(), 'de_v3') and
                        contains(text(), '_%s') and
                        contains(text(), '.base.csv')
                     """ % (category)
        return feed_path % conditions

    def parse(self, response):
        feed_categories = get_feed_categories(self.mysql_manager,
                                              self.spider_conf['source_id'] )
        available_feeds = self.get_feed_list()
        f = StringIO.StringIO(available_feeds)
        tree = etree.parse(f)
        for category in feed_categories:
            xpath = self.feeds_xpath(category['feed_name'])
            feeds = self.extract_feeds(tree, xpath)
            if not feeds:
                self.logger.warning("""AMAZON WARNING: No
                                       feed found in amazon %s for
                                       category %s""" % (self.country_code,
                                                         category['feed_name']))
            if len(feeds) > 1:
                for feed in feeds:
                    match = re.search(self.part_re, feed['filename'])
                    if match:
                        for item in self.process_feed(category, feed):
                            yield item
                    else:
                        self.logger.warning("""AMAZON WARNING: MultiFeed
                                               without part number in amazon
                                               %s for category %s: %s""" % \
                                                (self.country_code,
                                                category['feed_name'],
                                                str(feeds)))
            else:
                feed = feeds[0]
                for item in self.process_feed(category, feed):
                    yield item
