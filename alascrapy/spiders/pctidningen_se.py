# -*- coding: utf8 -*-

from digitalfotoforalla_se import DigitalfotoforallaSeSpider


class PctidningenSeSpider(DigitalfotoforallaSeSpider):
    name = 'pctidningen_se'
    allowed_domains = ['pctidningen.se']
    domain = 'test.pctidningen.se'
