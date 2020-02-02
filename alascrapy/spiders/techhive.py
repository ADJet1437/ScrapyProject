# -*- coding: utf8 -*-

from alascrapy.spiders.pcworld_en import Pcworld_enSpider

class TechhiveSpider(Pcworld_enSpider):
    name = 'techhive'
    allowed_domains = ['techhive.com']
    sitemap_urls = ['https://www.techhive.com/seo/sitemap/https/articles/index.xml']
