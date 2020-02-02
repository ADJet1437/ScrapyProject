# -*- coding: utf8 -*-

import re
import traceback
from datetime import datetime, date
import json
from langdetect import detect
from scrapy.http import Request
# from httplib import BadStatusLine

import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import date_format, get_full_url, dateparser
from alascrapy.lib.selenium_browser import get_award_image_screenshot
from alascrapy.items import ReviewItem, ProductItem

TEST_SCALE = 5


class TechRadarSpider(AlaSpider):
    name = 'techradar'
    allowed_domains = ['techradar.com']

    category_base_urls = {
        "Smartphones": [
            "https://www.techradar.com/more/reviews/phones/mobile-phones/1560251023",
            "https://www.techradar.com/more/reviews/phones/mobile-phones/1563180941",
            "https://www.techradar.com/more/reviews/phones/mobile-phones/1562076654",
            "https://www.techradar.com/more/reviews/phones/mobile-phones/1561645728",
            "https://www.techradar.com/reviews/phones/mobile-phones"
        ],
        "TVs": [
            "https://www.techradar.com/more/reviews/audio-visual/televisions/1559323103",
            "https://www.techradar.com/more/reviews/audio-visual/televisions/1559349791",
            "https://www.techradar.com/more/reviews/audio-visual/televisions/1549927645",
            "https://www.techradar.com/reviews/audio-visual/televisions"
        ],
        "digital cameras": [
            "https://www.techradar.com/more/reviews/cameras-and-camcorders/cameras/1557325191",
            "https://www.techradar.com/more/reviews/cameras-and-camcorders/cameras/1557416332",
            "https://www.techradar.com/reviews/cameras-and-camcorders/cameras"
        ],
        "Loptops": [
            "https://www.techradar.com/reviews/pc-mac/laptops-portable-pcs/laptops-and-netbooks"
        ],
        "Tablets": [
            "https://www.techradar.com/more/reviews/pc-mac/tablets/1562082944",
            "https://www.techradar.com/more/reviews/pc-mac/tablets/1559591162",
            "https://www.techradar.com/reviews/pc-mac/tablets"
        ],
        "Car Tech": [
            "https://www.techradar.com/reviews/car-tech/"
        ],
        "Audio Visual": [
            "https://www.techradar.com/more/reviews/audio-visual/1561986370",
            "https://www.techradar.com/more/reviews/audio-visual/1562090256",
            "https://www.techradar.com/more/reviews/audio-visual/1562671205",
            "https://www.techradar.com/more/reviews/audio-visual/1563306523",
            "https://www.techradar.com/reviews/audio-visual"
        ],
        "Wearables": [
            "https://www.techradar.com/more/reviews/wearables/1559592333",
            "https://www.techradar.com/more/reviews/wearables/1560337029",
            "https://www.techradar.com/more/reviews/wearables/1562340145",
            "https://www.techradar.com/reviews/wearables"
        ],
    }

    def __init__(self, *args, **kwargs):
        super(TechRadarSpider, self).__init__(self, *args, **kwargs)
        self.last_date_to_scrape = \
            incremental_utils.get_latest_pro_review_date(
                self.mysql_manager, self.spider_conf["source_id"])

    def start_requests(self):
        for key in self.category_base_urls:
            urls = self.category_base_urls.get(key, [])
            for url in urls:
                yield Request(url=url, callback=self.parse,
                              headers={'Accept': '*/*',
                                       'Referer': 'https://www.techradar.com/reviews/phones/mobile-phones',
                                       'Accept-Language': 'en-US,en;q=0.9'},
                              meta={'cat': key})

    def parse(self, response):
        category = response.meta.get('cat')
        review_links = self.extract_list(response.xpath(
            '//a[@class="article-link"]/@href'))
        for link in review_links:
            yield Request(link, callback=self.parse_review,
                          meta={'cat': category})

    def parse_review(self, response):
        review = ReviewItem()
        product = ProductItem()

        category = self.extract(response.xpath("//nav[@class='breadcrumb']/ol/li[3]/a/text()"))
        product['OriginalCategoryName'] = category

        sid = self.extract(response.xpath(
            '//article[@class="review-article"]/@data-id'))
        product['source_internal_id'] = sid
        review['source_internal_id'] = sid

        pros = self.extract_all(response.xpath(
            "//h4[contains(text(), 'For')]/following-sibling::ul/li//text()"))
        cons = self.extract_all(response.xpath(
            "//h4[contains(text(),'Against')]/"
            "following-sibling::ul/li//text()"))
        review['TestPros'] = pros
        review['TestCons'] = cons

        verdict = self.extract_all(response.xpath(
            "//h3[contains(text(), 'Verdict')]/following-sibling::p//text()"))
        review['TestVerdict'] = verdict

        body = response.body
        # remove whitespaces
        text = ''.join(x.rstrip('\n') for x in body)
        json_data = re.findall(r'json">(.*?)</script>', text, re.I)
        if json_data:
            json_data = json_data[1]
        else:
            self._logger.info("Bad product, skipped {}".format(response.url))
            return
        json_structrue = json.loads(json_data)
        review_date = self.extract(response.xpath("//time[@class='no-wrap chunk relative-date']/@datetime"))
        date_str = review_date.split('T')[0]
        date_time = datetime.strptime(date_str, '%Y-%m-%d')
        if date_time < self.last_date_to_scrape:
            return
        review['TestDateText'] = date_str

        summary = self.extract(response.xpath('//meta[@name="description"]/@content'))
        review['TestSummary'] = summary

        rating_str = json_structrue.get("reviewRating")
        if rating_str:
            rating = rating_str.get('ratingValue')
            if rating:
                SCALE = '5'
                review['SourceTestScale'] = SCALE
                review['SourceTestRating'] = rating

        test_url = response.url
        product['TestUrl'] = test_url
        review['TestUrl'] = test_url

        test_title = self.extract(response.xpath('//meta[@property="og:title"]/@content'))
        review['TestTitle'] = test_title

        author_str = self.extract(response.xpath("//span[@class='no-wrap by-author']/a/span/text()"))
        review['Author'] = author_str
        
        product_info = json_structrue.get('itemReviewed')
        if product_info:
            brand = product_info.get('brand').get('name')
            product['ProductManufacturer'] = brand
            product_name = product_info.get('name')
        product_name = product.get('ProductName', None)
        if not product_name:
            product_name = test_title.replace('review',
                                              '').replace('Review', '')
        if "hands on:" in product_name.lower():
            product_name = product_name.replace("Hands on:", '').strip()

        product['ProductName'] = product_name
        review['ProductName'] = product_name

        pic_url = json_structrue.get('image')
        if not pic_url:
            pic_url = json_structrue.get('thumbnailUrl')
        product['PicURL'] = pic_url
        review['DBaseCategoryName'] = 'PRO'

        yield product
        yield review
