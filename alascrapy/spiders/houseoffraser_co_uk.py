__author__ = 'frank'

from scrapy.http import Request

from alascrapy.items import CategoryItem
from alascrapy.lib.generic import get_full_url
from alascrapy.spiders.base_spiders.bazaarvoice_spiderAPI5_5 import BazaarVoiceSpiderAPI5_5
from alascrapy.spiders.base_spiders.ala_sitemap_spider import AlaSitemapSpider

import alascrapy.lib.dao.incremental_scraping as incremental_utils

import re


class HouseOfFraserCoUkSpider(AlaSitemapSpider, BazaarVoiceSpiderAPI5_5):
    name = 'houseoffraser_co_uk'
    sitemap_urls = ['https://www.houseoffraser.co.uk/sitemap/sitemap_electricals.xml',
                    'https://www.houseoffraser.co.uk/sitemap/sitemap_beauty.xml']

    # The site uses Bazaarvoice API 5.4 and does not have display_code in its URL pattern,
    # thus we need a customized URL format for it
    bv_base_params = {'passkey': 'ca7Kth4OijwCDydIgogLz2XHokIOZ3CycsLAe8RwG42ew',
                      'content_locale': 'en_GB'}

    LIMIT = 100

    FULL_URL_PATTERN = 'http://api.bazaarvoice.com/data/batch.json?passkey={passkey}' \
                       '&apiversion=5.4&resource.q0=reviews&filter.q0=productid:eq:{bv_id}' \
                       '&filter.q0=contentlocale:eq:{content_locale}' \
                       '&sort.q0=submissiontime:desc&stats.q0=reviews&filteredstats.q0=reviews' \
                       '&include.q0=authors,products&filter_reviews.q0=contentlocale:eq:{content_locale}' \
                       '&filter_reviewcomments.q0=contentlocale:eq:{content_locale}&limit.q0=' + str(LIMIT) + '' \
                       '&offset.q0={offset}'

    def parse(self, response):
        product_data = self.extract(response.xpath("//script[@type='text/javascript']"
                                                   "[contains(text(),'hof.data')]/text()"))
        product_id_re = r'"FriendlyProductId":"([0-9]+)"'

        current_page = response.meta.get('page_number')
        category = response.meta.get('category', '')
        original_url = response.meta.get('original_url', '')

        if not category:
            # We should be able to spot category name from the URL.
            # Otherwise we will need to parse category name from JavaScript,
            # as the site loads its product pages using knockout.js
            category = CategoryItem()
            category['category_path'] = response.url
            category['category_url'] = response.url
            yield category

            if self.should_skip_category(category):
                return

            current_page = 1
            original_url = response.url

        product_ids = re.findall(product_id_re, product_data)
        if not product_ids:
            return

        for product_id in product_ids:

            bv_params = self.bv_base_params.copy()
            bv_params['bv_id'] = product_id
            bv_params['offset'] = 0
            review_url = self.get_review_url(**bv_params)

            request = Request(url=review_url, callback=self.parse_reviews)
            last_user_review = incremental_utils.get_latest_user_review_date_by_sii(
                self.mysql_manager, self.spider_conf['source_id'],
                product_id
            )
            request.meta['last_user_review'] = last_user_review
            request.meta['bv_id'] = product_id
            request.meta['product_id'] = product_id
            request.meta['OriginalCategoryName'] = category.get('category_path')

            request.meta['filter_other_sources'] = False

            yield request

        next_page = current_page + 1
        next_page_url = original_url + '?page={}'.format(next_page)
        next_page_request = Request(url=next_page_url, callback=self.parse)
        next_page_request.meta['page_number'] = next_page
        next_page_request.meta['category'] = category
        next_page_request.meta['original_url'] = original_url
        yield next_page_request
