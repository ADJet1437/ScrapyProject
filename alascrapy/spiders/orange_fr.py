# -*- coding: utf8 -*-
#!/usr/bin/env python

from scrapy.http import Request

from alascrapy.items import ProductItem, ProductIdItem, ReviewItem
from alascrapy.lib.generic import get_full_url, date_format
from alascrapy.lib.conf import get_source_conf
from alascrapy.spiders.base_spiders.bazaarvoice_spiderAPI5_5 import BazaarVoiceSpiderAPI5_5

import alascrapy.lib.dao.incremental_scraping as incremental_utils


class OrangeFrSpider(BazaarVoiceSpiderAPI5_5):
    name = 'orange_fr'

    bv_base_params = {'passkey': 'caC8DbGJQvSbl3UNBL3JNmmrKPOseJWBq4MqpKnIK77i8',
                      'display_code': '12899-fr_fr',
                      'content_locale': 'fr_FR'}

    start_urls = ['https://boutique.orange.fr/mobile/choisir-un-mobile']

    def parse(self, response):

        product_list_xpath = "//div[@class='box-prod']/h2/a/@href"

        product_urls = self.extract_list(response.xpath(product_list_xpath))

        for product_url in product_urls:
            product_url = get_full_url(response, product_url)
            yield Request(url=product_url, callback=self.parse_product)

    def parse_product(self, response):

        product = ProductItem()
        product['TestUrl'] = response.url
        product['OriginalCategoryName'] = 'Cell phones' #self.extract_all(response.xpath('//ol[@id="breadcrumb-list"]/li/a/text()'),"->")

        productname_xpath ='//h1/span[@itemprop="name"]//text()'
        picurl_xpath = '//img[@id="Image1x"]//@src'
        manufactor_xpath = '//h1/span[@itemprop="brand"]//text()'
        ean_xpath = '//meta[@itemprop="gtin13"]/@content'

        product['ProductName'] = self.extract(response.xpath(productname_xpath))
        product['PicURL'] = get_full_url(response, self.extract(response.xpath(picurl_xpath)))
        product['ProductManufacturer'] = self.extract(response.xpath(manufactor_xpath))
        product['source_internal_id'] = self.extract(response.xpath(ean_xpath))
        yield product

        bv_params = self.bv_base_params.copy()
        bv_params['bv_id'] = product['source_internal_id']
        bv_params['offset'] = 0
        review_url = self.get_review_url(**bv_params)
        request = Request(url=review_url, callback=self.parse_reviews)

        last_user_review = incremental_utils.get_latest_user_review_date_by_sii(
            self.mysql_manager, self.spider_conf['source_id'],
            product["source_internal_id"]
        )
        request.meta['last_user_review'] = last_user_review

        request.meta['bv_id'] = product['source_internal_id']
        request.meta['product'] = product
        request.meta['extra_parser'] = self.final_review_parser

        request.meta['filter_other_sources'] = False

        yield request

    def final_review_parser(self, review, reviewData):
        verdict_rating_scale = 100
        rating_scale_factor = verdict_rating_scale / int(review['SourceTestScale'])
        verdict_format = "{}: {:d}/{:d}, "

        temp_verdict = ''
        for key in reviewData.get('SecondaryRatings', {}):
            reviewData['SecondaryRatings'][key]

            label = ''
            if key == 'Autonomie_1':
                label = 'autonomie'
            elif key == 'rapport_qualite_prix':
                label = u'rapport qualité/prix'
            elif key == 'facilite_utilisation':
                label = u"facilité d'utilisation"
            elif key == 'performances_multimedia':
                label = u'performances multimédia'
            elif key == 'catalogue_dapplications_jeux':
                label = "catalogue d'applications/jeux"
            elif key == 'design':
                label == 'design'

            number = reviewData['SecondaryRatings'][key]['Value']
            if label and number:
                scaled_number = int(number) * rating_scale_factor
                temp_verdict += verdict_format.format(label.encode('utf-8'), scaled_number, verdict_rating_scale)

        review['TestVerdict'] = temp_verdict.rstrip(', ')
        return review
