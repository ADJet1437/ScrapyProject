# -*- coding: utf8 -*-

from stuff_tv import StuffTvSpider

class StuffTvSpider(StuffTvSpider):
    name = 'stuff_tv_in'
    allowed_domains = ['stuff.tv']
    start_urls = ['http://www.stuff.tv/in/reviews']
        
