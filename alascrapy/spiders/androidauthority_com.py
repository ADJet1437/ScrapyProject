# -*- coding: utf8 -*-
from datetime import datetime
from urlparse import urlparse

import dateparser

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import CategoryItem
from alascrapy.lib.generic import date_format


class Androidauthority_comSpider(AlaSpider):
    name = 'androidauthority_com'
    allowed_domains = ['androidauthority.com']
    start_urls = ['https://www.androidauthority.com/reviews']

    def __init__(self, *args, **kwargs):
        super(Androidauthority_comSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        #if not self.stored_last_date:
        self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):

        review_divs_xpath = "//div[@class='loop']"
        review_divs = response.xpath(review_divs_xpath)

        for review_div in review_divs:
            date_xpath = './/span[contains(@class,"time")]/text()'
            dates = (review_div.xpath(date_xpath)).getall()
            for date in dates:
                review_date = dateparser.parse(date)
                if review_date > self.stored_last_date:
                    review_urls_xpath = ".//div//div//div//a/@href"
                    review_urls = (review_div.xpath(review_urls_xpath)).getall()
                    del review_urls[1::2]
                    for review_url in review_urls:
                        yield response.follow(url=review_url,
                                  callback=self.parse_review)

        last_page=30
        for i in range(2, last_page+1):
            next_page_url = 'https://www.androidauthority.com/reviews/page/'+str(i)
            if next_page_url:
                last_date = self.extract(response.xpath('(//div[@class="loop"]//span[contains(@class,"time")]/text())[last()]'))
                date_time = dateparser.parse(last_date, '%Y-%m-%d')

                if date_time > self.stored_last_date:
                    yield response.follow(next_page_url, callback=self.parse)

    def get_category(self, response):

        category_tags = ['cell phone', 'smartphone', 'smartphones',
                         'speaker', 'speakers', 'wireless speaker',
                         'bluetooth speaker', 'bluetoothspeaker',
                         'bookshelf speakers',
                         'headphones', 'headset', 'earphones', 'earbuds',
                         'wireless earbuds', 'bluetooth earbuds',
                         'laptop', 'laptops', 'gaming laptop', 'e-reader',
                         'tablet',
                         'camera',
                         'tv',
                         'desktop', 'pc', 'computer', 'gaming pc',
                         'webcam',
                         'monitor', 'display', 'gaming monitor',
                         'mouse', 'gaming mouse',
                         'fitness tracker', 'fitness trackers', 'watch',
                         'wearables',
                         'smart lamp',
                         'office chair',
                         'phone case', 'smartphone case',
                         '3d-printer', 'router',  'projector', 'ssd',
                         'fitnesstracker', 'smartwatch',
                         'drone', 'toys', 'usb hub', 'grilling', 'ice maker',
                         'iring', 'wireless charging', 'laser measuring',
                         'wood cover', 'backpack', 'routers', 'mobile']

        tag_xpath = "//meta[contains(@name,'keywords')]/@content"
        page_tags = self.extract(response.xpath(tag_xpath)).split(', ')
        page_tags = [t.lower() for t in page_tags]

        category_name = ''
        for page_tag in page_tags:
            if page_tag in category_tags:
                category_name = page_tag
                break

        if category_name:
            category = CategoryItem()
            category['category_path'] = category_name
            return category

    def parse_review(self, response):

        category = self.get_category(response)
        if category and not self.should_skip_category(category):
            yield category

        product_xpaths = {
            "PicURL": "(//meta[@property='og:image'])[1]/@content"
        }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)

        source_internal_id_xpath = "//link[@rel='shortlink']/@href"
        source_internal_id_re = r'p=([0-9]+)'
        product['source_internal_id'] = response.xpath(
            source_internal_id_xpath).re_first(source_internal_id_re)
        
        manufacturer = self.extract(response.xpath("//div[@class='product-title']/div[@class='device_manufacturer']/text()"))
        
        if manufacturer:
            product["ProductManufacturer"] = str(manufacturer).split(" ")[1]
        else:
            product["ProductManufacturer"] = self.extract(response.xpath("//meta[@property='article:tag']/@content"))

        productname = self.extract(response.xpath("//div[@class='product-title']/div[@class='device_name']/text()"))
        if not productname:
            productname = str(response.url).split('/')[3].split('-review')[0].replace('-', ' ')
            product['ProductName'] =  productname
        if manufacturer: 
            product['ProductName'] = str(manufacturer).split(" ")[1] + ' ' + productname
        
        yield product

        review_xpaths = {
            "TestDateText": "//meta[contains(@property,'published')]/@content",
            "TestPros": "//div[contains(@class,'procon pro')]//p//text()",
            "TestCons": "//div[contains(@class,'procon con')]//p//text()",
            "TestSummary": "//div[contains(@class,'bottomline')]/p/text()",
            "Author": "//div[@class='author-name-block']/a[@class='info author-name']/text()",
            "TestTitle": "//meta[@property='og:title']/@content",
            "SourceTestRating": "//meta[@itemprop='ratingValue']/@content",
            "SourceTestScale": "//meta[@itemprop='bestRating']/@content"
        }
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        if not review["TestSummary"]:
            review["TestSummary"] = self.extract(response.xpath
                            ("//meta[@property='og:description']/@content"))
        review["DBaseCategoryName"] = "PRO"
        review["ProductName"] = product["ProductName"]
        review['source_internal_id'] = product['source_internal_id']
        review['TestDateText'] = review['TestDateText'].split('T')[0]
        yield review
