#!/usr/bin/python
#-*-coding:utf-8-*-
import urlparse
from urllib import urlencode

from alascrapy.lib.generic import remove_prefix
from alascrapy.spiders.base_spiders.amazon_API_spider import AmazonAPISpider


class AmazonAuthMiddleware(object):
    def __init__(self):
        pass

    def process_request(self, request, spider):
        if isinstance(spider, AmazonAPISpider) and spider.endpoint in request.url and (not 'Signature' in request.url):
            # spider.logger.info('Original url : ' + request.url)
            source_key = spider.source_key
            parsed = urlparse.urlparse(request.url)
            params = urlparse.parse_qs(parsed.query)
            # urlparse.parse_qs returns lists as values, we extract the first item of list to simplify
            for k,v in params.iteritems():
                params[k] = v[0] if len(v) == 1 else None
            uri = parsed.path
            # print('params in middleware :')
            # print(str(params))
            paramsWithAuth = spider.amazon_apis[source_key].doAuth(params, uri)
            paramsString = urlencode(paramsWithAuth, doseq=True)
            newParsed = parsed._replace(query = paramsString)
            newReq = request.replace(url=urlparse.urlunparse(newParsed))
            return newReq