# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
from urllib import unquote

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format
import alascrapy.lib.dao.incremental_scraping as incremental_utils


class SoundstageaccessComSpider(AlaSpider):
    name = 'soundstageaccess_com'
    allowed_domains = ['www.soundstageaccess.com']
    start_urls = ['http://www.soundstageaccess.com/']

    def __init__(self, *args, **kwargs):
        super(SoundstageaccessComSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

    def parse(self, response):
        review_urls = self.extract_list(response.xpath("//h2//a/@href"))
        for url in review_urls:
            yield response.follow(url=url, callback=self.parse_review)

    def parse_review(self, response):
        product_xpaths = {
            "PicURL": "(//div[@itemprop='articleBody']//img/@src)[1]"
        }
        review_xpaths = {
            "TestTitle": "//h2[@itemprop='headline']/text()",
            "Author": "//meta[@name='author']/@content"
        }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        # incremental
        date_xpath = "//time[@itemprop='dateCreated']/@datetime"
        date_text = self.extract(response.xpath(date_xpath))
        if date_text:
            date_str = date_format(date_text, '%Y-%m-%d')
            date_time = datetime.strptime(date_str, '%Y-%m-%d')
            if date_time < self.stored_last_date:
                return
            review['TestDateText'] = date_str
        # pic_url
        pic_url = product['PicURL']
        if pic_url:
            pic_url = get_full_url(response.url, pic_url)
            product['PicURL'] = pic_url
        # sid
        sid = unquote(response.url).split('/')[-1].split('-')[0]
        review['source_internal_id'] = sid
        product['source_internal_id'] = sid
        sumary_list_xpath = "//ul[@class='mostread mod-list']//li//text()"
        sumary = self.extract_all(response.xpath(sumary_list_xpath))
        review['TestSummary'] = sumary
        review['DBaseCategoryName'] = 'PRO'
        review['ProductName'] = review['TestTitle']
        product['ProductName'] = review['ProductName']

        yield product
        yield review
