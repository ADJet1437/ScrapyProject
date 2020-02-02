#!/usr/bin/env python
import requests
import logging
import hmac, hashlib
import xmltodict, json
import re
import StringIO

from urllib import urlencode
from time import strftime, gmtime, sleep
from base64 import b64encode
from collections import OrderedDict
from lxml import etree
from distutils.util import strtobool
from alascrapy.lib.conf import get_project_conf


class AmazonAPI(object):

    def __init__(self, spider):
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        self.project_conf = get_project_conf()
        self.spider = spider
        self.endpoint = self.spider.endpoint


    def amazon_request(self, params):

        url, allParams = self.generate_amazon_url_and_load_params(params)
        response = requests.get(url, params=allParams)
        sleep(1.0)
        return response

    """
        This method loads generic params (Amazon credentials) into params and also return the url that
        is amazon endpoint
    """
    def generate_amazon_url_and_load_params(self, params, doAuth=True):
        # url
        uri = "/onca/xml"
        url = "http://%s%s" % (self.endpoint, uri)

        if doAuth:
            # print('doAuth params : ')
            # print(str(params))
            params = self.doAuth(params, uri)
        else:
            for k, v in params.iteritems():
                if isinstance(v, unicode):
                    params[k] = v.encode('utf-8')
            params = OrderedDict(sorted(params.items(), key=lambda t: t[0]))

        return (url, params)

    def doAuth(self, params, uri):
        # params
        associate_tag = self.spider.associate_tag
        subscription_id = self.spider.subscription_id
        secret_key = self.spider.secret_key
        api_version = self.project_conf.get('AMAZON', 'api_version')

        params['AssociateTag'] = associate_tag
        params['AWSAccessKeyId'] = subscription_id
        params['Version'] = api_version
        params["Timestamp"] = strftime("%Y-%m-%dT%H:%M:%S.000Z", gmtime())

        #print('doAuth params : ')
        #print(str(params))

        for k, v in params.iteritems():
            if isinstance(v, unicode):
                params[k] = v.encode('utf-8')

        params = OrderedDict(sorted(params.items(), key=lambda t: t[0]))
        canonical_query_string = urlencode(params, doseq=True)
        canonical_query_string = canonical_query_string.replace('+', '%20')

        string_to_sign = "GET\n%s\n%s\n%s" % (self.endpoint, uri, canonical_query_string)
        _hash = hmac.new(secret_key, string_to_sign, hashlib.sha256)
        signature = b64encode(_hash.digest())
        params['Signature'] = signature
        return params

    def get_node(self, node_id):
        params = {"Service": "AWSECommerceService",
                  "Operation": "BrowseNodeLookup",
                  "BrowseNodeId": int(node_id),
                  "ResponseGroup": "BrowseNodeInfo"}
        response = self.amazon_request(params)
        tries = 0
        while response.status_code != 200:
            response = self.amazon_request(params)
            tries += 1
            if tries > 5:
                return "Too many tries"

        dict = xmltodict.parse(response.text)
        dict = json.dumps(dict)
        dict = json.loads(dict)

        request = dict['BrowseNodeLookupResponse']['BrowseNodes']['Request']
        error_code = request.get("Errors",{}).get("Error",{}).get("Code", None)
        if error_code:
            return error_code

        try:
            return dict['BrowseNodeLookupResponse']['BrowseNodes']['BrowseNode']
        except:
            print "error"

    def item_search_full_url(self, node_id, brand=None, page=1, doAuth=True):
        params = {"Service": "AWSECommerceService",
                  "Operation": "ItemSearch",
                  "BrowseNode": node_id,
                  "ResponseGroup": ','.join(['ItemAttributes','Reviews', 'BrowseNodes','Images','ItemIds', 'SalesRank']),
                  "SearchIndex" : 'Electronics',
                  "Sort" : 'salesrank',
                  "ItemPage" : page
            }
        if brand:
            params['Brand'] = brand

        url, allparams = self.generate_amazon_url_and_load_params(params, doAuth)
        data = urlencode(allparams)
        data = data.replace('+', '%20')
        return url + '?' + data

    def have_reviews(self, asins):
        if not asins:
            return
        params = {"Service": "AWSECommerceService",
                  "Operation": "ItemLookup",
                  "ItemId": ','.join(asins),
                  "ResponseGroup": "Reviews"}
        response = self.amazon_request(params)

        tries = 0
        while response.status_code != 200:
            response = self.amazon_request(params)
            tries += 1
            if tries > 5:
                raise Exception("Too many tries: %s" % response.text)

        xml = response.text
        xml = xml.replace(' xmlns=', ' xmlnamespace=')
        f = StringIO.StringIO(xml)
        tree = etree.parse(f)

        try:
            request = tree.xpath("//ItemLookupResponse/Items/Request")[0]
        except IndexError:
            raise Exception('Invalid Response: %s' % xml)

        errors = request.xpath(".//Errors/Error")
        return_dict = {'asins': {},
                       'invalid_asins': [],
                       'errors': {}}
        error_dict = {}
        for error in errors:
            error_code = error.xpath("./Code")[0].text
            error_message = error.xpath(".//Message")[0].text
            if error_code=='AWS.InvalidParameterValue':
                invalid_asin_re = "^([\w]+) is not a valid value for ItemId"
                match = re.search(invalid_asin_re, error_message)
                if match:
                    return_dict['invalid_asins'].append(match.group(1))
                else:
                    error_dict[error_code] = error_message
        if error_dict:
            return_dict['errors'] = error_dict

        items = request.xpath('//ItemLookupResponse/Items/Item')
        item_dict = {}
        for item in items:
            asin = item.xpath(".//ASIN")[0].text
            has_reviews = item.xpath('.//CustomerReviews/HasReviews')[0].text
            item_dict[asin] = {'has_reviews': bool(strtobool(has_reviews))}
            parent_asin = item.xpath(".//ParentASIN")
            if parent_asin:
                item_dict[asin]['parent_asin'] = parent_asin[0].text
            else:
                item_dict[asin]['parent_asin'] = None
        return_dict['asins'] = item_dict
        return return_dict
