from logging.handlers import TimedRotatingFileHandler

import pika
import sys
import logging
import graypy

from traceback import format_tb

class MQObject(object):

    def __init__(self, project_conf, section):
        """Setup the mq publisher object, passing in the configurations we will use
        to connect to RabbitMQ.

        :param ConfigParser project_conf: The configuration parameters of the project.
        :param str section: The section in project_conf where to find the connection details to RabbitMQ.

        """

        self._connection = None
        self._channel = None

        self.project_conf= project_conf
        self.conf_section = section
        self.setup_logger()
        self.username = project_conf.get(section, "username")
        self.password = project_conf.get(section, "password")
        self.mq_host = project_conf.get(section, "host")
        self.mq_virtual_host = project_conf.get(section, "virtual_host")

        credsecurity = pika.PlainCredentials(self.username, self.password)

        parameters = pika.ConnectionParameters(
                        host=self.mq_host,
                        virtual_host=self.mq_virtual_host,
                        credentials=credsecurity)

        self._connection = pika.BlockingConnection(parameters)
        self._channel = self._connection.channel()
        self.logger.info('Connection opened')


    def setup_logger(self):
        """Setups logger for the spider

            Arguments:
            project_conf -- ConfigParser Object that contains
                            the configuration data in conf/alascrapy.conf
        """
        LOG_FORMAT = "alaScrapy MQ: %(asctime)s %(levelname)s [%(" \
                     "name)s] %(message)s"
        DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

        logging.basicConfig(format=LOG_FORMAT, datefmt=DATE_FORMAT)

        graylog_host = self.project_conf.get("LOGGING", "graylog_host")
        graylog_port = self.project_conf.getint("LOGGING", "graylog_port")
        graylog = graypy.GELFHandler(graylog_host, graylog_port)
        graylog.setLevel(logging.INFO)
        #TODO: separate the logger name so we can separate spider messages
        #from scheduler messages to a different stream
        file_handler = logging.handlers.TimedRotatingFileHandler(
            "/var/log/alaScrapy/mq.log",'midnight',10)
        file_handler.suffix = "%Y-%m-%d"
        file_handler.setLevel(logging.INFO)

        self.logger = logging.getLogger('alascrapy_mq')
        self.logger.addHandler(graylog)
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.INFO)
        sys.excepthook = self.log_uncaught_exception

    def log_uncaught_exception(self, exctype, value, tb):
        self.logger.critical("Uncaught Exception %s: %s.\nTraceback:\n%s" %
                       (exctype.__name__, value, "".join(format_tb(tb))))

    def reconnect(self): #TODO: Has given errors. Should refactor...
        self._connection.connect()
        self.logger.info('Reconnection successful')

    def close_connection(self):
        """This method closes the connection to RabbitMQ."""
        self._connection.close()
        self.logger.info('Closed connection')