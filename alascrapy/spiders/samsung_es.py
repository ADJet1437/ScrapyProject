from samsung_uk import SamsungUkSpider

class SamsungEsSpider(SamsungUkSpider):
    name = 'samsung_es'
    allowed_domains = ["samsung.com"]
    start_urls = ['http://reviews.es.samsung.com/7463-es_es/allreviews.htm']

