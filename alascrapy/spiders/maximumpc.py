# -*- coding: utf8 -*-
from datetime import datetime

from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import set_query_parameter, get_full_url
import alascrapy.lib.dao.incremental_scraping as incremental_utils


class MaximumPCSpider(AlaSpider):
    name = 'maximumpc'
    allowed_domains = ['maximumpc.com']
    start_urls = ['http://www.maximumpc.com/reviews/']

    def __init__(self, *args, **kwargs):
        super(MaximumPCSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(self.mysql_manager, self.spider_conf["source_id"])

    def parse(self, response):
        if 'page' in response.meta:
            page = response.meta['page']
        else:
            page = 1

        review_selectors = response.xpath("//div[@id='stream']//div[contains(@class,'article_box_wrap')]")
        review_url_xpath = "./a/@href"

        for review_selector in review_selectors:
            review_url = self.extract_all(review_selector.xpath(review_url_xpath))
            review_url = get_full_url(response, review_url)
            if review_url:
                request = Request(review_url, callback=self.parse_review)
                yield request

        if self.continue_to_next_page(response):
            next_page = page+1
            next_page_url = set_query_parameter(response.url, 'page', next_page)
            request.meta['page'] = next_page
            if next_page_url:
                request = Request(next_page_url, callback=self.parse)
                yield request

    def continue_to_next_page(self, response):
        if not self.stored_last_date:
            return True

        review_date_xpath = "//div[@id='stream']" \
                            "//div[contains(@class,'article_box_wrap')]" \
                            "//span[@class='localized']/text()"
        review_dates = self.extract_list(response.xpath(review_date_xpath))
        if review_dates:
            last_review_date = review_dates[-1]
            last_review_date = datetime.strptime(last_review_date,"%b %d, %Y")
            if self.stored_last_date > last_review_date:
                return False
        return True

    def parse_review(self, response):
        product_xpaths = { "PicURL": "(//*[@property='og:image'])[1]/@content",
                           "ProductName": "//h1[@class='headline']/text()"
                         }

        review_xpaths = { "TestTitle": "//*[@property='og:title']/@content",
                          "TestSummary": "//*[@property='og:description']/@content",
                          "Author": "//*[@class='review_header']/h3/text()",
                          "TestDateText": "//*[@class='review_header']"
                                          "//span[contains(@class,'localized')]"
                                          "/text()",
                          "TestPros": "//*[@class='fancy-box']"
                                      "//strong[contains(text(),'Pros')]"
                                      "/../text()",
                          "TestCons": "//*[@class='fancy-box']"
                                      "//strong[contains(text(),'Cons')]"
                                      "/../text()",
                          "SourceTestRating": "//div[@id='review2']/@data-score"
                        }
        author_alt_xpath = "//*[@class='center_content_top']/h3/text()"
        date_alt_xpath = "//*[@class='center_content_top']//span[contains(@class,'localized')]/text()"
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        product["ProductName"] = review["TestTitle"]

        review["DBaseCategoryName"] = "PRO"
        review["ProductName"] = product["ProductName"]

        if not review['Author']:
            review['Author'] = self.extract(response.xpath(author_alt_xpath))
        if not review['TestDateText']:
            review['TestDateText'] = self.extract(response.xpath(date_alt_xpath))

        review["TestDateText"] = datetime.strptime(review["TestDateText"],
            "%b %d, %Y").strftime('%Y-%m-%d %H:%M:%S')

        yield product
        yield review



