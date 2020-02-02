# -*- coding: utf8 -*-

from datetime import datetime
import re

from scrapy.http import Request

from alascrapy.lib.selenium_browser import SeleniumBrowser, uses_selenium
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format, strip
from alascrapy.items import CategoryItem
from alascrapy.lib.dao.incremental_scraping import is_product_in_db_by_sii

class MediaworldITSpider(AlaSpider):
    name = 'mediaworld_it'
    allowed_domains = ['mediaworld.it']
    start_urls = ['https://www.mediaworld.it/mw/servlet/LoadEditorialContentView?catalogId=20000&storeId=20000&content=/magazine/Recensioni%3F.html',
                  'http://www.mediaworld.it/mw/servlet/LoadEditorialContentView?catalogId=20000&storeId=20000&content=/magazine/categoria/tablet%3F.html',
                  'http://www.mediaworld.it/mw/servlet/LoadEditorialContentView?catalogId=20000&storeId=20000&content=/magazine/categoria/telefonia%3F.html',
                  'http://www.mediaworld.it/mw/servlet/LoadEditorialContentView?catalogId=20000&storeId=20000&content=/magazine/categoria/TV%3F.html',
                  'http://www.mediaworld.it/mw/servlet/LoadEditorialContentView?catalogId=20000&storeId=20000&content=/magazine/Living%20Room%3F.html'
                  ]

    @uses_selenium
    def parse(self, response):
        iframe_xpath = "//iframe[@id='mainframe']"
        review_url_xpath = "//div[@class='title']/a/@href"
        review_re = 'magazine/\d+/\d+/\d+/(\d+)/'
        continue_next_page = False
        with SeleniumBrowser(self, response) as browser:
            browser.get(response.url)
            selector = browser.switch_to_frame(iframe_xpath)

            next_page_xpath = "//a[@class='next_page']/@href"
            review_urls = self.extract_list(selector.xpath(review_url_xpath))

            for review_url in review_urls:
                match = re.search(review_re, review_url)
                if not match:
                    print review_url
                    continue
                source_internal_id = match.group(1)
                if not is_product_in_db_by_sii(self.mysql_manager,
                                               self.spider_conf["source_id"],
                                               source_internal_id):
                    continue_next_page=True
                    review_url = get_full_url(response.url, review_url)
                    request = Request(review_url, callback=self.parse_review)
                    request.meta['source_internal_id'] = source_internal_id
                    yield request

            if continue_next_page:
                next_page = self.extract(selector.xpath(next_page_xpath))
                next_page = get_full_url(response.url, next_page)
                if next_page:
                    request = Request(next_page, callback=self.parse)
                    yield request

    def continue_to_next_page(self, selector):
        if not self.stored_last_date:
            return True

        review_date_xpath = "//span[@class='date']/text()"
        review_dates = self.extract_list(selector.xpath(review_date_xpath))
        last_date = review_dates[-1]
        last_review_date = date_format(last_date, '%d %B %Y', languages=['it'])
        last_review_date = datetime.strptime(last_review_date, '%Y-%m-%d')
        if self.stored_last_date > last_review_date:
            return False
        else:
            return True

    def parse_review(self, response):
        iframe_url_xpath = "//iframe[@id='mainframe']/@src"
        iframe_xpath = "//iframe[@id='mainframe']"
        with SeleniumBrowser(self, response) as browser:
            selector = browser.get(response.url)
            iframe_url = self.extract(selector.xpath(iframe_url_xpath))
            if iframe_url[0:2]=='//':
                iframe_url = "http:%s" % iframe_url            

            selector = browser.switch_to_frame(iframe_xpath)    
            category_xpath = "//div[@class='subheading']/text()"
            category = CategoryItem()
            category['category_path'] = self.extract(selector.xpath(category_xpath))
            category['category_leaf'] = category['category_path']
            yield category

            product_xpaths = { "PicURL": "//div[@class='cover-image']/img/@src"}

            review_xpaths = { "TestTitle": "//h2[@class='story-title']/text()",
                              "TestVerdict": "//p[@class='story-blurb']/text()",
                              "TestSummary": "(//div[@class='story-block']//p[@class='magazine-regular-text' and text()])[1]//text()",
                              "Author": "//span[@class='author']/text()"
            }

            summary_alt_xpath = "//div[@class='content']//div[@class='text']//text()"
            pic_alt_xpath = "//div[@class='content']//div[@class='image']/img/@src"


            product = self.init_item_by_xpaths(response, "product", product_xpaths, selector=selector)
            review = self.init_item_by_xpaths(response, "review", review_xpaths, selector=selector)

            product['source_internal_id'] = response.meta['source_internal_id']
            review['source_internal_id'] = product['source_internal_id']

            if not product["PicURL"]:
                product["PicURL"] = self.extract_xpath(selector, pic_alt_xpath)

            if not review["TestSummary"]:
                review["TestSummary"] = self.extract_xpath(selector, summary_alt_xpath)

            product["PicURL"] = get_full_url(iframe_url, product["PicURL"])
            product["OriginalCategoryName"]=category['category_path']
            product_name_re = "([^:,]+)[:,]?"
            name_match = re.search(product_name_re, review["TestTitle"])
            if name_match:
                product["ProductName"] = strip(name_match.group(1))
                review["ProductName"] = product["ProductName"]
            else:
                product["ProductName"] = review["TestTitle"]
                review["ProductName"] = review["TestTitle"]


            review["DBaseCategoryName"] = "PRO"
            date_xpath = "//span[@class='date']/text()"
            test_date_string = self.extract(selector.xpath(date_xpath))
            if test_date_string:
                review["TestDateText"] = date_format(test_date_string, '%d %B %Y',
                                                     languages=['it'])

            yield product
            yield review