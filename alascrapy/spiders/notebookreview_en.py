# -*- coding: utf8 -*-
from datetime import datetime

from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ReviewItem, ProductItem

TEST_SCALE = 5


class Notebookreview_enSpider(AlaSpider):
    name = 'notebookreview_en'
    allowed_domains = ['notebookreview.com']
    start_urls = ['http://www.notebookreview.com/notebookreview/',
                    'http://www.notebookreview.com/phonereview/',
                    'http://www.notebookreview.com/desktopreview/',
                    'http://www.notebookreview.com/printerreview/',
                    'http://www.notebookreview.com/brands/laptop/dell/notebookreview/',
                    'http://www.notebookreview.com/brands/laptop/msi-computer/',
                    'http://www.notebookreview.com/brands/laptop/hp/notebookreview/',
                    'http://www.notebookreview.com/brands/laptop/lenovo/notebookreview/']

    def __init__(self, *args, **kwargs):
        super(Notebookreview_enSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):

        review_divs_xpath = "//section[@class='contentListContainer']"
        review_divs = response.xpath(review_divs_xpath)

        for review_div in review_divs:
            date_xpath = "//div[@class='meta-container']/time[@class='publishDate']/@datetime"
            dates = (response.xpath(date_xpath)).getall()
            for date in dates:
                review_date = datetime.strptime(date, '%Y-%m-%d')
                if review_date > self.stored_last_date:
                    review_urls_xpath = ".//h4/a/@href"
                    body_review_urls = (review_div.xpath(review_urls_xpath)).getall()
                    featured_review_xpath = "//h1[@id='headline']/a/@href"
                    featured_review = response.xpath(featured_review_xpath).extract()
                    review_urls = featured_review + body_review_urls
                    for review_url in review_urls:
                        yield Request(url=review_url, callback=self.parse_product)

        next_page_xpath = "//a[@rel='next']/@href"
        next_page = self.extract(response.xpath(next_page_xpath))

        review_date_xpath = "//div[@class='contentListItem'][last()]//time/@datetime"
        review_date = self.extract(response.xpath(review_date_xpath))
        oldest_review_date = datetime.strptime(review_date, '%Y-%m-%d')

        if next_page:
            if oldest_review_date > self.stored_last_date:
                yield response.follow(next_page, callback=self.parse)

    def parse_product(self, response):

        product_xpaths = {
            'PicURL': '//meta[@name="twitter:image"]/@content',
            'source_internal_id': "substring-after(//link[@rel='shortlink']"
            "/@href, '=')"
        }

        product = self.init_item_by_xpaths(response, 'product', product_xpaths)

        ocn_xpath = "//div[@class='breadcrumbs']/a[last()-1]/text()|"\
            "//div[@class='breadcrumbs']/a[last()]/text()"
        original_category_name = self.extract_all(
            response.xpath(ocn_xpath), " | ")
        product["OriginalCategoryName"] = original_category_name\
            .replace('Reviews', ' ').replace('Home', ' ')

        review_xpaths = {
            'TestTitle': '//meta[@name="twitter:title"]/@content',
            'Author': '//span[@itemprop="name"]/text()',
            'source_internal_id': "substring-after(//link[@rel='shortlink']"
            "/@href, '=')",
            "SourceTestRating": '//span[@class="star-rating-container"]'
            '/@data-score',
            "TestDateText": "//time[@itemprop='datePublished']/@datetime",
            'TestSummary': '//meta[@name="twitter:description"]/@content',
            'TestPros': '(//h2[@class="title"]/following-sibling::ul)'
            '[1]/li/text()|(//h2[@class="title"]/following-sibling::ul)[1]'
            '/li/span/text()',
            'TestCons': '(//h2[@class="title"]/following-sibling::ul)'
            '[2]/li/text()| //h2[@class="title"]/following-sibling::p/text()|'
            '(//h2[@class="title"]/following-sibling::ul)[1]/li/span/text()',
            'TestVerdict': '//h2[contains(text(),"Quick")]/'
            'following-sibling::p/text()'
        }

        review = self.init_item_by_xpaths(response, 'review', review_xpaths)
        date_time_to_compare = datetime.strptime(review['TestDateText'],
                                                 '%Y-%m-%d')
        if date_time_to_compare < self.stored_last_date:
            return

        product_name = self.extract(response.xpath('substring-before(//meta[@name="twitter:title"]/@content, "Review")'))
        if not product_name:
            product_name = str(review['TestTitle']).split("Review")[0].split(":")[0]

        review['ProductName'] = product_name
        product['ProductName'] = product_name

        if review["SourceTestRating"]:
            review["SourceTestScale"] = TEST_SCALE

        review['DBaseCategoryName'] = 'PRO'

        yield product
        yield review
