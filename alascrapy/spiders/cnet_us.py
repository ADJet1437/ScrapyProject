# -*- coding: utf8 -*-
import re

from urllib import unquote
from datetime import datetime

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.items import ProductIdItem, CategoryItem
from alascrapy.lib.generic import date_format, get_full_url
import alascrapy.lib.dao.incremental_scraping as incremental_utils

TESTSCALE = 10

class CnetUSSpider(AlaSpider):
    name = 'cnet_us'
    allowed_domains = ['cnet.com']
    start_urls = ['https://www.cnet.com/reviews/']

    def __init__(self, *args, **kwargs):
        super(CnetUSSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        #self.stored_last_date = datetime(2019, 6, 1)

    def parse(self, response):
        category_urls = self.extract_list(response.xpath(
            "//ul[@class='catListing']//li/a/@href"))
        for cat in category_urls:
            if 'game' in cat:
                continue
            yield response.follow(url=cat, callback=self.parse_review_page)

    def parse_review_page(self, response):
        # The website has three types of structure for reviews
        review_urls_xpath1 = "//div[@class='items']/section/div[2]/a/@href"
        review_urls_xpath2 = "//a[@class='assetHed']/@href"
        review_urls_xpath3 = "//div[@class='col-6 assetBody']/a/@href"
        review_urls = self.extract_list(response.xpath(
            review_urls_xpath1))
        length = len(review_urls)
        if length == 0:
            option_2 = len(self.extract_list(response.xpath(
                review_urls_xpath2)))
            if option_2 != 0:
                review_urls = self.extract_list(response.xpath(
                    review_urls_xpath2))
            else:
                review_urls = self.extract_list(response.xpath(
                    review_urls_xpath3))

        for review_url in review_urls:
            review_url = get_full_url(response.url, review_url)
            if 'news' in review_url:
                return
            if 'how-to' in review_url:
                return
            yield response.follow(url=review_url, callback=self.level_2)

        next_page_xpath = "//a[@class='next']/@href"
        next_page = self.extract(response.xpath(next_page_xpath))
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def get_product_name(self, response):
        title_option_2 = self.extract(response.xpath(
            "//span[@class='itemreviewed']/text()"))
        if title_option_2 and 'review' in title_option_2:
            product_name = title_option_2.split('review')[0]
        else:
            # use url to get product name
            name_xpath = response.url
            name = name_xpath.split('/')
            forth_item = 4
            product_name = name[forth_item]
            product_name = product_name.replace('-', ' ')
            patterns = ['preview', 'rreview', 'xreview', 'review']
            for pattern in patterns:
                if pattern in product_name:
                    product_name = product_name.replace(pattern, ' ')
        return product_name

    def parse_price(self, product, response):
        price_xpath = "//div[@class='price']/a/text()|"\
            "//a[@class='price']/text()|"\
            "//span[@class='msrp']/text()"
        price_str = (self.extract(response.xpath(price_xpath))).encode('utf-8')

        if price_str:
            return ProductIdItem.from_product(
                product,
                kind='price',
                value=price_str.lstrip('$')
            )

    def level_2(self, response):
        # skip video reviews
        url_str = unquote(response.url)
        video_pattern = 'https://www.cnet.com/videos'
        if video_pattern in url_str:
            return
        try:
            date_xpath = "//div[@class='reviewDate']/time/@datetime"
            date = self.extract(response.xpath(date_xpath))
            date_str = date.split("T")[0]
            date_time_to_compare = datetime.strptime(date_str, '%Y-%m-%d')
        except:
            date_xpath = "//div[@class='c-assetAuthor_date']/time/@datetime"
            date = self.extract(response.xpath(date_xpath))
            date_str = date.split("T")[0]
            date_time_to_compare = datetime.strptime(date_str, '%Y-%m-%d')
        if date_time_to_compare < self.stored_last_date:
            return

        product_xpaths = {
            "PicURL": '//meta[@property="og:image"][1]/@content'
        }

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['source_internal_id'] = str(response.url).split("/")[4].rstrip("/")

        review_xpaths = {
            "TestSummary": '//meta[@property="og:description"]/@content',
            "Author": "//a[@rel='author']/span/text()",
            'SourceTestRating': "//div[@class='col-1 overall']"
            "/div/span/text()",
            'TestCons': "//p[@class='theBad']/span/text()",
            'TestPros': "//p[@class='theGood']/span/text()",
            "TestTitle": "//meta[@name='description']/@content",
            'TestVerdict': "//p[@class='theBottomLine']/span/text()"
        }
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        
        title = review['TestTitle']
        if title and 'review' in title:
            product_name = title.split('review')[0]
            review['ProductName'] = product_name
        review['ProductName'] = self.get_product_name(response)
        product['ProductName'] = review['ProductName']

        review['source_internal_id'] = product['source_internal_id']

        product_manufacturer = review['ProductName'].split(' ')[0]
        product['ProductManufacturer'] = product_manufacturer
        if review['SourceTestRating']:
            review['SourceTestScale'] = TESTSCALE

        review["DBaseCategoryName"] = "PRO"
        review['TestDateText'] = date_str

        product_id = self.parse_price(product, response)
        original_category_name_xpath = "//ul[@class='breadcrumb -isDark']//li/a/text()"
        original_category_name = self.extract_all(
            response.xpath(original_category_name_xpath), " | ")
        if original_category_name and date_str:
            # filter uesless review page
            # https://www.cnet.com/pictures/black-friday-2018-the-best-playstation-4-console-game-deals/
            product["OriginalCategoryName"] = original_category_name
            yield product_id
            yield product
            yield review

