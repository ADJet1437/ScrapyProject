import os
import re
from scrapy.utils.httpobj import urlparse_cached
from six.moves.urllib.request import getproxies, proxy_bypass


def use_vpn_only(host, domains):
    """
    Check if we should only use VPN proxy for a host
    :param host: the host to check
    :param domains: a list of domains that we should only visit using vpn proxy, separated by commas
    :return: True if only VPN proxy should be used for the host, False otherwise 
    """

    vpn_only_list = [domain.strip() for domain in domains.split(',')]
    for name in vpn_only_list:
        if name:
            name = re.escape(name)
            pattern = r'(.+\.)?{}$'.format(name)
            if re.match(pattern, host, re.I):
                return True

    return False


class ProxyMiddleware(object):

    http_index = 0
    https_index = 0

    # overwrite process request
    def process_request(self, request, spider):
        # Set the location of the proxy

        use_vpn = False
        parsed = urlparse_cached(request)
        scheme = parsed.scheme

        # 'no_proxy' is only supported by http schemes
        if scheme in ('http', 'https'):
            if proxy_bypass(parsed.hostname):
                return
            use_vpn = use_vpn_only(parsed.hostname, spider.vpn_only)

        if 'http://' == request.url[0:7]:
            if use_vpn:
                request.meta['proxy'] = 'http://' + spider.vpn_proxy
            else:
                self.http_index = divmod(self.http_index+1,
                                    len(spider.http_proxy))[1]

                http_proxy = spider.http_proxy[self.http_index]
                request.meta['proxy'] = http_proxy

        if spider.crawlera_enabled:
            return

        elif 'https://' == request.url[0:8]:
            if use_vpn:
                request.meta['proxy'] = 'https://' + spider.vpn_proxy
            else:
                self.https_index = divmod(self.https_index+1,
                                     len(spider.https_proxy))[1]

                https_proxy = spider.https_proxy[self.https_index]
                request.meta['proxy'] = https_proxy
