# -*- coding: utf-8 -*-
import re
import sys
import json
import scheduler_dao
import logging
import graypy

from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
from traceback import format_tb

from alascrapy.lib.exceptions import InvalidConfiguration
from alascrapy.lib.mq.mq_publisher import MQPublisher
from alascrapy.lib.mysql_manager import MysqlManager
from alascrapy.lib.dao.incremental_scraping import is_product_in_db_by_sii


time_regex = re.compile('^(\d+,)*\d+$')

class AllMatch(set):
    """Universal set - match everything"""
    def __contains__(self, item): return True


class Scheduler():

    amazon_review_spiders = {39000015: 'amazon_it_reviews',
                             230492: 'amazon_com_reviews',
                             263862: 'amazon_de_reviews',
                             263863: 'amazon_fr_reviews',
                             1: 'amazon_uk_reviews'}


    def setup_logger(self):
        """Setups logger for the spider

            Arguments:
            project_conf -- ConfigParser Object that contains
                            the configuration data in conf/alascrapy.conf
        """
        LOG_FORMAT = "alaScrapy Schedulers: %(asctime)s %(levelname)s [%(" \
                     "name)s] %(message)s"
        DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

        logging.basicConfig(format=LOG_FORMAT, datefmt=DATE_FORMAT)

        graylog_host = self.project_conf.get("LOGGING", "graylog_host")
        graylog_port = self.project_conf.getint("LOGGING", "graylog_port")
        graylog = graypy.GELFHandler(graylog_host, graylog_port)
        graylog.setLevel(logging.INFO)

        file_handler = logging.handlers.TimedRotatingFileHandler(
            "/var/log/alaScrapy/scheduler.log",'midnight',10)
        file_handler.suffix = "%Y-%m-%d"
        file_handler.setLevel(logging.INFO)

        #TODO: separate the logger name so we can separate spider messages
        #from scheduler messages to a different stream
        self.logger = logging.getLogger('alascrapy_scheduler')
        self.logger.addHandler(graylog)
        self.logger.addHandler(file_handler)
        sys.excepthook = self.log_uncaught_exception

    def log_uncaught_exception(self, exctype, value, tb):
        self.logger.critical("Uncaught Exception %s: %s.\nTraceback:\n%s" %
                       (exctype.__name__, value, "".join(format_tb(tb))))

    def __init__(self, project_conf):
        self.project_conf = project_conf
        self.setup_logger()
        self.mysql_manager = MysqlManager(project_conf, self.logger)
        self.mq_publisher = MQPublisher(project_conf, "SCHEDULER")

    def parse_to_set(self, key, scheduled_spider):
        if self.is_time_valid(scheduled_spider[key], time_regex):
            if scheduled_spider[key]!= None:
                return set([int(k) for k in scheduled_spider[key].split(',')])
            else:
                return AllMatch()
        else:
            raise InvalidConfiguration(
                """Invalid schedule in spider %s: Invalid time string %s in field %s""" %
                (scheduled_spider['spider_name'], scheduled_spider[key], key) )

    def is_time_valid(self, time_string, regex):
        if time_string:
            match = re.match(regex, time_string)
            if match:
                return True
            return False
        else:
            return True

    def schedule_amazon_reviews(self):
        publisher = self.mq_publisher
        exchange = self.project_conf.get("SCHEDULER", "exchange")
        amazon_reviews_queue = self.project_conf.get("SCHEDULER",
                                                       "amazon_review_spider_queue")
        amazon_routing_key =  self.project_conf.get("SCHEDULER",
                                                    "amazon_review_routing_key")

        publisher._channel.queue_declare(queue=amazon_reviews_queue,
                                         durable=True, exclusive=False,
                                         auto_delete=False)
        publisher._channel.queue_bind(queue=amazon_reviews_queue,
                                      exchange=exchange,
                                      routing_key=amazon_routing_key)

        for source_id in self.amazon_review_spiders:
            missing_asins_frames = []
            asins_queue = "amazon_reviews_%s" % source_id
            spider_name = self.amazon_review_spiders[source_id]
            publisher._channel.queue_declare(queue=asins_queue, durable=True,
                                            exclusive=False, auto_delete=False)
            publisher._channel.queue_bind(queue=asins_queue,
                                         exchange=exchange,
                                         routing_key=str(source_id))
            while True:
                asin_method_frame, asin_properties, asin_body = \
                    publisher._channel.basic_get(asins_queue)

                if asin_method_frame and asin_properties and asin_body:
                    asin_body = json.loads(asin_body)
                    asin = asin_body['asin']
                    if not is_product_in_db_by_sii(self.mysql_manager, source_id, asin):
                        missing_asins_frames.append(asin_method_frame)
                        continue
                    publisher._channel.basic_ack(delivery_tag=asin_method_frame.delivery_tag)
                    message = {'spider': spider_name,
                               'parameters': {'asin': asin}}
                    publisher.publish_message(message, exchange, amazon_routing_key)
                else:
                    break

            for frame in missing_asins_frames:
                publisher._channel.basic_nack(delivery_tag=frame.delivery_tag)


    def should_execute(self, time, scheduled_spider):
        #print str(time.hour)+' '+str(scheduled_spider['hours'])
        #print str(time.day)+' '+str(scheduled_spider['days_of_month'])
        #print str(time.month)+' '+str(scheduled_spider['months'])
        #print str(time.weekday())+' '+str(scheduled_spider['days_of_week'])

        #print (time.hour      in scheduled_spider['hours'])
        #print (time.day       in scheduled_spider['days_of_month'])
        #print (time.month     in scheduled_spider['months'])
        #print (time.weekday() in scheduled_spider['days_of_week'])

        return ((time.hour       in scheduled_spider['hours']) and
                (time.day        in scheduled_spider['days_of_month']) and
                (time.month      in scheduled_spider['months']) and
                (time.weekday()  in scheduled_spider['days_of_week']))

    def run_scheduler(self):
        time = datetime(*datetime.now().timetuple()[:5])
        schedules = scheduler_dao.get_schedules(self.mysql_manager)
        if not schedules:
            message = "No scheduled spiders found for execution. Verify if the " \
                      "field enabled is set to True in table 'alascrapy.schedules'"
            self.logger.info(message)
            return

        for schedule in schedules:
            try:
                schedule['hours'] = self.parse_to_set('hours', schedule)
                schedule['days_of_week'] = self.parse_to_set('days_of_week',schedule)
                schedule['days_of_month'] = self.parse_to_set('days_of_month', schedule)
                schedule['months'] = self.parse_to_set('months', schedule)
            except InvalidConfiguration as e:
                continue

            if self.should_execute(time, schedule):
                self.send_scheduler_mq(schedule)

        self.schedule_amazon_reviews()
        self.close_scheduler()

    def send_scheduler_mq(self, schedule):
        exchange = self.project_conf.get("SCHEDULER", "exchange")
        routing_key = self.project_conf.get("SCHEDULER", "spider_routing_key")

        param_list = scheduler_dao.get_schedule_params(self.mysql_manager,
                                                       schedule["id"])
        param_dict = {}
        for param in param_list:
            param_dict[param['parameter']] = param['parameter_value']
        message = {'spider': schedule['spider_name'],
                   'parameters': param_dict}
        self.mq_publisher.publish_message(message, exchange, routing_key)

    def close_scheduler(self):
        self.mq_publisher.close_connection()
