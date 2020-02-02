# -*- coding: utf8 -*-
from datetime import datetime

from scrapy.http import Request

from alascrapy.items import CategoryItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format
from alascrapy.items import ReviewItem, ProductItem
import alascrapy.lib.dao.incremental_scraping as incremental_utils


class TheWirecutterSpider(AlaSpider):
    name = 'thewirecutter'
    allowed_domains = ['thewirecutter.com']
    start_urls = ['http://thewirecutter.com/']

    def __init__(self, *args, **kwargs):
        super(TheWirecutterSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

    def parse(self, response):
        ori_url = response.url
        needed_cats = ['electronics', 'home',
                       'ketchen', 'appliances']
        category_xpath = '//ul[@id="primary-large"]/li//a/@href'
        categories = self.extract_list(response.xpath(category_xpath))
        for cat in categories:
            cat_full_url = get_full_url(ori_url, cat)
            for i in needed_cats:
                if i in cat_full_url:
                    ori_cat = i
                    yield Request(url=cat_full_url,
                                  callback=self.parse_review,
                                  meta={'category': ori_cat})

    def parse_review(self, response):
        category = response.meta.get('category', '')
        review = ReviewItem()
        product = ProductItem()
        contents = response.xpath('//div[@itemprop="sectionBody"]//ul/li')
        for content in contents:
            # incremental
            date_str = self.extract(content.xpath('.//time/@datetime'))
            date_str = date_format(date_str, '%Y-%m-%d')
            date_time = datetime.strptime(date_str, '%Y-%m-%d')
            if date_time < self.stored_last_date:
                return
            title = self.extract(content.xpath('.//h3//text()'))
            author = self.extract_all(content.xpath(
                './/p[@class="_0595b3a8"]//text()')).replace(
                    'by', '').strip()
            pic_url = self.extract(content.xpath('.//img/@src'))
            sumamry = self.extract_all(content.xpath(
                './/div[@class="aae31009"]//text()'))
            test_url = self.extract(content.xpath('.//h3//a/@href'))
            sid = test_url.split('/')[-2]
            # product name
            product_name = self.get_product_name(title)
            # product items
            product['ProductName'] = product_name
            product['PicURL'] = pic_url
            product['source_internal_id'] = sid
            product['TestUrl'] = test_url
            product['OriginalCategoryName'] = category
            # review items
            review['ProductName'] = product_name
            review['TestTitle'] = title
            review['Author'] = author
            review['TestUrl'] = test_url
            review['DBaseCategoryName'] = 'pro'
            review['TestDateText'] = date_str
            review['TestSummary'] = sumamry
            review['source_internal_id'] = sid

            yield review
            yield product

    def get_product_name(self, title):
        product_name = title
        if 'The Best' in product_name:
            product_name = product_name.replace('The Best', '')
        if 'Review:' in product_name:
            product_name = product_name.split('Review:')[0]
        product_name = product_name.strip()
        return product_name
