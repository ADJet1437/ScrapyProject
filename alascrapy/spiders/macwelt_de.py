# -*- coding: utf8 -*-
import datetime
from datetime import datetime, timedelta

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils


class Macwelt_deSpider(AlaSpider):
    name = 'macwelt_de'
    allowed_domains = ['macwelt.de']
    start_urls = ['https://www.macwelt.de/archiv']

    def __init__(self, *args, **kwargs):
        super(Macwelt_deSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):
        start_dt = self.stored_last_date
        end_dt = datetime.today()
        for dt in self.daterange(start_dt, end_dt):
            day = dt.strftime("%Y-%m-%d")
            day_url = 'https://www.macwelt.de/archiv/tag/%s'%(day)
            yield response.follow(url=day_url, callback=self.parse_day)

    def parse_day(self, response):
        category_xpath = "//span[text()='Test']/parent::a/@href"
        category_urls = self.extract_list(response.xpath(category_xpath))
        for category_url in category_urls:
            yield response.follow(url=category_url, callback=self.parse_review)

    def parse_review(self, response):
        product_xpaths = {
            "PicURL": "//meta[@property='og:image']/@content"
        }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)

        product_name_xpath = "//meta[@property='og:title']/@content"
        ProductName = response.xpath(product_name_xpath).re_first(r'(.*):')
        if not ProductName:
            ProductName = response.xpath(product_name_xpath).re_first(r'(.*)-')
        if not ProductName:
            ProductName = self.extract(response.xpath(product_name_xpath))
        product["ProductName"] = ProductName

        source_internal_id_xpath = "//link[@rel='amphtml']/@href"
        product['source_internal_id'] = response.xpath(
            source_internal_id_xpath).re_first(r'/([0-9]+)')
        yield product

        review_xpaths = {
            "TestDateText": "//meta[@name='date']/@content",
            "TestSummary": "//meta[@name='description']/@content",
            "Author": "//meta[@name='author']/@content",
            "TestTitle": "//meta[@property='og:title']/@content",
        }
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        review["DBaseCategoryName"] = "PRO"
        review["ProductName"] = product["ProductName"]
        review['source_internal_id'] = product['source_internal_id']
        yield review

    def daterange(self, date1, date2):
        """ this function return the date between date 1 and date 2 """
        for n in range(int((date2 - date1).days) + 1):
            yield date1 + timedelta(n)
