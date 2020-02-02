#!/usr/bin/env python
import requests
import hmac
import hashlib
import json
from urllib import urlencode
from time import strftime, gmtime, sleep
from base64 import b64encode
from collections import OrderedDict
import sys

import xmltodict

from alascrapy.lib.amazon_graph import CategoryTree

sys.setrecursionlimit(10000)

visited = []

countries = {
    'uk': {'start_nodes': [560800, 1025616,  340832031, 391784011],
           'endpoint': 'webservices.amazon.co.uk'},
    'it': {'start_nodes': [425917031, 412610031,  412604031, 602473031, 602473031],
           'endpoint': 'webservices.amazon.it'},
    'fr': {'start_nodes': [908827031, 340859031,  235571011, 235560011],
           'endpoint': 'webservices.amazon.fr'},
    'de': {'start_nodes': [368179031, 569604,  541708, 3169211, 571860],
           'endpoint': 'webservices.amazon.de'}
}


def amazon_request(params, country):
    endpoint = countries[country]['endpoint']
    uri = "/onca/xml"
    secret_key = "1RFwtwfJeqi6fTzO/hxmf+J9E8Nfai2rHWSwy6xu"
    params["Timestamp"] = strftime("%Y-%m-%dT%H:%M:%S.000Z", gmtime())
    params = OrderedDict(sorted(params.items(), key=lambda t: t[0]))
    canonical_query_string=urlencode(params, doseq=True)
    string_to_sign = "GET\n%s\n%s\n%s" % (endpoint, uri, canonical_query_string)
    _hash = hmac.new(secret_key, string_to_sign, hashlib.sha256)
    signature = b64encode(_hash.digest())
    params['Signature']=signature
    return requests.get("http://%s%s" % (endpoint, uri), params=params)

def get_node_request(node_id, country):
    params = {"Service": "AWSECommerceService",
              "Operation": "BrowseNodeLookup",
              "AWSAccessKeyId": "0EWA6R5AGNW9AA6JF8R2",
              "AssociateTag": "alatestcouk0e-21",
              "BrowseNodeId": node_id,
              "ResponseGroup": "BrowseNodeInfo"}
    return amazon_request(params, country)

def extract_children(neo_graph, browse_node, node_category, country):
    children = browse_node.get("Children", None)
    if children:
        if type(children['BrowseNode']) is dict:
            child_id = children['BrowseNode']["BrowseNodeId"]
            child_cat = neo_graph.merge_node(children['BrowseNode'], country)
            relationship = neo_graph.relationship(node_category, child_cat)
            neo_graph.create_relationship(relationship)
            request_node(child_id, country)
        elif type(children['BrowseNode']) is list:
            for child in children['BrowseNode']:
                child_id = child["BrowseNodeId"]
                child_cat = neo_graph.merge_node(child, country)
                relationship = neo_graph.relationship(node_category, child_cat)
                neo_graph.create_relationship(relationship)
                request_node(child_id, country)
             
def parse_node(neo_graph, browse_node, country,
               parent_cat=None, child_cat=None):
    # browse_node expected format
    #{u'Ancestors': {u'BrowseNode': {u'Ancestors': {u'BrowseNode': {u'BrowseNodeId': u'560798',
    #                                                               u'Name': u'Electronics & Photo'}},
    #                                u'BrowseNodeId': u'560800',
    #                                u'IsCategoryRoot': u'1',
    #                                u'Name': u'Categories'}},
    # u'BrowseNodeId': u'1340509031',
    # u'Children': {u'BrowseNode': [{u'BrowseNodeId': u'560826',
    #                                u'Name': u'Accessories'},
    #                               {u'BrowseNodeId': u'2829144031',
    #                                u'Name': u'Big Button Mobile Phones'},
    #                              {u'BrowseNodeId': u'430574031',
    #                               u'Name': u'Mobile Broadband'},
    #                              {u'BrowseNodeId': u'5362060031',
    #                               u'Name': u'Mobile Phones & Smartphones'},
    #                              {u'BrowseNodeId': u'213005031',
    #                               u'Name': u'SIM Cards'},
    #                              {u'BrowseNodeId': u'3457450031',
    #                               u'Name': u'Smartwatches'}]},
    # u'Name': u'Mobile Phones & Communication'}

    category = neo_graph.merge_node(browse_node, country)
    extract_children(neo_graph, browse_node, category, country)

def parse_category_tree(xml_string, country):
    neo_graph = CategoryTree(country)
    dict = xmltodict.parse(xml_string)
    dict = json.dumps(dict)
    dict = json.loads(dict)
    browse_node = dict['BrowseNodeLookupResponse']['BrowseNodes']['BrowseNode']
    parse_node(neo_graph, browse_node, country)


def request_node(node_id, country):
    print "Requesting: %d" % int(node_id)
    if node_id not in visited:
        response = get_node_request(int(node_id), country)
        visited.append(node_id)
        parse_category_tree(response.text, country)
        sleep(1)

def main():
    for country in countries:
        if country=='de':
            for node in countries[country]['start_nodes']:
                request_node(node, country)

if __name__ == "__main__":
    main()
