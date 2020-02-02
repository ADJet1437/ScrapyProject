# -*- coding: utf-8 -*-
from urllib import unquote
from datetime import datetime
from dateparser import parse
# from translate import Translator

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.items import ProductItem, ReviewItem
from alascrapy.lib.generic import date_format
import alascrapy.lib.dao.incremental_scraping as incremental_utils


class HwupgradeItSpider(AlaSpider):
    name = 'hwupgrade_it'
    allowed_domains = ['hwupgrade.it']
    start_urls = ['https://www.hwupgrade.it/home/telefonia/',
                  'https://www.hwupgrade.it/home/tablet/']

    def __init__(self, *args, **kwargs):
        super(HwupgradeItSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):
        print("Entering: {}".format(response.url))
        article_selector_list = response.xpath("//ul[@class='news']//li")
        for selector in article_selector_list:
            article_url = self.extract(selector.xpath("./a/@href"))
            date_str = self.extract(selector.xpath(
                ".//span[@class='data']/text()"))
            date = parse(date_str)
            if date > self.stored_last_date:
                yield response.follow(url=article_url,
                                      callback=self.parse_product)

    def parse_product(self, response):
        pro_xpaths = "//ul[@class='pro-list']//li/text()"
        if self.extract_list(response.xpath(pro_xpaths)):
            self.parse_product_case2
        review_xpaths = {
            "TestSummary": "//meta[@ property='og:description']/@content",
            "TestTitle": "//meta[@property='og:title']/@content",
            "Author": "//span[@itemprop='name']/text()"
        }
        product_xpaths = {
            "PicURL": "//meta[@itemprop='image']/@content",
            "OriginalCategoryName": "//a[@class='categoria hwu']/text()"
        }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        original_date = self.extract(response.xpath(
            "//span[@itemprop='datePublished']/@content"))
        date_str = date_format(original_date, '%Y-%m-%d')
        review['TestDateText'] = date_str
        # sii
        url_str = unquote(response.url)
        sii = url_str.split('_')[-1].split('.')[0]
        review['source_internal_id'] = sii
        product['source_internal_id'] = sii
        # product name: can not find a perfect way to fetch the product name,
        # just get more information from the title.
        # Need to improve by CR
        # title_it = review.get('TestTitle', '')
        # translator = Translator(from_lang="Italian", to_lang="English")
        # title_en = translator.translate(title_it)
        # items_en = title_en.split(' ')
        # items_it = url_str.split('/')[-1].split('-')
        # title_en_list = [item for item in items_en]
        # title_it_list = [item for item in items_it]

        # product_name = ''
        # for char_en in title_en_list:
        #     for char_it in title_it_list:
        #         if char_en.lower() == char_it.lower():
        #             if char_en not in product_name:
        #                 product_name += '{} '.format(char_en)

        product['ProductName'] = review['TestTitle']
        review['ProductName'] = review['TestTitle']
        review['DBaseCategoryName'] = 'PRO'

        yield product
        yield review
