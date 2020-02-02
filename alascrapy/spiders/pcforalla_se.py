# -*- coding: utf8 -*-
from m3_se import M3IdgSE


class PcForAllaSpider(M3IdgSE):
    name = 'pcforalla_se'
    allowed_domains = ['pcforalla.idg.se']
    start_urls = ['https://pcforalla.idg.se/2.30484/tester?ref=topTest']
