__author__ = 'leonardo'

from alascrapy.spiders.sennheiser_us import SennheiserUsSpider


class SennheiserDeSpider(SennheiserUsSpider):
    name = 'sennheiser_uk'
    start_urls = ['http://en-uk.sennheiser.com/headphones',
                  'http://en-uk.sennheiser.com/headsets']
