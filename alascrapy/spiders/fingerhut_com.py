__author__ = 'jim'

from scrapy.http import Request
from alascrapy.items import ProductItem
from alascrapy.spiders.base_spiders.bazaarvoice_spider import BVNoSeleniumSpider

import re


class FingerhutComSpider(BVNoSeleniumSpider):
    name = 'fingerhut_com'
    allowed_domains = ['fingerhut.com']
    start_urls = ['http://reviews.fingerhut.com/3526/allreviews.htm']

    default_kind = 'fingerhut_id'
    parse_BV_product = True

    # Fingerhut blocks spiders quite easily in www.fingerhut.com.
    # we must improve our proxy management before scraping this page
    #
    # source_internal_id_re = re.compile(r'"product_code":\s*"([^"]+)"')
    # mpn_re = re.compile(r'"product_model":\s*"([^"]+)"')
    # brand_re = re.compile(r'"entity_brandName":\s*"([^"]+)"')
    # pic_re = re.compile(r'"entity_thumbnailUrl":\s*"([^"]+)"')
    #
    # def _parse_product(self, response):
    #     product = ProductItem()
    #     info_xpath = '//script[@id="tmpl-product-finance"]/following::script[@type="text/javascript"][1]/text()'
    #     info_alt_xpath = "//script[contains(text(), 'product_model') and contains(text(), 'window.utag_data')]/text()"
    #
    #     info = self.extract(response.xpath(info_xpath))
    #     if not info:
    #         info = self.extract(response.xpath(info_alt_xpath))
    #     else:
    #         raise Exception("Could not extract javascript code")
    #
    #
    #     product['TestUrl'] = response.url
    #     product['OriginalCategoryName'] = response.meta['category']['category_path']
    #     sii = re.search(self.source_internal_id_re, info)
    #     if sii:
    #         product['source_internal_id'] = sii.group(1)
    #     pic_url = re.search(self.pic_re, info)
    #     if pic_url:
    #         product['PicURL'] = pic_url.group(1)
    #     brand = re.search(self.brand_re, info)
    #     if brand:
    #         product['ProductManufacturer'] = brand.group(1)
    #
    #     mpn = re.search(self.mpn_re, info)
    #     if mpn:
    #         product['ProductName'] = "%s %s" % (product["ProductManufacturer"],
    #                                             mpn.group(1))
    #     else:
    #         name = self.extract(response.xpath('//title/text()'))
    #         product['ProductName'] = name
    #
    #     mpn = self.product_id(product)
    #     mpn['ID_kind'] = "MPN"
    #     mpn['ID_value'] = mpn
    #     yield mpn
    #
    #     fingerhut_id = self.product_id(product)
    #     fingerhut_id['ID_kind'] = 'fingerhut_id'
    #     fingerhut_id['ID_value'] = product['source_internal_id']
    #     yield fingerhut_id
    #
    #     yield product
    #
    #     review_url = response.meta['review_url']
    #     request = Request(url=review_url, callback=self.parse_reviews)
    #     request.meta['product'] = product
    #     request.meta['product_id'] = fingerhut_id
    #     yield request
