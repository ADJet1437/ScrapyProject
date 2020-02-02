__author__ = 'leonardo'

from alascrapy.spiders.mediamarkt_at import MediaMarktATSpider


class MediaMarktATSpider(MediaMarktATSpider):
    name = 'saturn_at'
    allowed_domains = ['saturn.at']
    start_urls = ['http://www.saturn.at/']
    locale = 'de_AT'
    kind = 'saturn_at_id'