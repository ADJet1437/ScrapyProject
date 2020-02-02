# -*- coding: utf8 -*-
from alascrapy.spiders.base_spiders.notebookcheck_spider import Notebookcheck_Spider


class Notebookcheck_comSpider(Notebookcheck_Spider):
    name = 'notebookcheck_com'
    allowed_domains = ['notebookcheck.com']
    language = 1
    incremental_scraping = True
    url_format = "https://www.notebookcheck.com/?&hide_youtube=1&page={}&tagArray[]={}"


class Notebookcheck_netSpider(Notebookcheck_Spider):
    name = 'notebookcheck_net'
    allowed_domains = ['notebookcheck.com', 'notebookcheck.net']
    language = 2
    incremental_scraping = True
    url_format = "https://www.notebookcheck.net/?&hide_youtube=1&tagArray[]={}"


class Notebookcheck_orgSpider(Notebookcheck_Spider):
    name = 'notebookcheck_org'
    allowed_domains = ['notebookcheck.com', 'notebookcheck.org']
    language = 3
    incremental_scraping = True
    url_format = "https://www.notebookcheck.org/?&tagArray[]={}"


class Notebookcheck_infoSpider(Notebookcheck_Spider):
    name = 'notebookcheck_info'
    allowed_domains = ['notebookcheck.com', 'notebookcheck.info']
    language = 4
    incremental_scraping = True
    url_format = "https://www.notebookcheck.info/?&tagArray[]={}"


class Notebookcheck_itSpider(Notebookcheck_Spider):
    name = 'notebookcheck_it'
    allowed_domains = ['notebookcheck.com', 'notebookcheck.it']
    url_format = 'https://www.notebookcheck.it/?&page={}&tagArray[]={}&typeArray[]=1'
    language = 5
    incremental_scraping = True


class Notebookcheck_nlSpider(Notebookcheck_Spider):
    name = 'notebookcheck_nl'
    allowed_domains = ['notebookcheck.com', 'notebookcheck.nl']
    language = 6
    incremental_scraping = True


class Notebookcheck_bizSpider(Notebookcheck_Spider):
    name = 'notebookcheck_biz'
    allowed_domains = ['notebookcheck.com', 'notebookcheck.biz']
    language = 7
    incremental_scraping = True
    url_format = "https://www.notebookcheck.nl/?&tagArray[]={}"


class Notebookcheck_plSpider(Notebookcheck_Spider):
    name = 'notebookcheck_pl'
    allowed_domains = ['notebookcheck.com', 'notebookcheck.pl']
    language = 8
    incremental_scraping = True
    url_format = "https://www.notebookcheck.pl/?&hide_youtube=1&hide_external_reviews=1&tagArray[]={}&typeArray[]=1"


class Notebookcheck_trSpider(Notebookcheck_Spider):
    name = 'notebookcheck_tr'
    allowed_domains = ['notebookcheck.com', 'notebookcheck-tr.com']
    language = 9
    incremental_scraping = True
    url_format = "https://www.notebookcheck-tr.com/?&tagArray[]={}"


class Notebookcheck_ruSpider(Notebookcheck_Spider):
    name = 'notebookcheck_ru'
    allowed_domains = ['notebookcheck.com', 'notebookcheck-ru.com']
    language = 10
    incremental_scraping = True


class Notebookcheck_seSpider(Notebookcheck_Spider):
    name = 'notebookcheck_se'
    allowed_domains = ['notebookcheck.com', 'notebookcheck.se']
    language = 19
    incremental_scraping = True
    url_format = "https://www.notebookcheck.se/?&tagArray[]={}"
