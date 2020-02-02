# -*- coding: utf8 -*-
from alascrapy.spiders.base_spiders.bazaarvoice_spiderAPI5_5 \
    import BazaarVoiceSpiderAPI5_5


class SoshFrSpider(BazaarVoiceSpiderAPI5_5):
    name = 'sosh_fr'
    start_urls = ['https://shop.sosh.fr/mobile/achat-smartphone-neuf']

    bv_base_params = {
        'passkey': 'ca1XHmuPAcFW7kEwNE7ef4EhbpluWWKDRP5uFE513eJJc',
        'display_code': '13619-fr_fr',
        'content_locale': 'fr_FR',
    }

    def parse(self, response):
        reviews_xpath = '//*[@class="titre-produit"]/a/@href'
        review_links = response.xpath(reviews_xpath).extract()
        for link in review_links:
            yield response.follow(url=link, callback=self.parse_product_page)

    def parse_product_page(self, response):
        # Default bv_id xpath form parent spider is not working
        ean_xpath = '//meta[@itemprop="gtin13"]/@content'
        ean = self.extract(response.xpath(ean_xpath))
        response.meta['bv_id'] = ean
        yield self.call_review(response, incremental=False).next()
