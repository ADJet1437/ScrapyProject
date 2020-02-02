from scrapy.downloadermiddlewares.redirect import RedirectMiddleware


class ConfigurableRedirectMiddleware(RedirectMiddleware):
    """Handle redirection of requests based on response status and meta-refresh html tag"""

    def process_response(self, request, response, spider):
        spider_conf = spider.spider_conf

        if "allow_redirects" in spider_conf:
            allow_redirects = spider_conf['allow_redirects']
            if not allow_redirects:
                return response

        return super(ConfigurableRedirectMiddleware,self).process_response(request, response, spider)