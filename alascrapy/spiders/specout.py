# -*- coding: utf8 -*-
import json

from scrapy.http.request import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.items import CategoryItem, ProductItem, ProductIdItem
from alascrapy.lib.generic import get_base_url, set_query_parameter

class SpecoutSpider(AlaSpider):
    name = 'specout'
    allowed_domains = ['specout.com']
    download_delay=2

    load_urls = {'VR Headsets': 'http://virtual-reality-headsets.specout.com/ajax/filters/load?app_id=8565&compact=false&ids%5B%5D=54580&ids%5B%5D=54965&ids%5B%5D=54962&ids%5B%5D=55951&ids%5B%5D=54963&ids%5B%5D=54579&ids%5B%5D=55582&ids%5B%5D=54964&ids%5B%5D=54966&ids%5B%5D=55606',
                 'Cellphones': 'http://smartphones.specout.com/ajax/filters/load?app_id=770&compact=false&ids%5B%5D=7072&ids%5B%5D=4081&ids%5B%5D=5093&ids%5B%5D=7407&ids%5B%5D=4088&ids%5B%5D=46177&ids%5B%5D=41859&ids%5B%5D=7200&ids%5B%5D=7408&ids%5B%5D=4084&ids%5B%5D=37844&ids%5B%5D=31594&ids%5B%5D=56900&ids%5B%5D=22724&ids%5B%5D=20984&ids%5B%5D=43502&ids%5B%5D=5094',
                 'Tablets': 'http://tablets.specout.com/ajax/filters/load?app_id=774&compact=false&ids%5B%5D=4150&ids%5B%5D=31676&ids%5B%5D=8321&ids%5B%5D=32998&ids%5B%5D=4176&ids%5B%5D=4151&ids%5B%5D=8323&ids%5B%5D=4155&ids%5B%5D=8322&ids%5B%5D=16854&ids%5B%5D=21072&ids%5B%5D=18705&ids%5B%5D=43402&ids%5B%5D=4754',
                 'TVs': 'http://tvs.specout.com/ajax/filters/load?app_id=1029&compact=false&ids%5B%5D=15005&ids%5B%5D=6416&ids%5B%5D=52128&ids%5B%5D=53505&ids%5B%5D=6042&ids%5B%5D=21852&ids%5B%5D=54080&ids%5B%5D=54078&ids%5B%5D=54079&ids%5B%5D=53517&ids%5B%5D=6041&ids%5B%5D=6386&ids%5B%5D=35635&ids%5B%5D=8379&ids%5B%5D=17142',
                 'Headphones':'http://headphones.specout.com/ajax/filters/load?app_id=805&compact=false&ids%5B%5D=15132&ids%5B%5D=24621&ids%5B%5D=4416&ids%5B%5D=4417&ids%5B%5D=4431&ids%5B%5D=6861&ids%5B%5D=21693&ids%5B%5D=19221&ids%5B%5D=6641',
                 'Digital Cameras': 'http://digital-cameras.specout.com/ajax/filters/load?app_id=801&compact=false&ids%5B%5D=22401&ids%5B%5D=15130&ids%5B%5D=51972&ids%5B%5D=17160&ids%5B%5D=4402&ids%5B%5D=52586&ids%5B%5D=6605&ids%5B%5D=17942&ids%5B%5D=4475&ids%5B%5D=18047&ids%5B%5D=4478&ids%5B%5D=4479&ids%5B%5D=19847'
                 }

    products_url = {'Cellphones': 'http://smartphones.specout.com/ajax_search_sponsored?_len=100&page=0&app_id=770&_sortfld=expert_rating&_sortdir=DESC&_tpl=srp&head%5B%5D=_i_1&head%5B%5D=mm&head%5B%5D=os_version.display_value&head%5B%5D=release_date&head%5B%5D=_urr_avg_rating&head%5B%5D=expert_rating&head%5B%5D=_GC_money_srp&head%5B%5D=screen_size&head%5B%5D=talk_time&head%5B%5D=megapixels&head%5B%5D=price_w&head%5B%5D=storage_gb&head%5B%5D=weight_sp&head%5B%5D=_GC_money6&head%5B%5D=id&head%5B%5D=_encoded_title&head%5B%5D=amazon_asin&head%5B%5D=UPC&head%5B%5D=price_wo&head%5B%5D=asin_verizon&head%5B%5D=_price&head%5B%5D=amazon_url&head%5B%5D=bestbuy_affiliate&head%5B%5D=manufacturer_dropdown&head%5B%5D=amazon_gen&head%5B%5D=_avg_rating&head%5B%5D=_num_reviews',
                    'Tablets': 'http://tablets.specout.com/ajax_search?_len=100&page=0&app_id=774&_sortfld=expert_rating&_sortdir=DESC&_tpl=srp&head%5B%5D=_i_1&head%5B%5D=manufacturer_model&head%5B%5D=_GC_os_version_two&head%5B%5D=date_released&head%5B%5D=_urr_avg_rating&head%5B%5D=expert_rating&head%5B%5D=_GC_money&head%5B%5D=screen_size&head%5B%5D=battery_life&head%5B%5D=internal_memory&head%5B%5D=processor_speed&head%5B%5D=weight&head%5B%5D=front_camera&head%5B%5D=geekbench_multicore&head%5B%5D=rear_camera&head%5B%5D=ram&head%5B%5D=id&head%5B%5D=_encoded_title&head%5B%5D=os&head%5B%5D=android_versions&head%5B%5D=ios_versions&head%5B%5D=amazon_asin&head%5B%5D=upc&head%5B%5D=price&head%5B%5D=company&head%5B%5D=amazon_gen&head%5B%5D=_avg_rating&head%5B%5D=_num_reviews&head%5B%5D=ram',
                    'TVs': 'http://tvs.specout.com/ajax_search_sponsored?_len=100&page=0&app_id=1029&_sortfld=expert_rating&_sortdir=DESC&_tpl=srp&head%5B%5D=_i_1&head%5B%5D=company_product&head%5B%5D=displaytype&head%5B%5D=type_tv&head%5B%5D=_urr_avg_rating&head%5B%5D=expert_rating&head%5B%5D=_GC_money&head%5B%5D=size&head%5B%5D=display_tech&head%5B%5D=price_per_inch&head%5B%5D=mprt&head%5B%5D=display_tech_pregenfunc&head%5B%5D=id&head%5B%5D=_encoded_title&head%5B%5D=amazon_asin&head%5B%5D=upc&head%5B%5D=msrp&head%5B%5D=affiliate_link&head%5B%5D=bestbuy_affiliate&head%5B%5D=company&head%5B%5D=amazon_gen&head%5B%5D=_avg_rating&head%5B%5D=_num_reviews',
                    'Headphones': 'http://headphones.specout.com/ajax_search?_len=100&page=0&app_id=805&_sortfld=expert_rating&_sortdir=DESC&_tpl=srp&head%5B%5D=_i_1&head%5B%5D=manfacture_model&head%5B%5D=_GC_style_category&head%5B%5D=_urr_avg_rating&head%5B%5D=expert_rating&head%5B%5D=_GC_money_srp&head%5B%5D=additional_features&head%5B%5D=impedance&head%5B%5D=sensitivity&head%5B%5D=freq&head%5B%5D=freq_high&head%5B%5D=_GC_msrp_srp&head%5B%5D=Price&head%5B%5D=_GC_money&head%5B%5D=style&head%5B%5D=hp_cat_srp&head%5B%5D=id&head%5B%5D=_encoded_title&head%5B%5D=style_srp&head%5B%5D=hp_category&head%5B%5D=amazon_asin&head%5B%5D=upc&head%5B%5D=bestbuy_affiliate&head%5B%5D=affiliate_link_vmi&head%5B%5D=brand_text&head%5B%5D=amazon_gen&head%5B%5D=brand&head%5B%5D=_avg_rating&head%5B%5D=_num_reviews',
                    'VR Headsets': 'http://virtual-reality-headsets.specout.com/ajax_search?_len=100&page=0&app_id=8565&_sortfld=refresh_rate&_sortdir=DESC&_tpl=srp&head%5B%5D=_i_1&head%5B%5D=manufacturer_model&head%5B%5D=_GC_SRP_release_date_and_type&head%5B%5D=_GC_money_srp&head%5B%5D=refresh_rate&head%5B%5D=processing_source&head%5B%5D=field_of_view&head%5B%5D=weight&head%5B%5D=msrp&head%5B%5D=reality_type&head%5B%5D=id&head%5B%5D=_encoded_title&head%5B%5D=expected_release&head%5B%5D=release_date&head%5B%5D=amazon_asin',
                    'Digital Cameras': 'http://digital-cameras.specout.com/ajax_search?_len=100&page=0&app_id=801&_sortfld=expert_rating&_sortdir=DESC&_tpl=srp&head%5B%5D=_i_1&head%5B%5D=manufacturer_model&head%5B%5D=camera_category.display_value&head%5B%5D=release_date&head%5B%5D=_urr_avg_rating&head%5B%5D=expert_rating&head%5B%5D=_GC_money&head%5B%5D=sensor_format&head%5B%5D=megapixel&head%5B%5D=Max_ISO&head%5B%5D=shutter_speed_range_pregen&head%5B%5D=sensor_type_pregen&head%5B%5D=Price&head%5B%5D=sensor_size_text&head%5B%5D=_GC_sensortype&head%5B%5D=id&head%5B%5D=_encoded_title&head%5B%5D=amazon_asin&head%5B%5D=UPC&head%5B%5D=affiliate_link&head%5B%5D=affiliate_link_bestbuy&head%5B%5D=category_pregen&head%5B%5D=_avg_rating&head%5B%5D=_num_reviews'
                   }

    def __init__(self, *args, **kwargs):
         super(SpecoutSpider, self).__init__(self, *args, **kwargs)
         self.category = kwargs['category']

    def start_requests(self):
        category_name = self.category
        start_url = self.load_urls[category_name]
        _headers = self.get_headers(start_url)
        yield Request(url=start_url, headers=_headers,
                      callback=self.parse_cat_filters,
                      meta={'category_name': category_name})

    def get_headers(self, url):
        base_url= get_base_url(url)
        return {'Referer': base_url,
                'X-Requested-With': 'XMLHttpRequest'}

    def parse_cat_filters(self, response):
        category_name= response.meta['category_name']
        base_url= get_base_url(response.url)
        category = CategoryItem()
        category["category_path"] = category_name
        category["category_leaf"] = category_name
        category["category_url"] = base_url
        yield category

        response_json = json.loads(response.body_as_unicode())
        specs = response_json['specs']

        for spec in specs:
            if spec['f_name'] == 'Manufacturer':
                db_name = spec['db_name']
            else:
                continue

            if 'options' in spec:
                options = spec['options']
                filter_key = 'id'

            if 'tree' in spec:
                options = spec['tree']
                filter_key = 'key'


            if not options or not filter_key:
                raise Exception("Cannot find all manufacturer values in %s" % \
                                json.dumps(spec))

            for option in options:
                manufacturer = option['title']
                filter_value = option[filter_key]
                products_url = self.products_url[category_name]

                products_url = set_query_parameter(products_url,
                                                     '_fil[0][field]',
                                                     db_name)
                products_url = set_query_parameter(products_url,
                                                     '_fil[0][operator]',
                                                     '=')
                products_url = set_query_parameter(products_url,
                                                     '_fil[0][value]',
                                                     filter_value)

                _headers = self.get_headers(response.url)

                request = Request(products_url, self.parse_product,
                                  headers=_headers, meta={'dont_merge_cookies': True,
                                                          'dont_redirect': True},
                                  cookies={})
                request.meta['category'] = category
                request.meta['manufacturer'] = manufacturer
                yield request
            return

    def parse_product(self, response):
        #    self._check_if_blocked(response)
        category = response.meta['category']
        manufacturer = response.meta['manufacturer']
        base_url = get_base_url(response.url)

        json_response = json.loads(response.body_as_unicode())
        data = json_response["data"]
        image_url_format = "https://s3.graphiq.com/sites/default/files" \
                           "/%s/media/images/%s"
        product_url_format = "%s/l/%s/%s"
        product_name_fields = ["manufacturer_model", "manfacture_model",
                               "company_product", "mm"]
        name_index = ""
        amazon_asin_index=""
        upc_index = ""

        app_id= data["app_id"]
        page = data["page"]
        results = data['recs']

        id_index = data["head"].index("id")

        encoded_title_index = data["head"].index("_encoded_title")

        for name_field in product_name_fields:
            try:
                index = data["head"].index(name_field)
                name_index = index
                break
            except ValueError:
                continue

        if not name_index:
            raise Exception("Could not find product name in %s" % response.url)

        image_index = data["head"].index("_i_1")
        if 'amazon_asin' in data["head"]:
            amazon_asin_index = data["head"].index("amazon_asin")
        if 'UPC' in data["head"]:
            upc_index = data["head"].index("UPC")
        elif 'upc' in data["head"]:
            upc_index = data["head"].index("upc")

        for product_data in data["data"]:
            image_name = ""
            if len(product_data[image_index])>1:
                image_name = product_data[image_index][0]
            product = ProductItem()
            product['OriginalCategoryName'] = category['category_path']
            if image_name:
                product['PicURL'] = image_url_format % (app_id, image_name)
            product['TestUrl'] = product_url_format % (base_url,
                product_data[id_index], product_data[encoded_title_index])

            product['ProductManufacturer'] = manufacturer
            if name_index:
                product['ProductName'] = product_data[name_index]

            yield product

            if upc_index:
                if product_data[upc_index]:
                    upc = ProductIdItem()
                    upc['ProductName'] = product['ProductName']
                    upc['ID_kind'] = "UPC"
                    upc['ID_value'] = product_data[upc_index]
                    yield upc

            if amazon_asin_index:
                if product_data[amazon_asin_index]:
                    asin = ProductIdItem()
                    asin['ProductName'] = product['ProductName']
                    asin['ID_kind'] = "ASIN"
                    asin['ID_value'] = product_data[amazon_asin_index]
                    yield asin

        number_of_pages = int(int(results)/100)
        if page < number_of_pages:
            next_page_url = set_query_parameter(response.url,'page',page+1)
            _headers = self.get_headers(response.url)
            request = Request(next_page_url, self.parse_product,
                              headers=_headers, cookies={},
                              meta={'dont_merge_cookies': True,
                                    'dont_redirect': True})
            request.meta['manufacturer']=manufacturer
            request.meta['category']=category
            yield request
