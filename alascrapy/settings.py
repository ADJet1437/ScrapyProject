# -*- coding: utf-8 -*-

# Scrapy settings for alascraper project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'alascrapy'

SPIDER_MODULES = ['alascrapy.spiders']
NEWSPIDER_MODULE = 'alascrapy.spiders'
COOKIES_ENABLED = False
RETRY_TIMES = 20 #8 tor processes in round robin
LOG_LEVEL='INFO'

DOWNLOAD_DELAY = 1.5

CRAWLERA_PRESERVE_DELAY = True
AUTOTHROTTLE_ENABLED = False
CONCURRENT_REQUESTS_PER_IP = 10
CONCURRENT_REQUESTS = 10
CRAWLERA_APIKEY = '54028e8d49cf458b8701ef5e0d96ab65'

DOWNLOADER_MIDDLEWARES = {
    'alascrapy.middleware.canonical_link_check_middleware.CanonicalLinkCheckMiddleware': 50,
    'alascrapy.middleware.forbidden_requests_middleware.ForbiddenRequestsMiddleware': 80,
    'alascrapy.middleware.proxy_middleware.ProxyMiddleware': 111,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 115,
    # 'alascrapy.middleware.user_agent_middleware.RotateUserAgentMiddleware': 120,
    'alascrapy.middleware.redirect_middleware.ConfigurableRedirectMiddleware': 130,
    'alascrapy.middleware.offsite_middleware.OffsiteMiddleware': 135,
    'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': None,
    'alascrapy.middleware.amazon_auth_middleware.AmazonAuthMiddleware': 140,
    'scrapy_crawlera.CrawleraMiddleware': 150,
}

ITEM_PIPELINES = {
    'alascrapy.pipelines.amazon_review_pipeline.AmazonReviewPipeline': 90,
    'alascrapy.pipelines.additional_values_pipeline.AdditionalValuesPipeline': 100,
    'alascrapy.pipelines.categories_pipeline.CategoriesPipeline': 200,
    'alascrapy.pipelines.validate_pipeline.ValidatePipeline': 800,
    'alascrapy.pipelines.mysql_pipeline.MySQLDBPipeline': 900,
    'alascrapy.pipelines.csv_pipeline.CsvSavePipeline': 950,
    'alascrapy.pipelines.summary_pipeline.SummayLogPipeline': 1000
}

DOWNLOAD_HANDLERS = {'s3': None}
LOG_FORMATTER = 'alascrapy.lib.log.PoliteLogFormatter'

SPIDER_MIDDLEWARES = {
    'alascrapy.middleware.limit_requests_middleware.LimitRequestsMiddleware':
        1000
}

FEED_EXPORTERS = {
    'csv': 'alascrapy.exporters.csv_item_exporter.CSVItemExporter',
}
# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:35.0) Gecko/20100101 Firefox/35.0'

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
HTTPCACHE_ENABLED = False
HTTPCACHE_EXPIRATION_SECS = 604800
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = [403, 500, 503, 404]
HTTPCACHE_GZIP = True
HTTPCACHE_MONGO_HOST= 'mongodb://mongocache901.office.alatest.se'
HTTPCACHE_MONGO_PORT= 27017
HTTPCACHE_MONGO_DATABASE= 'scrapy'
HTTPCACHE_MONGO_USERNAME='scrapy'
HTTPCACHE_MONGO_PASSWORD='scrapy.att.60'
HTTPCACHE_STORAGE = 'alascrapy.lib.httpcache.MongoCacheStorage'
HTTPCACHE_SHARDED = True
