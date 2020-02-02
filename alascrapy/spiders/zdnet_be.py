# -*- coding: utf8 -*-

from alascrapy.spiders.techpulse_be import Techpulse_BeSpider


class Zdnet_BeSpider(Techpulse_BeSpider):
    name = 'zdnet_be'
    allowed_domains = ['zdnet.be']
    start_urls = ['http://www.zdnet.be/review/']

    review_url_xpath = "//h3/a"
    last_date_xpath = "(//div[@class='content']/p[@class='meta'])[last()]/text()"
