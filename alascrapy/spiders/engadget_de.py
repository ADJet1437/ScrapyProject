# -*- coding: utf8 -*-

from datetime import datetime

from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_text_from_selector, get_full_url


class EngadgetDeSpider(AlaSpider):
    name = 'engadget_de'
    allowed_domains = ['engadget.com']
    start_urls = ['http://de.engadget.com/tag/review/']

    def parse(self, response):
        """
        Handle the reviews index page on the-digital-picture and split it into pages to scrape

        :param response: The response from the requested page
        :return: Either a review or a request
        """

        review_urls = self.extract_list(
            response.xpath('//*[@class="post-mini"]/a/@href'))

        for review_url in review_urls:
            request = Request(review_url, callback=self.parse_review)
            yield request

        next_page_xpath = '//*[@class="post-pagination"]/li[@class="older"]/a/@href'
        next_page_rel_url = self.extract(response.xpath(next_page_xpath))

        next_page_url = get_full_url(response, next_page_rel_url)
        request = Request(next_page_url, callback=self.parse)
        yield request

    def parse_review(self, response):

        product_xpaths = { "ProductName": "//*[@class='post-gallery']/*[@class='title']/text()",
                           "PicURL": "//*[@property='og:image']/@content"
                         }

        review_xpaths = { "TestTitle": "//*[@itemprop='headline']/text()",
                          "Author": "//*[@itemprop='author']/text()",
                          "TestDateText": "//*[@class='timeago']/@datetime"
                        }

        content_xpath = "//*[@itemprop='articleBody']"
        content_selector = response.xpath(content_xpath)

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        review_content = get_text_from_selector(content_selector[0], 
            "object", "script", "head", "p", "table")

        review_content = review_content.strip().split('\n', 1) # Summary is only the first paragraph
        review["TestSummary"] = review_content[0] 

        if not product["ProductName"]:
            product["ProductName"] = review["TestTitle"]

        review["TestUrl"] = response.url
        review["ProductName"] = product["ProductName"]
        
        if("(Video)" in review["TestTitle"] or 
            "(Videos)" in review["TestTitle"]):
            review["DBaseCategoryName"] = "VPRO"
        else:
            review["DBaseCategoryName"] = "PRO"

        review["TestDateText"] = datetime.strptime(review["TestDateText"][0:-6], 
            "%Y-%m-%dT%H:%M:%S").strftime('%Y-%m-%d %H:%M:%S')

        yield product
        yield review




