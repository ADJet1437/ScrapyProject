
# -*- coding: utf8 -*-

from digitalfotoforalla_se import DigitalfotoforallaSeSpider


class KotimikroFiSpider(DigitalfotoforallaSeSpider):
    name = 'kotimikro_fi'
    allowed_domains = ['kotimikro.fi']
    domain = 'testit.kotimikro.fi'

