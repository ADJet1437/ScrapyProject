import json

from scrapy.http import Request

import pytz

from alascrapy.lib.generic import strip, date_format, dateparser

import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.items import ProductIdItem, ProductItem, ReviewItem

"""
    This class is a generic spider for websites that uses Bazaar Voice
"""
class BazaarVoiceSpiderAPI5_5(AlaSpider):

    """
        BV limits to 100 items at max per query,
        otherwise empty answer with error message
    """
    LIMIT = 100

    """
        Pattern of the new BV API
        Parameters :
        {0} : passkey of the client (use network dev tools to find it)
        {1} : internal product id
        {2} : offset, BV limits to 100 items at max, so pagination could be needed if we want all reviews
    """
    FULL_URL_PATTERN = 'http://api.bazaarvoice.com/data/batch.json' \
                     '?passkey={passkey}' \
                     '&apiversion=5.5' \
                     '&displaycode={display_code}' \
                     '&resource.q0=reviews' \
                     '&filter.q0=productid:eq:{bv_id}' \
                     '&filter.q0=contentlocale:eq:{content_locale}' \
                     '&sort.q0=submissiontime:desc' \
                     '&stats.q0=reviews' \
                     '&filteredstats.q0=reviews' \
                     '&include.q0=authors,products' \
                     '&filter_reviews.q0=contentlocale:eq:{content_locale}' \
                     '&filter_reviewcomments.q0=contentlocale:eq:{content_locale}' \
                     '&limit.q0=' + str(LIMIT) + '' \
                     '&offset.q0={offset}'

    def __init__(self, *a, **kw):
        super(BazaarVoiceSpiderAPI5_5, self).__init__(*a, **kw)

    """
        parses reviews returned in response body json
    """
    def parse_reviews(self, response):
        jsonresponse = json.loads(response.body_as_unicode())
        if jsonresponse.get('BatchedResults', {}):
            query = jsonresponse['BatchedResults']['q0']
        elif jsonresponse.get('data', {}):
            query = jsonresponse['data']
        else:
            return

        limit = query['Limit']
        offset = query['Offset']
        totalReviews = query['TotalResults']
        stop_scraping = False

        bv_id = response.meta['bv_id']
        filter_other_sources = response.meta.get('filter_other_sources', True)
        extra_parser = response.meta.get('extra_parser', None)

        if offset == 0 and query.get('Includes', {}).get('Products', {}).get(bv_id, {}):
            product_info = query['Includes']['Products'][bv_id]

            # if product is not part of metadata, it should be parsed through BV API
            product = response.meta.get('product', None)
            if not product:
                product = self.parse_product_from_bv(product_info, response.meta.get('OriginalCategoryName', ''),
                                                     source_internal_id=response.meta.get('product_id', None))
                response.meta['product'] = product
                yield product

            for ean in product_info.get('EANs', []):
                ean_id = ProductIdItem.from_product(product, kind='EAN', value=ean)
                yield ean_id

            for upc in product_info.get('UPCs', []):
                upc_id = ProductIdItem.from_product(product, kind='UPC', value=upc)
                yield upc_id

            # The MPNs provided by BV API of some sources seem not very accurate.
            # They are more like source internal IDs.
            #for mpn in product_info.get('ManufacturerPartNumbers', []):
            #    mpn_id = self.product_id(product, kind='MPN', value=mpn)
            #    yield mpn_id

        for review in query['Results']:
            # review is from another product, skip
            if review.get('ProductId', bv_id) != bv_id:
                continue

            if filter_other_sources and review.get('IsSyndicated', True):
                continue

            parsedReview = self.parse_review(response, review, extra_parser)
            if response.meta.get('last_user_review', ''):
                current_user_review = dateparser.parse(parsedReview['TestDateText'],
                                                       date_formats=['%Y-%m-%d'])
                if current_user_review < response.meta['last_user_review']:
                    stop_scraping = True
                    break

            yield parsedReview

        # first review page, now we know the total review count and
        # thus can trigger all other pages parsing.
        if offset + limit < totalReviews and not stop_scraping:
            # there is a need to call the next page of reviews
            bv_params = self.bv_base_params.copy()
            bv_params['bv_id'] = bv_id
            bv_params['offset'] = offset + limit
            fullUrl = self.get_review_url(**bv_params)
            request = Request(fullUrl, callback=self.parse_reviews,
                              meta=response.meta)
            offset += limit
            yield request

    def get_review_url(self, **kw):
        return self.FULL_URL_PATTERN.format(**kw)

    # TODO: if necessary, we can make a dictionary to tell which part of product item should be overwritten
    def parse_product_from_bv(self, product_data, original_category_name,
                              source_internal_id=None, _product=None, overwrite=False):
        product = _product if _product else ProductItem()

        if not product.get('OriginalCategoryName'):
            product['OriginalCategoryName'] = original_category_name

        if overwrite or not product.get('ProductName'):
            product['ProductName'] = product_data.get('Name', '')

        if overwrite or not product.get('source_internal_id'):
            if source_internal_id:
                product['source_internal_id'] = source_internal_id
            else:
                product['source_internal_id'] = product_data.get('Id', '')

        # TODO: test if URLs are valid?
        if overwrite or not product.get('PicURL'):
            product['PicURL'] = product_data.get('ImageUrl', '')
        if overwrite or not product.get('TestUrl'):
            product['TestUrl'] = product_data.get('ProductPageUrl', '')

        if overwrite or not product.get('ProductManufacturer'):
            product['ProductManufacturer'] = product_data.get('Brand', {}).get('Name', {})

            # TODO: undo this step if it does not make sense for most of the sources
            if product['ProductManufacturer'] and \
                    product['ProductManufacturer'].lower() not in product['ProductName'].lower():
                product['ProductName'] = product['ProductManufacturer'] + ' ' + product['ProductName']

        return product

    """
        parses a single review
    """
    def parse_review(self, response, reviewData, extra_parser=None):
        product = response.meta['product']

        review = ReviewItem.from_product(
            product = product,
            rating = reviewData['Rating'],
            scale =  reviewData['RatingRange'],
            date = date_format(reviewData['SubmissionTime'],
                               '%Y-%m-%dT%H:%M:%S'),
            author = reviewData['UserNickname'],
            title = reviewData['Title'],
            summary = reviewData['ReviewText'],
            pros = reviewData['Pros'],
            cons = reviewData['Cons'],
            tp = 'USER'
        )

        if not review.get('TestPros', ''):
            review['TestPros'] = ' ; '.join(reviewData.get('TagDimensions', {}).get('Pro', {}).get('Values', []))

        if not review.get('TestCons', ''):
            review['TestCons'] = ' ; '.join(reviewData.get('TagDimensions', {}).get('Con', {}).get('Values', []))

        if extra_parser:
            review = extra_parser(review, reviewData)

        return review

    def call_review(self, response, product=None, incremental=True):
        bv_id = response.meta.get('bv_id', None)

        if not bv_id:
            bv_id_xpath = "//div/@data-product-id"
            bv_id = self.extract_xpath(response, bv_id_xpath)

        if incremental:
            last_user_review = incremental_utils.get_latest_user_review_date_by_sii(
                self.mysql_manager, self.spider_conf['source_id'],
                product["source_internal_id"]
            )
            response.meta['last_user_review'] = last_user_review

        bv_params = self.bv_base_params.copy()
        bv_params['bv_id'] = bv_id
        bv_params['offset'] = 0
        fullUrl = self.FULL_URL_PATTERN.format(**bv_params)

        response.meta['product'] = product
        response.meta['bv_id'] = bv_id
        request = Request(fullUrl, callback=self.parse_reviews,
                          meta=response.meta)
        yield request

