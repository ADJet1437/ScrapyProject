# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider


class AlaCrawlSpider(CrawlSpider, AlaSpider):

    def __init__(self, *a, **kw):
        super(AlaCrawlSpider, self).__init__(*a, **kw)

