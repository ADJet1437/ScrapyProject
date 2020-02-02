# -*- coding: utf-8 -*-
import scrapy
from alascrapy.spiders.base_spiders.google_custom_search_api import GoogleCustomSearchApiSpider
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider

class GcseDroneSpider(GoogleCustomSearchApiSpider, AlaSpider):
    name = 'gcse_drone'
    allowed_domains = ['googleapis.com']
    keyword = "drone+review"
    ENGINE_ID = "005191276492245267773:z-2yd-ndp2m"
    KPI_KEY = "AIzaSyCmyupeOgRdGBT0MYA4bnTglT0qzHdAgLk"
    template = "https://www.googleapis.com/customsearch/v1?filter=1&q={0}&num=10&key={1}&start=1&cx={2}".format(keyword, KPI_KEY, ENGINE_ID)
    
    start_urls = [template]
