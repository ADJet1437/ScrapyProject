# -*- coding: utf8 -*-

import re
from datetime import datetime
import dateparser
from urllib import unquote
from scrapy import Request

from alascrapy.items import ProductItem, ReviewItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import date_format, get_full_url
import alascrapy.lib.dao.incremental_scraping as incremental_utils


class OutdoorgearlabSpider(AlaSpider):
    name = 'outdoorgearlab_com'
    allowed_domains = ['outdoorgearlab.com']
    start_urls = ['https://www.outdoorgearlab.com/t/luggage',
                 'https://www.outdoorgearlab.com/t/backpacks']

    def __init__(self, *args, **kwargs):
        super(OutdoorgearlabSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):

        review_divs_xpath = "//div[@id='tag_tiles']/div[1]"
        review_divs = response.xpath(review_divs_xpath)

        for review_div in review_divs:
            date_xpath = "./article//span[@class='tag_tile_age']/text()"
            dates = (review_div.xpath(date_xpath)).getall()
            for date in dates:
                review_date = dateparser.parse(date)
                if review_date > self.stored_last_date:
                    review_urls_xpath = "./article/a/@href"
                    review_urls = (review_div.xpath(review_urls_xpath)).getall()
                    for review in review_urls:
                        review_url = get_full_url(response.url, review)
                        yield Request(review_url, callback=self.parse_review)

        next_page_xpath = "//div[@class='small']/a[@class='small']/@href"
        next_page = self.extract(response.xpath(next_page_xpath))

        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_review(self, response):

        review_xpaths = {
            "TestTitle": "//meta[@property='og:title']/@content",
            "Author": "//div[@id='main_content']/div[4]/div[@class='small'][1]/a/text()",
            "TestSummary": "//meta[@name='description']/@content"
        }
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        product = ProductItem()
        review['TestTitle'] = review['TestTitle'].replace(" | OutdoorGearLab", "")
        if not review['TestSummary']:
            review['TestSummary'] = self.extract(response.xpath("//meta[@property='og:description']/@content"))
        
        if not review['Author']:
            review['Author'] = self.extract(response.xpath("//div[@id='main_content']/div[@class='small'][1]/a/text()"))

        test_url = response.url
        try:
            try:
                internal_source_id = str(test_url).split('/')[6].rstrip('/')
            except:
                internal_source_id = str(test_url).split('/')[5].rstrip('/')
        except:
            internal_source_id = str(test_url).split('/')[4].rstrip('/')
            
        review['source_internal_id'] = internal_source_id
        product['source_internal_id'] = internal_source_id
        # product name
        title = (review['TestTitle']).encode('utf-8')
        if 'review' in title:
            product_name = title.replace(" review", "")
        elif 'Review' in title:
            product_name = title.replace(" Review", "")
        elif ':' in title:
            product_name = str(title).split(":")[0]
        else:
            product_name = title

        # product_name = product_name.replace(" - Carryology - Exploring better ways to carry", "").replace(" Video", "").replace("Drive By", "").replace(":", "").replace(" |", "").replace(" Carryology", "")

        review['ProductName'] = product_name
        product['ProductName'] = product_name

        source_test_rating = self.extract(response.xpath(
            "//div[@class='rating_chart_score table_score_top']/text()"))
        if source_test_rating:
            review['SourceTestRating'] = source_test_rating
            review['SourceTestScale'] = '100'
        review['TestUrl'] = test_url
    
        date_str = (self.extract(response.xpath("//div[@id='main_content']//div[@class='small'][1]/text()[3]"))).encode('utf-8')
        if date_str:
            if 'and' in date_str:
                pass
            else:
                date_str = date_str.lstrip("  ⋅  ")
        else:
            date_str = self.extract(response.xpath("//div[@id='main_content']/div[@class='small'][2]/text()"))

        if not date_str:
            date_str = self.extract(response.xpath("//div[@id='main_content']/div[@class='small'][2]/text()"))
        
        if not date_str:
            date_str = (self.extract(response.xpath("//div[4]/div[@class='small'][1]/text()[2]"))).encode('utf-8')
            date_str = date_str.replace("⋅ Review Editor  ⋅  ", "").replace("Senior Review Editor  ⋅  ", "")
        
        date_time = date_format(date_str, "%M %d, %Y")
        review['TestDateText'] = date_time
        review['DBaseCategoryName'] = 'PRO'

        product['TestUrl'] = test_url
        product['OriginalCategoryName'] = self.extract(response.xpath("//div[@id='breadcrumb_wrapper']/ol/li[2]/a/span/text()"))
        product['PicURL'] = self.extract(response.xpath('//meta[@property="og:image"]/@content'))

        yield review
        yield product