#!/usr/bin/env python

from alascrapy.items import CategoryItem, ProductItem, ProductIdItem
from alascrapy.spiders.base_spiders.ala_sitemap_spider import AlaSitemapSpider
from alascrapy.spiders.base_spiders.bazaarvoice_spider import BazaarVoiceSpider


class PhilipsNlSpider(AlaSitemapSpider, BazaarVoiceSpider):
    name = 'philips_nl'
    sitemap_urls = ['https://www.philips.nl/sitemap-B2C-nl_NL-web-index.xml']
    sitemap_follow = ['product-catalog']
    sitemap_rules = [('reviewenawards', 'parse_product')]

    source_id = 100000010

    bv_subdomain = "philips.ugc.bazaarvoice.com"
    bv_site_locale = "7543b-nl_nl"

    brand_name = 'Philips'

    def parse_product(self, response):
        product = ProductItem()
        product['TestUrl'] = response.url
        product['ProductManufacturer'] = self.brand_name

        product_name_xpath = "//meta[@name='PS_DTN']/@content"
        pic_url_xpath = "//meta[@name='ISS_IMAGE']/@content"
        sii_xpath = "//meta[@name='PHILIPS.METRICS.PRODUCTID']/@content"

        product_name_orig = self.extract(response.xpath(product_name_xpath))
        if not product_name_orig:
            return

        product['ProductName'] = self.brand_name + ' ' + product_name_orig

        category_path_xpath = "//meta[@name='ISS_GROUP_KEY_NEW']/@content"
        category_path = self.extract(response.xpath(category_path_xpath))
        if category_path:
            category = CategoryItem()
            category['category_path'] = category_path
            product['OriginalCategoryName'] = category_path

            if self.should_skip_category(category):
                return
            yield category

        product['PicURL'] = self.extract(response.xpath(pic_url_xpath))
        product['source_internal_id'] = self.extract(response.xpath(sii_xpath))
        yield product

        # We were using product MPNs as philips_id,
        # do the same thing in alaScrapy spider
        philips_id = ProductIdItem.from_product(product, kind='philips_id',
                                                value=product_name_orig)
        yield philips_id

        eans_xpath = "//meta[@name='PS_GTIN']/@content"
        ean = self.extract(response.xpath(eans_xpath))
        if ean:
            ean_item = ProductIdItem.from_product(product, kind='EAN',
                                                  value=ean)
            yield ean_item

        request = self.start_reviews(response, product,
                                     filter_other_sources=False)
        request.meta['product'] = product
        yield request
