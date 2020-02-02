# -*- coding: utf-8 -*-
from scrapy.spiders import SitemapSpider

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider


class AlaSitemapSpider(SitemapSpider, AlaSpider):

    def __init__(self, *a, **kw):
        super(AlaSitemapSpider, self).__init__(*a, **kw)
