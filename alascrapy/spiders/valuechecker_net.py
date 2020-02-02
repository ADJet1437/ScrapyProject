# -*- coding: utf8 -*-
from __future__ import print_function
from __future__ import unicode_literals

import csv
import os
import re
from pprint import pprint as print
from scrapy.http import Request

from alascrapy import items
from alascrapy.spiders.base_spiders import ala_spider


PATH_TO_PRODUCTS_FILE = '/tmp/valuechecker_feedin/products.csv'
PATH_TO_PRODUCT_IDS_FILE = '/tmp/valuechecker_feedin/product_ids.csv'


files = {'products': PATH_TO_PRODUCTS_FILE,
         'product_ids': PATH_TO_PRODUCT_IDS_FILE}

# magic prefix for source_id to show that this source is used for valuechecker
MAGIC_NUMBER = '777'

#  table of original source_ids for sources in vinnie
#  '3140' - 'tweakers_id', # tweakers.net
#  '44000092' - 'idealo_id',  # idealo.co.uk
#  '4904' - 'pricerunner_id_de', # pricerunner.de
#  '263852' - 'pricerunner_id_uk', # pricerunner.co.uk
#  '4780' - 'prisjakt_id', # prisjakt.no
#  '263853' - 'pricerunner_id_se', # pricerunner.se
#  '4622' - 'prisjakt_id', # prisjakt.nu
#  '3213' - 'tweakers_id', # tweakers.net (Belgium)
#  '3320' - 'idealo_fr_id', # idealo.fr
#  '49065' - 'idealo_de_id', # idealo.de
#  '4504' - 'pricerunner_id_dk', # pricerunner.dk
#  '44000089' - 'prisjakt_id', # pricespy.co.uk
#  '10000283' - 'bestbuy_ud', # bestbuy.com
#  '32000013' - 'kieskeurig_id', # kieskeurig.be
#  '300004' - 'kieskeurig_id', # kieskeurig.nl
#

# sources in valuechecker database with already added magic_number
# Obtained on the VC database from table `valuechecker.sources`
# '777 + source_id': 'id_kind',
SOURCE_KINDS_TABLE = {
    '7771001' : 'bestbuy_id',           # bestbuy.com
    '7771002' : 'gsmarena_id',          # gsmarena.com
    '77710000': 'vc_alatest_catalog',   # alatest_catalog
    '77731001': 'tweakers_id',          # tweakers.net
    '77731002': 'kieskeurig_id',        # kieskeurig.nl
    '77732001': 'tweakers_id',          # tweakers.be (Belgium)
    '77732002': 'kieskeurig_id',        # kieskeurig.be
    '77733001': 'idealo_id',            # idealo.fr
    '77733003': 'prisjakt_id',          # ledenicheur.fr
    '77734001': 'idealo_id',            # idealo.es
    '77744001': 'pricerunner_id',       # pricerunner.co.uk
    '77744002': 'prisjakt_id',          # pricespy.co.uk
    '77744003': 'idealo_id',            # idealo.co.uk
    '77744005': 'geizhals_id',          # skinflint.co.uk
    '77745001': 'pricerunner_id',       # pricerunner.dk
    '77745002': 'prisjakt_id',          # prisjagd.dk
    '77746001': 'pricerunner_id',       # pricerunner.se
    '77746002': 'prisjakt_id',          # prisjakt.nu
    '77747001': 'prisjakt_id',          # prisjakt.no
    '77749001': 'pricerunner_id',       # pricerunner.de
    '77749002': 'idealo_id',            # idealo.de
    '77749004': 'geizhals_id',          # geizhals.de
}


class FeedFileParser(object):
    """
    object for parsing csv files from valuechecker feed
    """
    COLUMNS = []

    def __init__(self, filepath):
        self._filepath = filepath

    def parse(self):
        """
        :rtype None:
        """
        with open(self._filepath) as f:
            # potential problem for python3 version. don't want to fix it now
            delimiter = '‖'.encode('utf-8')
            # read one line just to skip header of the file
            f.readline()
            for row in f:
                # hate it, but still. splitlines to remove \n character,
                # sptil by delimiter and zip with column names, to get
                # dict with all product data
                row_to_dict = {x[0]: x[1] for x in zip(self.COLUMNS,
                                                       row.splitlines()[0].split(delimiter))}

                yield row_to_dict


class ProductsFileParser(FeedFileParser):
    """Override header for products file"""
    COLUMNS = ['sid', 'source_internal_id', 'pid', 'productname', 'category', 'manufacturer', 'url', 'pic_url' ]

    def __init__(self, filepath):
        super(ProductsFileParser, self).__init__(filepath)


class ProductIDsFileParser(FeedFileParser):
    """Override header for product_ids file"""
    COLUMNS = ['pid', 'id_kind', 'id_value']

    def __init__(self, filepath):
        super(ProductIDsFileParser, self).__init__(filepath)


class CacheForProductIDs(object):
    """
    object, that will be used to store product_id : id_kind info
    maybe structure will be improved in future
    {
        'product_id' : {
            'kind_id' : 'kind_id_value',
            'product_name' : 'name',
            'source_internal_id' : 'id',
            'source_id' : id
        }
    }
    """

    def __init__(self):
        self._products = {}

    def __getitem__(self, key):
        """Method for debugging, for get element like cache[index]."""
        key = self._products.keys()[key]
        print({key: self._products[key]})
        return

    def _get_kind_id(self, source_id):
        """
        :param source_id: already changed source_id with MAGIC_NUMBER at the
        beginning
        """
        # TODO(mdovgal): need to add try / except block
        # and just log message. 'cause it's non trivial error
        return SOURCE_KINDS_TABLE[source_id]

    def add(self, product_id, **kwargs):
        """
        :param product_id:
        :param kwargs: source_id
                       product_name
                       source_internal_id
        :rtype: None
        """
        # TODO(mdovgal): need to figure out how to deal with the situation
        # when we already have this product id in cache
        kwargs['source_id'] = MAGIC_NUMBER + kwargs['source_id']

        if 'source_id' in kwargs:
            kwargs['kind_id'] = self._get_kind_id(kwargs['source_id'])

        # change from original valuechecher source id to our with MN before

        self._products[product_id] = dict(**kwargs)

    def get(self, product_id):
        """
        :param product_id: valuechecker id of a product
        :return: None or dict with kind_id and product name
        info
        """
        try:
            return self._products[product_id]
        except KeyError as e:
            # if we don't have this product
            # very awkward situation, but still real
            # log it and reraise

            # now I skip products for source_id = 10000. so return None if
            # we can't find product
            return None
            # raise

    def count(self):
        """:return: amount of all cached products."""
        return len(self._products.keys())

    def print_all(self):
        """pprint all products that were cached."""
        print(self._products)


class ValueCheckerSpider(ala_spider.AlaSpider):
    """
    main class for dealing with valuechecker feed in files
    """
    name = 'valuechecker_net'
    products_file_url = "https://us-east4-consummate-fold-158813.cloudfunctions.net/vc-alatest-feed-pipeline?filename=products.csv&api_key=M4UxWBb6Gf9gmUhHFfY9Mc4t7jM7zDcb"
    product_ids_file_url = "https://us-east4-consummate-fold-158813.cloudfunctions.net/vc-alatest-feed-pipeline?filename=product_ids.csv&api_key=M4UxWBb6Gf9gmUhHFfY9Mc4t7jM7zDcb"
    # start url contains link to gcp cloud function on vc side that
    # will return real function to products file.
    # also we have one starting url for products file. product_ids file
    # need to be process after products one. That's why to be sure that
    # it will be executed after Request will be triggered at the end of
    # parse_product_file function
    start_urls = {products_file_url,
                  product_ids_file_url}

    def __init__(self, *args, **kwargs):
        super(ValueCheckerSpider, self).__init__(*args, **kwargs)
        self.cache = CacheForProductIDs()
        self.process_file_callbacks = {'products': self.process_products_file}
        # create folder for temp files if it is not there for some reason
        try:
            os.makedirs('/tmp/valuechecker_feedin')
        except OSError as e:
            pass


    def parse(self, response):
        """
        :param response: standart scrapy response object
        For this spider this function will accept different links as
        parameters and after make another call to get real file.
        Cloud function intergration on VC side is used.
        """
        if response.request.url in self.start_urls:
            yield Request(url=response.body, callback=self.parse_vc_file)

    def parse_vc_file(self, response):
        """save file recieved from GCS bucket on drive to be able to use
        old spiders code, not to change idea of processing local files."""
        # here file name can be only one, but not to make if/else statements
        # to check if we get something
        filenames = re.findall(r'vc2-feeds-bucket/(.*?).csv', response.url)
        for filename in filenames:
            with open(files[filename], 'w') as f:
                f.write(response.body)

            for item in self.process_file_callbacks[filename]():
                yield item

    def process_products_file(self):
        """
        process product files with saving categories, products and
        product ids (for real kind id and for valuechecker_pid)
        """
        products = ProductsFileParser(filepath=PATH_TO_PRODUCTS_FILE)
        for product in products.parse():
            # get kind_id from source_kinds_table. will be None if we don't
            # know this source.
            kind_id = SOURCE_KINDS_TABLE.get(MAGIC_NUMBER + product['sid'], None)

            if kind_id is None:
                continue

            self.cache.add(product_id=product['pid'],
                           source_id=product['sid'],
                           product_name=product['productname'],
                           source_internal_id=product['source_internal_id'])

            item = items.ProductItem()
            item['ProductName'] = product['productname']
            item['source_internal_id'] = product['source_internal_id']
            item['OriginalCategoryName'] = product['category']
            item['TestUrl'] = product['url']
            item['ProductManufacturer'] = product['manufacturer']
            item['PicURL'] = product['pic_url']
            item['source_id'] = MAGIC_NUMBER + product['sid']
            yield item

            # save product for original kind (`local_kind` like `geizhals_de_id`. See story #169011934)
            prod_id_item = items.ProductIdItem()
            prod_id_item['ID_kind'] = kind_id
            prod_id_item['ID_value'] = product['source_internal_id']
            prod_id_item['source_internal_id'] = product['source_internal_id']
            prod_id_item['source_id'] = MAGIC_NUMBER + product['sid']
            prod_id_item['ProductName'] = product['productname']
            yield prod_id_item

            # save product item for valuechecker_pid kind
            prod_id_item = items.ProductIdItem()
            prod_id_item['ID_kind'] = 'valuechecker_pid'
            prod_id_item['ID_value'] = product['pid']
            prod_id_item['source_internal_id'] = product['source_internal_id']
            prod_id_item['source_id'] = MAGIC_NUMBER + product['sid']
            prod_id_item['ProductName'] = product['productname']
            yield prod_id_item

            # here will be yield category
            category = items.CategoryItem()
            category['category_path'] = product['category']
            category['source_id'] = MAGIC_NUMBER + product['sid']
            yield category

        allowed_kind_ids = ['first_publish_date', 'EAN', 'screen_size', 'MPN']

        product_ids = ProductIDsFileParser(filepath=PATH_TO_PRODUCT_IDS_FILE)
        for product_id in product_ids.parse():
            # we skip all product ids whose kind id is not in the list
            if product_id['id_kind'] not in allowed_kind_ids:
                continue
            # get product from cache. we add them during parsing products file
            cached_product = self.cache.get(product_id['pid'])
            # check if product exists in our cache. skip if not
            if not cached_product:
                continue

            item = items.ProductIdItem()

            item['ID_kind'] = product_id['id_kind']
            item['ID_value'] = product_id['id_value']
            item['source_internal_id'] = cached_product['source_internal_id']
            item['ProductName'] = cached_product['product_name']
            item['source_id'] = cached_product['source_id']
            yield item