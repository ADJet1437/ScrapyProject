# -*- coding: utf8 -*-
from datetime import datetime
import re

from scrapy.http import Request, HtmlResponse
from scrapy.selector import Selector

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.spiders.base_spiders.bazaarvoice_spider import BVNoSeleniumSpider
from alascrapy.lib.generic import get_full_url, date_format
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import CategoryItem, ProductItem, ReviewItem, ProductIdItem
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from alascrapy.lib.selenium_browser import SeleniumBrowser
import alascrapy.lib.dao.incremental_scraping as incremental_utils


class Laptopmag_comSpider(AlaSpider):
    name = 'laptopmag_com'
    allowed_domains = ['laptopmag.com']
    start_urls = ['https://www.laptopmag.com/reviews']

    def __init__(self, *args, **kwargs):
        super(Laptopmag_comSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

    def parse(self, response):

        review_contents = response.xpath("//div[@class='mod line listItem']")
        for content in review_contents:
            review_url = ".//div[starts-with(@class,'h1')]/a/@href"
            url = self.extract(content.xpath(review_url))

            date_xpath = ".//time/text()"
            date_time = self.get_date_time(response, date_xpath)
            if self.stored_last_date > date_time:
                return
            yield response.follow(url=url, callback=self.parse_review)

        next_page_xpath = "//a[@rel='next']/@href"
        next_page = self.extract(response.xpath(next_page_xpath))

        oldest_date_xpath = "(//time/text())[last()]"
        date_time = self.get_date_time(response, date_xpath)
        if next_page and self.stored_last_date < date_time:
            yield response.follow(url=next_page, callback=self.parse)

    def get_date_time(self, response, date_xpath):
        date_ori = self.extract(response.xpath(date_xpath))
        date_str = date_format(date_ori, "%b %d, %Y")
        date_time = datetime.strptime(date_str, '%Y-%m-%d')
        return date_time

    def parse_review(self, response):

        product_xpaths = {
            "PicURL": "//meta[@property='og:image']/@content",
        }
        review_xpaths = {
            "TestTitle": "//meta[@property='og:title']\
            [not(contains(//meta[@property='og:url']/@content,'tomsguide'))]\
            /@content",

            "SourceTestRating": "//div[@itemprop='itemReviewed']\
            /following::meta[@itemprop='ratingValue'][1]/@content",

            "TestDateText": "//time/@datetime",

            "TestPros": "//div[contains(text(), 'Pros')]\
            /following-sibling::p/text()",

            "TestCons": "//div[contains(text(), 'Cons')]\
            /following-sibling::p/text()",

            "TestSummary": "//meta[@property='og:description']/@content",

            "TestVerdict": "//div[contains(text(), 'Verdict')]\
            /following-sibling::p/text()"
        }

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        # OriginalCategoryName
        script = self.extract_all(response.xpath(
            "//script[@type='text/javascript']"))
        category = re.findall(r'ad_category = "([a-zA-Z]+)"', script)
        category = category[0]
        product['OriginalCategoryName'] = category
        # pic url
        picurl = product.get("PicURL", "")
        if picurl and picurl[:2] == "//":
            product["PicURL"] = "https:" + product["PicURL"]
        if picurl and picurl[:1] == "/":
            product["PicURL"] = get_full_url(original_url, picurl)

        try:
            title = review.get('TestTitle', '')
            if "Review" in title:
                product_name = title.replace("Review", '').rstrip()
                review['ProductName'] = product_name
                product['ProductName'] = product_name
            else:
                product_name = title
                review['ProductName'] = product_name
                product['ProductName'] = product_name
        except:
            print("No TestTitle")
        # sid
        url_id = response.url.split('/')[-1]
        sid = re.findall(r"\w+", url_id)
        sid = "".join(i for i in sid)
        review['source_internal_id'] = sid
        product['source_internal_id'] = sid
        # pros, cons and verdict
        if not review.get('TestPros', ''):
            pro = self.extract(response.xpath(
                "//li[@class='otmPros']//p/text()"))
            review['TestPros'] = pro
        if not review.get('TestCons', ''):
            con = self.extract(response.xpath(
                "//li[@class='otmCons']//p/text()"))
            review['TestCons'] = con
        if not review.get('TestPros', ''):
            verdict = self.extract(response.xpath(
                "//li[@class='otmVerdict']//p/text()"))
            review['Verdict'] = verdict

        id_value = self.extract(response.xpath(
            "//meta[contains(@content,'Price')]/following-sibling::meta[1]/@content"))
        if id_value:
            product_id = self.product_id(product)
            product_id['ID_kind'] = "price"
            product_id['ID_value'] = id_value
            yield product_id

        review["DBaseCategoryName"] = "PRO"

        # json ld
        json_ld_date = self.extract_all(response.xpath(
            '//script[@type="application/ld+json"]'))

        rating = re.findall(r'"ratingValue": "(.*?)"', json_ld_date)[0]
        review["SourceTestRating"] = rating
        review["SourceTestScale"] = "5"

        author = re.findall(r'"name": "(.*?)"', json_ld_date)[0]
        review['Author'] = author

        if review["TestDateText"]:
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(
                review["TestDateText"], "%b %d, %Y", ["en"])

        yield product

        yield review
