# -*- coding: utf8 -*-

import dateparser
import re
from scrapy.http import Request
from datetime import datetime

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format
from alascrapy.items import CategoryItem
import alascrapy.lib.dao.incremental_scraping as incremental_utils


class Engadget_comSpider(AlaSpider):
    name = 'engadget_com'
    allowed_domains = ['engadget.com']
    start_urls = ['https://www.engadget.com/reviews/latest/']

    def __init__(self, *args, **kwargs):
        super(Engadget_comSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)
    
    def parse(self, response):
        original_url = response.url
        date_re = r'([0-9]+/[0-9]+/[0-9]+)'

        urls_xpath = "//div[@class='th-title']//a/@href | //a[contains (@class,'o-hit') and contains(@class,'link')]/@href"
        urls = self.extract_list(response.xpath(urls_xpath))
        
        for single_url in urls:
            try:
                date_match = re.search(date_re, single_url)
                if date_match:
                    review_date_text = date_match.group(1)
                    review_date = dateparser.parse(review_date_text)
                    if review_date < self.stored_last_date:
                        return
            except:
                pass

            single_url = get_full_url(original_url, single_url)
            request = Request(single_url, callback=self.level_2)
            yield request

        # next page
        url_xpath = "//div[@class='container']//div[@class='table']//a[div[contains(text(),'Older')]]/@href"
        single_url = self.extract(response.xpath(url_xpath))
        if single_url:
            single_url = get_full_url(original_url, single_url)
            request = Request(single_url, callback=self.parse)
            yield request
    
    def level_2(self, response):
                                     
        original_url = response.url
        
        product_xpaths = {
                "source_internal_id": "//meta[@name='post_id']/@content",
                "ProductName":"//meta[@property='og:title']/@content",
                "OriginalCategoryName":"//div[@class='th-meta']/a[@class='th-topic']//text()",
                "PicURL":"//meta[@property='og:image']/@content",
                "ProductManufacturer":"//div[contains(@class,'flush-top') and contains(@class,'flush-bottom')]//div[@class='grid@tl+']//a[@class='th-topic']/text()"
                            }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['TestUrl'] = original_url
        picurl = product.get("PicURL", "")
        if picurl and picurl[:2] == "//":
            product["PicURL"] = "https:" + product["PicURL"]
        if picurl and picurl[:1] == "/":
            product["PicURL"] = get_full_url(original_url, picurl)
        manuf = product.get("ProductManufacturer", "")
        if manuf == "" and "//div[contains(@class,'flush-top') and contains(@class,'flush-bottom')]//div[@class='grid@tl+']//a[@class='th-topic']/text()"[:2] != "//":
            product["ProductManufacturer"] = "//div[contains(@class,'flush-top') and contains(@class,'flush-bottom')]//div[@class='grid@tl+']//a[@class='th-topic']/text()"

        if product["OriginalCategoryName"]:
            category = CategoryItem()
            category["category_path"] = product["OriginalCategoryName"]
            yield category

        review_xpaths = {
                "source_internal_id": "//meta[@name='post_id']/@content",
                "ProductName":"//meta[@property='og:title']/@content",
                "SourceTestRating":"//div[contains(@class,'flush-top') and contains(@class,'flush-bottom')]/descendant::div[contains (.,'Engadget Score')][1]//h4[contains (.,'Engadget Score')]/following-sibling::div[1]//div[contains (@class,'t-rating')]/text()",
                "TestDateText":"//div[starts-with(@class,'t-meta-small')]/div[@class='th-meta']/text()[1]",
                "TestPros":"//div[contains(@class,'flush-top') and contains(@class,'flush-bottom')]/descendant::div[contains (.,'Engadget Score')][1]//h5[contains (.,'Pros')]/following-sibling::ul[1]/li/text()",
                "TestCons":"//div[contains(@class,'flush-top') and contains(@class,'flush-bottom')]/descendant::div[contains (.,'Engadget Score')][1]//h5[contains (.,'Cons')]/following-sibling::ul[1]/li/text()",
                "TestSummary":"(//meta[@property='og:description']/@content | //*[contains(.,'Summary')]/following-sibling::p[text()]/text())[last()]",
                "TestVerdict":"//h3[contains (.,'Wrap-up') or contains (.,'Wrapup')]/following::p[2]//text()",
                "TestTitle":"//div[starts-with(@class,'grid') and contains(@class,'flex')]//article[@class='c-gray-1']//h1/text()",
                            }
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        review['TestUrl'] = original_url
        try:
            review['source_internal_id'] = product['source_internal_id']
        except:
            pass

        review["DBaseCategoryName"] = "PRO"
        if review.get('SourceTestRating', '') and not review.get('SourceTestScale', ''):
            review["SourceTestScale"] = "100"

        if review["TestDateText"]:
            review["TestDateText"] = review["TestDateText"].lower().replace('in'.lower(), "")
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(review["TestDateText"], "%m.%d.%y", ["en"])

        yield product
        yield review
