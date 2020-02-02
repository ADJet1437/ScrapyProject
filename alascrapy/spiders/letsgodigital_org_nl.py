# -*- coding: utf8 -*-
from alascrapy.spiders.letsgodigital_org_en import LetsGoDigitalOrgEnSpider


class LetsGoDigitalOrgNlSpider(LetsGoDigitalOrgEnSpider):
    name = 'letsgodigital_org_nl'
    allowed_domains = ['nl.letsgodigital.org']
    start_urls = ['https://nl.letsgodigital.org/']
