__author__ = 'leonardo'

from alascrapy.spiders.sennheiser_us import SennheiserUsSpider


class SennheiserDeSpider(SennheiserUsSpider):
    name = 'sennheiser_de'
    start_urls = ['http://en-de.sennheiser.com/headphones',
                  'http://en-de.sennheiser.com/headsets']
