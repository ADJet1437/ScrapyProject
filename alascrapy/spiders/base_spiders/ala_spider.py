# -*- coding: utf-8 -*-
from Queue import Queue, Empty
from traceback import format_tb
from logging.handlers import TimedRotatingFileHandler
import logging
import sys
import os
from datetime import datetime

from scrapy import Spider
from scrapy import signals
from scrapy.selector import Selector
from scrapy.http.request import Request
from scrapy.exceptions import CloseSpider
import graypy

from alascrapy.lib.mysql_manager import MysqlManager
from alascrapy.lib.conf import get_project_conf, get_source_conf
from alascrapy.lib.generic import strip, parse_float, normalize_price, get_full_url, remove_prefix
from alascrapy.lib.log import FakeUserAgentFilter
from alascrapy.items import ProductItem, CategoryItem, ReviewItem, ProductIdItem


class AlaSpider(Spider):
    crawlera_enabled = False

    def __init__(self, *a, **kw):
        super(AlaSpider, self).__init__(self.name, **kw)
        self.project_conf = get_project_conf()
        self.setup_logger()
        self.setup_logger_for_each_spider()
        self.spider_conf = get_source_conf(self.name)
        self.mysql_manager = MysqlManager(self.project_conf, self._logger)
        self.set_proxy()
        self.skip_categories = []
        self.active_sel_requests = 0
        self.active_browsers = 0
        self.request_queue = Queue()
        self.queue_sizes = []
        self.input_start_url = kw.get('start_url', None)
        self.parse_function_name = kw.get('parse_function', None)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = cls(*args, **kwargs)
        db_output_enabled = spider.project_conf.getboolean("OUTPUT",
                                                           'db_output_enabled')
        csv_output_enabled = spider.project_conf.getboolean("OUTPUT",
                                                            'csv_output_enabled')
        settings = crawler.settings
        if not db_output_enabled:
            mysql_pipeline_module = \
                "alascrapy.pipelines.mysql_pipeline.MySQLDBPipeline"
            settings['ITEM_PIPELINES'].pop(mysql_pipeline_module, None)

        if not csv_output_enabled:
            csv_pipeline_module = \
                "alascrapy.pipelines.csv_pipeline.CsvSavePipeline"
            settings['ITEM_PIPELINES'].pop(csv_pipeline_module, None)

        # Do not use proxy and rotate user-agent string when cookies are enabled
        if settings.get('COOKIES_ENABLED', False):
            proxy_middleware_module = \
                'alascrapy.middleware.proxy_middleware.ProxyMiddleware'
            http_proxy_middleware_module = \
                'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware'
            rotate_useragent_middleware_module = \
                'alascrapy.middleware.user_agent_middleware.RotateUserAgentMiddleware'

            # Not sure why pop() throws KeyError if the setting does not exist,
            # Scrapy needs to fix this
            if proxy_middleware_module in settings['DOWNLOADER_MIDDLEWARES']:
                settings['DOWNLOADER_MIDDLEWARES'].pop(
                    proxy_middleware_module, None)
            if http_proxy_middleware_module in settings['DOWNLOADER_MIDDLEWARES']:
                settings['DOWNLOADER_MIDDLEWARES'].pop(
                    http_proxy_middleware_module, None)
            if rotate_useragent_middleware_module in settings['DOWNLOADER_MIDDLEWARES']:
                settings['DOWNLOADER_MIDDLEWARES'].pop(
                    rotate_useragent_middleware_module, None)

        crawler.settings = settings
        crawler.signals.connect(spider._send_queued_requests,
                                signal=signals.spider_idle)
        spider._set_crawler(crawler)
        spider.max_sel_requests = settings.getint('MAX_SELENIUM_REQUESTS', 4)
        spider.max_retry_times = settings.getint('RETRY_TIMES', 8)
        return spider

    def start_requests(self):
        if self.input_start_url and self.parse_function_name:
            input_parse_function = getattr(self, self.parse_function_name)
            yield Request(url=self.input_start_url,
                          callback=input_parse_function)
        else:
            for url in self.start_urls:
                yield Request(url=url, callback=self.parse)

    def get_temp_dir(self):
        tmp_dir = self.project_conf.get('RUN', 'tmp_dir')
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)
        return tmp_dir

    def get_spider_log_dir(self):
        base_log_dir = self.project_conf.get('LOGGING', 'base_log_dir')
        sort_by_date = datetime.strftime(datetime.today(), '%Y-%m-%d')
        sort_by_spider = self.name

        date_dir = '{}/{}'.format(base_log_dir, sort_by_date)
        if not os.path.exists(date_dir):
            os.makedirs(date_dir)
        log_dir = '{}/{}'.format(date_dir, sort_by_spider)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        return log_dir

    def errback(self, failure):
        self.logger.error(repr(failure))

    def _selenium_error(self, failure):
        """
        Something went wrong while downloading a selenium_request.
        We do not really care what, but we must decrease
        the active requests number.
        :param failure:
        :return:
        """
        self.active_sel_requests -= 1

    def selenium_request(self, url, callback):
        request = Request(url, callback=callback, errback=self._selenium_error)
        request.meta['uses_selenium'] = True
        return request

    def _send_queued_requests(self):
        """
        This is an awful hack. But as of scrapy 1.0.1 there is no way to
        schedule a request from the signal handler that allow requests to
        go through spider middlewares. Also engine API is still considered
        unstable, so this can break after an update to scrapy.

        It is called after spider_idle signal is sent and it's purpose is to
        start resending the queued requests. Only schedules a dummy call
        to the _remaning_requests callback which will yield the right requests.
        :return:
        """
        if not self.request_queue.empty():
            request = Request(self.start_urls[0],
                              callback=self._remaining_requests,
                              dont_filter=True)
            status = {'active_sel_request': self.active_sel_requests,
                      'active_browsers': self.active_browsers,
                      'queue_size': self.request_queue.qsize()}
            self.queue_sizes.append(self.request_queue.qsize())
            if len(self.queue_sizes) > 3:
                same_queue_size = False
                if self.queue_sizes[-1] == self.queue_sizes[-2] and \
                   self.queue_sizes[-2] == self.queue_sizes[-3]:
                    same_queue_size == True

                if same_queue_size:
                    request.meta["quit"] = True

            self._logger.info(
                "Sending dummy request to send queued requests. \nStatus: %s" % str(status))
            self.crawler.engine.crawl(request, self)

    def set_proxy(self):
        self.vpn_proxy = self.project_conf.get('PROXY', 'vpn_proxy')
        self.default_proxy = self.vpn_proxy

        self.http_proxy = self.project_conf.get(
            'PROXY', 'http_proxy').split(',')
        self.https_proxy = self.project_conf.get(
            'PROXY', 'https_proxy').split(',')
        self.no_proxy = self.project_conf.get('PROXY', 'no_proxy')
        self.vpn_only = self.project_conf.get('PROXY', 'vpn_only')

        # os.environ['http_proxy'] = self.http_proxy
        # os.environ['https_proxy'] = self.https_proxy
        os.environ['no_proxy'] = self.no_proxy
        # os.environ['HTTP_PROXY'] = self.http_proxy
        # os.environ['HTTPS_PROXY'] = self.https_proxy
        os.environ['NO_PROXY'] = self.no_proxy

    def _remaining_requests(self, response):
        """
        Callback that sends queued requests.

        :param response:
        :return:
        """
        quit = response.meta.get("quit", False)
        if quit:
            self.quit(message="Spider is stuck. Quiting now")

        if self.active_sel_requests >= self.max_sel_requests or self.active_sel_requests < 0:
            # TODO: If it enters here the active_sel_requests count is wrong!!
            # I give up. Do not know why maybe errback was not called or the
            # dupefilter middleware executed after limit_request_middleware
            # or maybe something else. (The latter most likely because I
            # tested the other ones)
            # I could not find the mistake to I am fixing the counter now so
            # we can continue scraping. The less than zero case has not
            # happened but there just in case...
            # Such hack. Very Sorry. wow :(.
            #
            # Do not try to fix this by using the amount of browsers.
            # by the time the number of browsers is incremented scrapy already
            # sent many requests that create browsers and hell will break loose.
            # A day may come when active_sel_requests works as expected.
            # But it will not be this day.

            if self.active_sel_requests != self.active_browsers:
                self.active_sel_requests = self.active_browsers

        if self.active_sel_requests < self.max_sel_requests:
            for i in range(self.max_sel_requests-self.active_sel_requests):
                try:
                    request = self.request_queue.get_nowait()
                    yield request
                except Empty:
                    break

    def _retry(self, request):
        retries = request.meta.get('as_retry_times', 0) + 1
        url = request.url
        redirect_urls = request.meta.get('redirect_urls', [])
        try:
            url = redirect_urls[0]
        except IndexError:
            pass

        if retries <= self.max_retry_times:
            self.logger.debug("Retrying %(request)s (failed %(retries)d times)",
                              {'request': request, 'retries': retries},
                              extra={'spider': self})
            retryreq = request.replace(url=url,
                                       priority=-1*retries)
            retryreq.meta['as_retry_times'] = retries
            retryreq.dont_filter = True
            return retryreq
        else:
            self.logger.info("Forbidden! Gave up retrying %(request)s (failed %(retries)d times)",
                             {'request': request, 'retries': retries},
                             extra={'spider': self})
            return None

    def quit(self, message="Abnormal closing of spider", send_mq=True):
        if send_mq == True:
            self.project_conf.set('OUTPUT', 'send_mq_request', str(send_mq))
        raise CloseSpider(message)

    def setup_logger(self):
        """Setups logger for the spider

            Arguments:
            project_conf -- ConfigParser Object that contains
                            the configuration data in conf/alascrapy.conf
        """
        LOG_FORMAT = self.name + \
            ": %(asctime)s %(levelname)s [%(name)s] %(message)s"
        DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

        logging.basicConfig(format=LOG_FORMAT, datefmt=DATE_FORMAT)

        graylog_host = self.project_conf.get("LOGGING", "graylog_host")
        graylog_port = self.project_conf.getint("LOGGING", "graylog_port")
        graylog = graypy.GELFHandler(graylog_host, graylog_port)
        graylog.setLevel(logging.INFO)
        file_handler = logging.handlers.TimedRotatingFileHandler(
            "/var/log/alaScrapy/spiders.log", when='midnight', backupCount=10)
        file_handler.suffix = "%Y-%m-%d"
        file_handler.setLevel(logging.INFO)
        # TODO: separate the logger name so we can separate spider messages
        # from scheduler messages to a different stream
        self._logger = logging.getLogger('')  # get root logger

        self._logger.addHandler(graylog)
        self._logger.addHandler(file_handler)

        sys.excepthook = self.log_uncaught_exception

        # suppress expected 'error messages' when using fake user agent
        fu_logger = logging.getLogger('fake_useragent')
        fu_logger.addFilter(FakeUserAgentFilter())

    def setup_logger_for_each_spider(self):
        LOG_FORMAT = self.name + \
            ": %(asctime)s %(levelname)s [%(name)s] %(message)s"
        DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
        logging.basicConfig(format=LOG_FORMAT, datefmt=DATE_FORMAT)

        log_dir = self.get_spider_log_dir()

        file_handler = logging.handlers.RotatingFileHandler(
            filename="{}/{}.log".format(log_dir, self.name), mode='a')
        file_handler.setLevel(logging.INFO)
        self._logger = logging.getLogger('')
        self._logger.addHandler(file_handler)

    def log_uncaught_exception(self, exctype, value, tb):
        self._logger.critical("Uncaught Exception %s: %s.\nTraceback:\n%s" %
                              (exctype.__name__, value, "".join(format_tb(tb))))

    def init_item_by_xpaths(self, response, item_type, fields, selector=None):
        if not selector:
            selector = Selector(response=response)

        if item_type not in ('review', 'product', 'product_id', 'category'):
            raise Exception("Invalid item type: %s" % item_type)

        if item_type == "review":
            item = ReviewItem()
        elif item_type == "product":
            item = ProductItem()
        elif item_type == "product_id":
            item = ProductIdItem()
        elif item_type == "category":
            item = CategoryItem()

        if item_type in ('review', 'product'):
            item["TestUrl"] = response.url

        for field in fields:
            # TODO: maybe check field.
            if item_type == "review" and field in ("TestPros, TestCons"):
                item[field] = self.extract_all(selector.xpath(fields[field]),
                                               " ; ")
            else:
                item[field] = self.extract_all(selector.xpath(fields[field]))
        return item

    def set_product(self, review, product):
        url = review.get('TestUrl', None)
        if not url:
            review['TestUrl'] = product['TestUrl']

        review['source_internal_id'] = product.get("source_internal_id", None)
        review['ProductName'] = product["ProductName"]

    def product_id(self, product, kind='', value=''):
        product_id = ProductIdItem()
        if "source_internal_id" in product:
            product_id['source_internal_id'] = product["source_internal_id"]
        product_id['ProductName'] = product["ProductName"]
        product_id['ID_kind'] = kind
        product_id['ID_value'] = value
        return product_id

    def extract_xpath(self, element, xpath, strip_chars='', strip_unicode=None):
        return self.extract(element.xpath(xpath),
                            strip_chars=strip_chars,
                            strip_unicode=strip_unicode)

    def extract_list_xpath(self, element, xpath, strip_chars='',
                           strip_unicode=None):
        return self.extract_list(element.xpath(xpath),
                                 strip_chars='',
                                 strip_unicode=strip_unicode)

    def extract_all_xpath(self, element, xpath, separator=" ",
                          strip_chars='', strip_unicode=None):
        return self.extract_all(element.xpath(xpath), separator=separator,
                                strip_chars=strip_chars,
                                strip_unicode=strip_unicode)

    # extract functions to prevent [0] and standarize cleaning
    def extract(self, selector_list, strip_chars='', strip_unicode=None):
        for selector in selector_list:
            value = selector.extract()
            value = strip(value, strip_chars=strip_chars,
                          strip_unicode=strip_unicode)
            if value:
                return value
        return ""

    def extract_all(self, selector_list, separator=" ", strip_chars='',
                    strip_unicode=None, keep_whitespace=False):
        extract = selector_list.extract()
        extract = [strip(line, strip_chars=strip_chars,
                         strip_unicode=strip_unicode, keep_whitespace=keep_whitespace) for line in extract]
        return separator.join([line for line in extract if line])

    def extract_list(self, selector_list, strip_chars='', strip_unicode=None, keep_whitespace=False):
        extract = selector_list.extract()
        extract = [strip(line, strip_chars=strip_chars,
                         strip_unicode=strip_unicode, keep_whitespace=keep_whitespace) for line in extract
                   if strip(line, strip_chars=strip_chars,
                            strip_unicode=strip_unicode, keep_whitespace=keep_whitespace)]
        return extract

    def should_skip_category(self, category):
        db_category = self._categories.get(category['category_path'].lower(),
                                           None)
        if db_category:
            return bool(db_category['do_not_load'])
        else:
            return category.get('do_not_load', False)  # We return the value of
            #  the script or default false
