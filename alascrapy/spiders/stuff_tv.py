# -*- coding: utf8 -*-
import re
from datetime import datetime

from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url

import alascrapy.lib.dao.incremental_scraping as incremental_utils


class StuffTvSpider(AlaSpider):
    name = 'stuff_tv'
    allowed_domains = ['stuff.tv']
    start_urls = ['http://www.stuff.tv/reviews']

    def __init__(self, *args, **kwargs):
        super(StuffTvSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):
        latest_review_date_xpath = "(//span[@class='date'])[1]/text()"
        latest_review_date_text = self.extract(response.xpath(latest_review_date_xpath))
        latest_review_date = datetime.strptime(latest_review_date_text, "%d %B %Y")
        if latest_review_date and latest_review_date < self.stored_last_date:
            return

        next_page_xpath = "//li[@class='pager-next']//a/@href"
        review_url_xpath = ".//div[@class='teaser-content']//a/@href"
        img_xpath = ".//img/@src"
        product_items = response.xpath("//div[@id='content']//article")
        
        for item in product_items:
            review_url = self.extract(item.xpath(review_url_xpath))
            review_url = get_full_url(response, review_url)
            request = Request(review_url, callback=self.parse_review)
            img = self.extract(item.xpath(img_xpath))
            request.meta['PicURL'] = img
            yield request

        next_page = self.extract(response.xpath(next_page_xpath))
        next_page = get_full_url(response, next_page)
        request = Request(next_page, callback=self.parse)
        yield request

    def parse_review(self, response):
        product_xpaths = {}

        review_xpaths = { "TestTitle": "//h1[@id='page-title']/text()",
                          "TestSummary": "//span[@itemprop='description']/text()",
                          "Author": "//a[@itemprop='author']/text()",
                          "SourceTestRating": "//div[@class='rating-box']//meta[@itemprop='ratingValue']/@content",
                          "TestDateText": "//time[@itemprop='datePublished']/@datetime",
                          "TestPros":"//div[@id='our-verdict']//div[@id='field-for']//div[@class='field-items']/div//text()", 
                          "TestCons":"//div[@id='our-verdict']//div[@id='field-against']//div[@class='field-items']/div//text()", 
                          "TestVerdict":"//div[@id='our-verdict']/div[@id='field-verdict']//div[@class='field-item even']/text()"
                        }

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        if review and review['TestTitle']:
            title = review["TestTitle"].lower()
            review["ProductName"] = title.replace("app of the week:", "").strip('review').strip()
            product["ProductName"] = review["ProductName"]
            
        try:
            manufacturer_pattern = '"manufacturer":\["\w+"\]'
            manufacturer = re.findall(manufacturer_pattern, response.body, re.M)
            if manufacturer:
                product["ProductManufacturer"] = manufacturer[0].split(":")[-1].strip('"[]')
        except:
            pass
            
        try:
            category_pattern = '"category":\["\w+"\]'
            category = re.findall(category_pattern, response.body, re.M)
            if category:
                product["OriginalCategoryName"] = category[0].split(":")[-1].strip('"[]')
        except:
            pass
        product["PicURL"] = response.meta['PicURL']
        yield product
        
        review["DBaseCategoryName"] = "PRO"
        review["SourceTestScale"] = "5"
        yield review
