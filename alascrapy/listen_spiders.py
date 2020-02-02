#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import time
import subprocess
import os
import re
from os.path import isfile, join, dirname, realpath
from alascrapy.lib.conf import get_project_conf
from alascrapy.lib.mq.mq_object import MQObject


class SpiderConsumer(MQObject):

    # number of spiders can be run simultaneously when none of them is using Selenium
    max_spiders = 3

    # format: {spider_process1: if_selenium_is_used,
    #          spider_process2: if_selenium_is_used,
    #          ...}
    spider_processes = {}

    def __init__(self, project_conf,  project_path):
        super(SpiderConsumer, self).__init__(project_conf, "SCHEDULER")
        self.project_path = project_path

    def if_use_selenium(self, spider_name):
        '''
        Check if a spider uses Selenium or not by reading its script file.
        Limits: 1. if the spider resides in a file containing multiple spiders,
                   then it will always be marked as a Selenium-using spider
                   if one or more of those spiders use Senlenium
                2. it cannot detect if a spider's base spider uses Selenium or not
                   (currently this is only a problem for cnet_uk)
        :param spider_name: name of the spider
        :return: a Boolean that shows if the spider uses Selenium or not
        '''
        spiders_dir = join(self.project_path, 'spiders')
        spider_name_regex = r'^\s*name\s*=\s*[\'"]{0}[\'"]\s*$'.format(spider_name)
        use_selenium_regex = r'^\s*[^#]*SeleniumBrowser\s*\('
        use_selenium_regex_2 = r'^\s*[^#]*get_award_image_screenshot\s*\('

        # read all spider scripts, find the one containing the spider, and see if Selenium code
        # is used in the file or not
        for root, dirs, files in os.walk(spiders_dir):
            for name in files:
                fpath = os.path.join(root, name)
                ext = os.path.splitext(name)[-1]
                if ext != '.py':
                    continue

                with open(fpath) as f:
                    content = f.read()
                    if not re.search(spider_name_regex, content, re.MULTILINE):
                        continue

                    if (re.search(use_selenium_regex, content, re.MULTILINE) or
                            re.search(use_selenium_regex_2, content, re.MULTILINE)):
                        return True
                    else:
                        return False

        return False

    def execute(self, spider_name, parameters):
        self.logger.info('Executing spider: "%s"' % spider_name)
        os.chdir(self.project_path)
        command = ["scrapy", "crawl"]
        for param_name in parameters:
            command.append("-a")
            command.append("%s=%s" % (param_name,parameters[param_name]))
        command.append(spider_name)
        use_selenium = self.if_use_selenium(spider_name)
        proc = subprocess.Popen(command)
        self.spider_processes[proc] = use_selenium

    def on_message(self, method_frame, header_frame, body):
        if self._connection.is_open:
            message_dict = json.loads(body)

            if isinstance(message_dict, unicode) or isinstance(message_dict, str):
                message_dict = json.loads(message_dict)
                #TODO: patch, remove after the bad messages have been proccessed.

            try:
                spider_name = message_dict["spider"]
                parameters = message_dict["parameters"]
            except Exception, e:
                self.logger.warning("Parsing Error, discarding message: %s" % body)
                self._channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                return

            self._channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            self.execute(spider_name, parameters)
        else:
            self.logger.info('Connection lost. Trying to reconnect')
            self.reconnect()
            self.on_message(method_frame, header_frame, body)

    def run(self):
        spider_queue = self.project_conf.get("SCHEDULER", "spider_queue")
        amazon_queue = self.project_conf.get("SCHEDULER", "amazon_review_spider_queue")
        queues = [spider_queue, amazon_queue]

        while True:
            for queue_name in queues:
                if self._connection.is_open:
                    time.sleep(0.03) #Niceness on CPU usage

                    selenium_running = False
                    finished_spider_processes = []
                    for proc, use_selenium in self.spider_processes.iteritems():
                        # Check if the spider is finished or not
                        if proc.poll() is not None:
                            finished_spider_processes.append(proc)
                        # Check if the spider uses Selenium or not
                        if use_selenium:
                            selenium_running = True

                    for proc in finished_spider_processes:
                        self.spider_processes.pop(proc)

                    # Only run spider when the number of spiders current running is less than
                    # the maximum and none of them uses Selenium
                    if selenium_running or len(self.spider_processes) >= self.max_spiders:
                        continue

                    method_frame, properties, body = self._channel.basic_get(queue_name)
                    if method_frame and properties and body:
                        self.logger.info('Message received: "%s"' % body)
                        self.on_message(method_frame, properties, body)
                else:
                    self.logger.info('Connection lost. Trying to reconnect')
                    self.reconnect()


def main():
    path = dirname(realpath(__file__))
    project_conf = get_project_conf()
    consumer = SpiderConsumer(project_conf, path)
    consumer.run()

if __name__ == '__main__':
    main()
