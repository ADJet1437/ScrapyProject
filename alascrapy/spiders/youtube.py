# -*- coding: utf-8 -*-
import dateparser
import re
from datetime import datetime
import json
import pprint
import requests

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from scrapy.http import Request
from alascrapy.items import ReviewItem, ProductItem, ProductIdItem
from alascrapy.lib.generic import get_full_url
import alascrapy.lib.dao.incremental_scraping as incremental_utils


class YoutubeSpider(AlaSpider):
    name = 'youtube'
    allowed_domains = ['youtube.com']

    def __init__(self, *args, **kwargs):
        super(YoutubeSpider, self).__init__(self, *args, **kwargs)
        self.channel_list, self.url_format_list, self.search_str_list, \
            self.ori_cat_list = \
            incremental_utils.get_youtube_channel_id_and_search_str(
                self.mysql_manager
            )

    def start_requests(self):
        print('started ....')
        start_urls = [
            'https://www.youtube.com/channel/UCVYamHliCI9rw1tHR1xbkfw/search?query=review',
            'https://www.youtube.com/user/Mrwhosetheboss/search?query=review',
        ]
        for cat, search_str, channel_id, url_format in zip(self.ori_cat_list,
                                               self.search_str_list,
                                               self.channel_list,
                                               self.url_format_list):
            if url_format == 'user':
                if search_str is not None:
                    url = 'https://www.youtube.com/user/{}/search?query={}'.format(
                        channel_id, search_str)
                    yield Request(url=url,
                                callback=self.parse,
                                meta={'category': cat})
            else:
                url = 'https://www.youtube.com/channel/{}/search?query=review'.format(
                    channel_id)
                yield Request(url=url,
                              callback=self.parse,
                              meta={'category': cat})


        for url in start_urls:
            yield Request(url=url, callback=self.parse)

    def parse(self, response):
        review = ReviewItem()
        product = ProductItem()
        product_id = ProductIdItem()
        contents = response.xpath("//div[@class='yt-lockup-content']")
        pic_contents = response.xpath("//div[@class='yt-lockup-dismissable']")
        for content, pic_content in zip(contents, pic_contents):
            # print response.url
            test_url = self.extract(content.xpath(".//a/@href"))
            full_url = get_full_url(response.url, test_url)
            sid = full_url.split('=')[1]
            title = self.extract(content.xpath(".//a/@title"))
            summary = self.extract_all(content.xpath(
                ".//div[@class='yt-lockup-description yt-ui-ellipsis yt-ui-ellipsis-2']//text()"))
            date_str = self.extract(content.xpath(
                ".//ul[@class='yt-lockup-meta-info']/li[1]/text()"))
            date_time = dateparser.parse(date_str)
            review_date = datetime.strftime(date_time, "%Y-%m-%d")
            author = self.extract(content.xpath(
                ".//div[@class='yt-lockup-byline']//a//text()"))
            if not author:
                self.go_to_review_page(test_url)
                author = self.get_author(response)
            if not author:
                author = self.extract(content.xpath(
                    '//meta[@name="title"]/@content'))
            pic_url = 'https://i.ytimg.com/vi/{}/default.jpg'.format(sid)
            duration_str = self.extract_all(pic_content.xpath(
                './/span[@class="video-time"]//text()'))
            duration = self.calculate_duration(duration_str)
            # product items
            product['source_internal_id'] = sid
            product['ProductName'] = self.get_product_name(title)
            product['TestUrl'] = full_url
            product['PicURL'] = pic_url
            # review items
            review['source_internal_id'] = sid
            review['TestUrl'] = full_url
            review['ProductName'] = self.get_product_name(title)
            review['TestSummary'] = summary
            review['DBaseCategoryName'] = 'vpro'
            review['Author'] = author
            review['TestDateText'] = review_date
            review['TestTitle'] = title
            # we have differnt product_id items, for youtube_id:
            product_id['ProductName'] = self.get_product_name(title)
            product_id['source_internal_id'] = sid
            product_id['ID_kind'] = 'youtube_id'
            product_id['ID_value_orig'] = sid
            product_id['ID_value'] = sid
            yield product_id  
            # for duration
            product_id['ProductName'] = self.get_product_name(title)
            product_id['source_internal_id'] = sid
            product_id['ID_kind'] = 'video_duration'
            product_id['ID_value'] = duration
            yield product_id  

            yield review
            yield product

    def get_product_name(self, title):
        product_name = title
        if product_name.startswith('Review:'):
            product_name = product_name.replace('Review:', '')
        if ' - ' in product_name:
            product_name = product_name.split('-')[0]
        if "!" in product_name:
            product_name = product_name.replace("!", "")
        if ":" in product_name:
            product_name = product_name.split(':')[0].strip()
        if 'review' in product_name.lower():
            product_name = product_name.replace(
                'review', '').replace("Review", "")
        if "Hands On" in product_name:
            product_name = product_name.replace("Hands On", "")
        product_name = product_name.strip()

        return product_name

    def go_to_review_page(self, test_url):
        yield Request(url=test_url, callback=self.get_author)

    def get_author(self, response):
        author = self.extract(response.xpath(
            '//span[@class="stat attribution"]//span//text()'))
        return author
    
    def calculate_duration(self, duration_str):
        duration_str = duration_str.strip()
        minutes = duration_str.split(':')[0]
        seconds = duration_str.split(':')[1]
        total_seconds = int(minutes)*60 + int(seconds)
        
        return str(total_seconds)
