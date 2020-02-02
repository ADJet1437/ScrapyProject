# -*- coding: utf8 -*-
from datetime import datetime
import re

from urllib import unquote

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import date_format, get_full_url
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem, ProductIdItem

TESTSCALE = 5


class Pc_magazin_deSpider(AlaSpider):
    name = 'pc_magazin_de'
    allowed_domains = ['pc-magazin.de']
    start_urls = ['http://www.pc-magazin.de/testbericht/alle']

    def __init__(self, *args, **kwargs):
        super(Pc_magazin_deSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        if self.stored_last_date:
            self.stored_last_date = datetime(self.stored_last_date.year,
                                             self.stored_last_date.month,
                                             1)
        else:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):
        archive_urls_xpath = "//h5/a[@class='teaser__link']/@href"
        archive_date_re = r'/testbericht/alle/(\d+)-(\d+)'
        urls = self.extract_list(response.xpath(archive_urls_xpath))

        for archive_url in urls:
            match = re.search(archive_date_re, archive_url)
            if match:
                year = int(match.group(1))
                month = int(match.group(2))
                archive_date = datetime(year, month, 1)
                if archive_date >= self.stored_last_date:
                    yield response.follow(archive_url,
                                          callback=self.parse_archive_page,
                                          dont_filter=True)

    def parse_archive_page(self, response):
        product_url_xpath = "//h3/a[@itemprop='url']/@href"
        urls = self.extract_list(response.xpath(product_url_xpath))

        for product_url in urls:
            yield response.follow(product_url, callback=self.parse_product)

    def parse_product(self, response):
        review_xpaths = {
            "SourceTestRating": "translate(string(count(//div"
            "[div[contains(@class,'homepagelink')] and @class='row']/"
            "preceding::span[contains(@class,'star')][1]/../span[not"
            "(contains(@class,'inactive'))])),'0','')",
            "TestDateText": "//span[contains(@class,'date')]/@content",
            "TestPros": "//*[starts-with(normalize-space(),'Pro')]"
            "/following-sibling::ul/li/text()",
            "TestCons": "//*[starts-with(normalize-space(),'Contra')]"
            "/following-sibling::ul/li/text()",
            "TestSummary": "//p[contains(@class,'lead')]/text()",
            "Author": "//meta[@name='author']/@content",
            "TestTitle": "//meta[@property='og:title']/@content"
        }
        original_url = response.url
        product = ProductItem()
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        product['TestUrl'] = original_url
        # sid
        source_internal_id = unquote(response.url).split('-')[-1].split('.')[0]
        product['source_internal_id'] = source_internal_id
        # PicUrl
        pic_url = self.extract(response.xpath(
            "//meta[@property='og:image']/@content"))
        product['PicURL'] = pic_url
        # ocn
        original_category_name = "//meta[@name='j_tags']/@content"
        product['OriginalCategoryName'] = self.extract(response.xpath(
            original_category_name)).split(',')[-2]  

        title = review['TestTitle']
        if 'im' in title:
            product_name = title.split('im')[0]
        elif ':' in title:
            product_name = title.split(':')[0]
        else:
            product_name = title
        product['ProductName'] = product_name
        review['ProductName'] = product_name
        review['source_internal_id'] = source_internal_id
        review['DBaseCategoryName'] = 'PRO'

        test_verdict_xpath = 'string(//*[text()=(//*[starts-with('\
            'normalize-space(),"Fazit") or starts-with(normalize-space(),'\
            '"FAZIT") or contains(.,"fazit")]/../*[(name()="span" and '\
            './preceding-sibling::*[position()=1 and starts-with(.,"Fazit")]'\
            ' and not(//*[name()="p" or name()="h2"][starts-with(.,"Fazit")'\
            ' or starts-with(.,"FAZIT") or contains(.,"fazit")])) or '\
            '(name()="p" and (starts-with(.,"Fazit") or starts-with(.,"FAZIT"'\
            ') or contains(.,"fazit") or preceding-sibling::h2[starts-with'\
            '(.,"Fazit") or starts-with(.,"FAZIT") or contains(.,"fazit")])'\
            ' and not(preceding-sibling::p[preceding-sibling::h2[starts-with'\
            '(.,"Fazit") or starts-with(.,"FAZIT") or '\
            'contains(.,"fazit")]]))]//text())]|//*[@class='\
            '"inline_plusminuslist__headline"][contains(text(), "Fazit")]'\
            '/following-sibling::span/text())'

        review["TestVerdict"] = self.extract(response.xpath(
            test_verdict_xpath))

        if review["SourceTestRating"]:
            review["SourceTestScale"] = TESTSCALE
        yield product
        yield review
    
