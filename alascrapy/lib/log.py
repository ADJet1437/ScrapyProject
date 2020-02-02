import logging
from scrapy import logformatter
from traceback import format_exc

def log_exception(logger, exception):
    logger.error("%s\n%s" % (str(exception), format_exc()))


class PoliteLogFormatter(logformatter.LogFormatter):
    def dropped(self, item, exception, response, spider):
        return {
           'level': logging.INFO,
           'msg': logformatter.DROPPEDMSG,
           'args': {
              'exception': exception,
              'item': item,
           }
        }


class FakeUserAgentFilter(logging.Filter):
    def filter(self, record):
        if "fallback" in record.getMessage():
            return False
        return True
