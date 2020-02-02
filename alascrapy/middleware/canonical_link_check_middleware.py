from urlparse import urlparse

import scrapy.exceptions


# parse both canonical_link and response.url, ignore the response
# if they do not share the same host name
class CanonicalLinkCheckMiddleware(object):

    def process_response(self, request, response, spider):
        canonical_link_xpath = "//link[@rel='canonical']/@href"
        canonical_link = spider.extract(response.xpath(canonical_link_xpath))

        if not canonical_link:
            return response

        parsed_canonical_link = urlparse(canonical_link)

        # The canonical link is not a full url. It should have
        # the same host name as response.url
        if not parsed_canonical_link.hostname:
            return response

        canonical_link_host = parsed_canonical_link.hostname
        response_url_host = urlparse(response.url).hostname

        if canonical_link_host != response_url_host:
            raise scrapy.exceptions.IgnoreRequest()

        return response
