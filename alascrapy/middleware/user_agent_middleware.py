#!/usr/bin/python
#-*-coding:utf-8-*-

from fake_useragent import UserAgent
from fake_useragent import settings
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from os.path import getmtime, dirname, join
from shutil import copyfile
import sys
import time
import json

class RotateUserAgentMiddleware(UserAgentMiddleware):

    def __init__(self, user_agent=''):
        self.user_agent = user_agent
        self.ua = UserAgent(fallback=self.user_agent)
        cache_file = settings.DB

        ONEDAY_DELTA = 86400
        now = time.time()

        cache_age = 0
        try:
            cache_age = getmtime(cache_file)
        except OSError:
            pass

        if cache_age <= now - ONEDAY_DELTA:
            self.ua.update()

        with open(cache_file, mode='rb') as fp:
            browser_data = json.load(fp)
            test = browser_data.get('browsers', {}).get('chrome', [])
            if not test:
                d = dirname(sys.modules["alascrapy"].__file__)
                backup_filename = 'fake_useragent_%s.json' % settings.__version__
                copyfile(join(d, backup_filename), cache_file)

    def process_request(self, request, spider):
        manual_user_agent = request.meta.get('User-Agent', None)
        if manual_user_agent:
             request.headers['User-Agent'] = manual_user_agent
        else:
            new_user_agent = self.ua.random
            if new_user_agent:
                request.headers['User-Agent']= new_user_agent