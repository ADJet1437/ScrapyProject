# -*- coding: utf8 -*-
from datetime import datetime
from urlparse import urlparse
import dateparser

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import CategoryItem, ProductItem
from alascrapy.lib.generic import date_format


class Fwdmagazine_deSpider(AlaSpider):
    name = 'fwdmagazine_be'
    start_urls = ['https://www.fwdmagazine.be/type/review']

    def __init__(self, *args, **kwargs):
        super(Fwdmagazine_deSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):
        review_xpath = "//div[@class='section']/div/a/@href"
        review_urls = self.extract_list(response.xpath(review_xpath))
        for review_url in review_urls:
            review_url = get_full_url(response, review_url)
            yield response.follow(url=review_url,
                                  callback=self.parse_review)

        latest_date_xpath = "(//div[contains(@class,'section')]" \
                            "//span[contains(@class,'category')])[1]/text()"
        # get the date of latest review of the page
        latest_date_text = self.extract(response.xpath(latest_date_xpath))
        latest_date = dateparser.parse(latest_date_text)
        if latest_date and latest_date < self.stored_last_date:
            return

        next_page_xpath = "//a[@rel='next']/@href"
        next_page_url= self.extract(response.xpath(next_page_xpath))
        if next_page_url:
            yield response.follow(url=next_page_url, callback=self.parse)

    def parse_review(self, response):
        source = urlparse(response.url).hostname
        product = ProductItem()
        productname_xpath = "//meta[@property='og:title']/@content"
        productname_re = r'^(?:Review:|Test:)?\s*(.*)'
        product['ProductName'] = response.xpath(productname_xpath).\
            re_first(productname_re)

        if source == 'www.hifi.nl':
            product['PicURL'] = self.extract(response.xpath(
                "//meta[@property='og:image']/@content"))
            source_internal_id_re2 = r'_([0-9]+)'
            source_internal_id_xpath = \
                "//div[contains(@class,'article_')]/@class"
            product['source_internal_id'] = response.xpath(
                source_internal_id_xpath).re_first(source_internal_id_re2)
        elif source == 'www.wearablesmagazine.nl':
            product['PicURL'] = self.extract(response.xpath(
                "//meta[@property='og:image']/@content"))
            product['source_internal_id'] = self.extract\
                (response.xpath("//div[@data-type='article']/@data-id"))
        elif source == 'www.fwdmagazine.be':
            product['PicURL'] = self.extract(
                response.xpath("//meta[@property='og:image']/@content"))
            source_internal_id_re = r'/([0-9]+)$'
            source_internal_id_xpath = "//link[@rel='next']/@href"
            product['source_internal_id'] = response.xpath(
                source_internal_id_xpath).re_first(source_internal_id_re)
        else:
            picURL_xpath = "(//img[@srcset])[1]/@srcset"
            picURL_re = r'(.*),'
            product['PicURL'] = response.xpath(picURL_xpath).re_first(
                picURL_re)
            source_internal_id_re = r'p=([0-9]+)'
            source_internal_id_xpath = "//link[@rel='shortlink']/@href"
            product['source_internal_id'] = response.xpath(
                source_internal_id_xpath).re_first(source_internal_id_re)

        product['TestUrl'] = response.url

        category = CategoryItem()
        category_path_xpath = "//span[contains(@class,'cat')]/a/text()"
        category_re = r'(.*)(?i)reviews'
        category['category_path'] = response.xpath\
            (category_path_xpath).re_first(category_re)
        # prevent categories_pipeline to call lower() on 'None' object
        if not category['category_path']:
            category['category_path'] = ''
        # product's OriginalCategoryName should always
        # match category_path of the corresponding category item
        product['OriginalCategoryName'] = category['category_path']

        yield product
        yield category

        date_xpath = ''
        if source == 'www.hifi.nl':
            review_xpaths = {
                "TestSummary": "//meta[@name='description']/@content",
                "Author": "//a[contains(@href,'auteur')]//text()",
                "TestTitle": "//meta[@property='og:title']/@content"
            }
            date_xpath = "//a[contains(@href,'auteur')]/following::text()"
        elif source == 'www.fwdmagazine.be':
            review_xpaths = {
                "TestPros": "//ul[@class='pro']//li/text()",
                "TestCons": "//ul[@class='con']//li/text()",
                "TestSummary": "//meta[@name='description']/@content",
                "Author": "//span[@itemprop='name']/text()",
                "TestTitle": "//meta[@property='og:title']/@content",
                "SourceTestScale": "count(//span[contains(@class,'star-icon')])",
                "SourceTestRating": "count(//span[contains(@class,'full')])"
                                    "+0.5*count(//span[contains(@class,'half')])",
            }
            date_xpath = "//meta[contains(@itemprop,'ublished')]/@content"
        else:
            review_xpaths = {
                "TestPros": "//div[contains(@class,'positive')]/ul/li/text()",
                "TestCons": "//div[contains(@class,'negative')]/ul/li/text()",
                "TestSummary": "//h2[contains(text(),'onclusi')]"
                               "/following-sibling::p/text()",
                "Author": "//a[@rel='author']/text()",
                "TestTitle": "//meta[@property='og:title']/@content",
                "SourceTestScale": "//span[@class='best']/text()",
                "SourceTestRating": "//span[@class='value']/text()"
            }
            if source == 'www.wearablesmagazine.nl':
                date_xpath = "//div[contains(@class,'date')]/text()"
            else:
                date_xpath = "//span[contains(@class,'date')]/text()"
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        date_text = self.extract(response.xpath(date_xpath))
        if not review.get('TestSummary', ''):
            review['TestSummary'] = self.extract(response.xpath("//meta[@property='og:description']/@content"))
        review["TestDateText"] = date_format(date_text, "%Y-%m-%d")
        review["ProductName"] = product["ProductName"]
        review["DBaseCategoryName"] = "PRO"
        review['source_internal_id'] = product['source_internal_id']
        review['TestUrl'] = product['TestUrl']
        if source == 'www.wearablesmagazine.nl':
            review["SourceTestScale"] = "10"
        yield review

