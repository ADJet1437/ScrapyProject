# -*- coding: utf8 -*-
from datetime import datetime
import re

from scrapy.http import Request, HtmlResponse
from scrapy.selector import Selector

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.spiders.base_spiders.bazaarvoice_spider \
    import BVNoSeleniumSpider
from alascrapy.lib.generic import get_full_url, date_format
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import CategoryItem, ProductItem, ReviewItem, \
    ProductIdItem
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from alascrapy.lib.selenium_browser import SeleniumBrowser


class Techcrunch_comSpider(AlaSpider):
    name = 'techcrunch_com'
    allowed_domains = ['techcrunch.com']
    start_urls = ['https://techcrunch.com/reviews/']

    def __init__(self, *args, **kwargs):
        super(Techcrunch_comSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

    def parse(self, response):
        date = self.extract(response.xpath(
            "//time[@class='river-byline__time']/@datetime"))
        article_selectors = response.xpath(
            "//div[@class='post-block post-block--image post-block--unread']")
        for selector in article_selectors:
            original_date_time = self.extract(selector.xpath(
                ".//time[@class='river-byline__time']/@datetime"))
            date_time_str = date_format(original_date_time, '%Y-%m-%d')
            date_time = datetime.strptime(date_time_str, '%Y-%m-%d')
            if date_time < self.stored_last_date:
                return
            url_xpath = "//a[@class='post-block__title__link']/@href"
            review_url = self.extract(selector.xpath(url_xpath))
            yield response.follow(url=review_url, callback=self.level_2)

    def level_2(self, response):
        product_xpaths = {
            "source_internal_id": "//body/@class",
            "OriginalCategoryName": "//meta[@property='og:site']"
            "/following-sibling::meta[@name='category'][1]/@content",
            "PicURL": "//meta[@property='og:image']/@content",
            "ProductManufacturer":
            "//*/*[1]/*[starts-with(@class,'card-title')]"
            "/*[not(contains(@href,'/product/'))]/text()"
        }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        picurl = product.get("PicURL", "")
        if picurl and picurl[:2] == "//":
            product["PicURL"] = "https:" + product["PicURL"]
        if picurl and picurl[:1] == "/":
            product["PicURL"] = get_full_url(original_url, picurl)
        manuf = product.get("ProductManufacturer", "")
        if manuf == "" and "//*/*[1]/*[starts-with(@class,'card-title')]"\
                "/*[not(contains(@href,'/product/'))]/text()"[:2] != "//":
            product["ProductManufacturer"] = \
                "//*/*[1]/*[starts-with(@class,'card-title')]"\
                "/*[not(contains(@href,'/product/'))]/text()"
        try:
            product["OriginalCategoryName"] = category['category_path']
        except:
            pass
        ocn = product.get("OriginalCategoryName", "")
        if ocn == "" and "//meta[@property='og:site']"\
                "/following-sibling::meta[@name='category'][1]"\
                "/@content"[:2] != "//":
            product["OriginalCategoryName"] = "//meta[@property='og:site']"\
                "/following-sibling::meta[@name='category'][1]/@content"
        review_xpaths = {
            "source_internal_id": "//body/@class",
            "TestPros": "//*[normalize-space()='Pros']"
            "/following-sibling::*[text()][1]//text()",
            "TestCons": "//*[normalize-space()='Cons']"
            "/following-sibling::*[text()][1]//text()",
            "TestSummary": "//meta[@property='og:description']/@content",
            "TestVerdict": "//div[starts-with(@class,'article-entry')]"
            "/h2[last()]/following-sibling::p[text()][1]/text()",
            "Author": "//div[@class='article__byline']/a/text()",
            "TestTitle": "//h1/text()",
        }
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        try:
            review['ProductName'] = product['ProductName']
            review['source_internal_id'] = product['source_internal_id']
        except:
            pass
        awpic_link = review.get("AwardPic", "")
        if awpic_link and awpic_link[:2] == "//":
            review["AwardPic"] = "https:" + review["AwardPic"]
        if awpic_link and awpic_link[:1] == "/":
            review["AwardPic"] = get_full_url(original_url, awpic_link)
        if review and review['TestTitle']:
            title = review["TestTitle"].lower()
            if ":" in title:
                all_title_parts = title.split(":")
                for part in all_title_parts:
                    review["ProductName"] = part.replace(
                        "review", "") if 'review' in part else title.replace(
                            "review", "")
            else:
                review["ProductName"] = title.replace("review", "")

            review["ProductName"] = review["ProductName"].strip("-: ")
            product["ProductName"] = review["ProductName"]

        review["DBaseCategoryName"] = "PRO"

        matches = None
        field_value = product.get("source_internal_id", "")
        if field_value:
            matches = re.search("((?<=postid-)\d*(?=\s))",
                                field_value, re.IGNORECASE)
        if matches:
            product["source_internal_id"] = matches.group(1)

        matches = None
        field_value = review.get("source_internal_id", "")
        if field_value:
            matches = re.search("((?<=postid-)\d*(?=\s))",
                                field_value, re.IGNORECASE)
        if matches:
            review["source_internal_id"] = matches.group(1)

        script_text = self.extract(response.xpath(
            "(//script[@type='application/ld+json'])[1]"))
        date_match = re.findall(r"datePublished\":\"([^,]*)\"", script_text)
        date_str = date_match[0]
        date = date_format(date_str, '%Y-%m-%d')
        review['TestDateText'] = date

        yield product

        yield review
