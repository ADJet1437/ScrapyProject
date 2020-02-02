# -*- coding: utf8 -*-

__author__ = 'zaahid'
import dateparser
from datetime import datetime
from scrapy.http import Request
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import date_format
from alascrapy.items import ProductIdItem, ProductItem, ReviewItem
import alascrapy.lib.dao.incremental_scraping as incremental_utils


class Notebookcheck_bizSpider(AlaSpider):
    name = 'notebookcheck_biz_new'
    allowed_domains = ['notebookcheck.biz']
    start_urls = ['https://www.notebookcheck.biz/Critiques.114.0.html']

    def __init__(self, *args, **kwargs):
        super(Notebookcheck_bizSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):

        review_divs_xpath = '//*[@id="introa_content_1824985"]'
        review_divs = response.xpath(review_divs_xpath)
        for review_div in review_divs:
            date_xpath = './/div[@class="introa_fulldate"]/text()'
            dates = (review_div.xpath(date_xpath)).getall()
            for date in dates:
                review_date = dateparser.parse(date, date_formats=['%d.%m.', '%d.%m.%Y'])
                #print("Review Date is: {}".format(review_date))
                if review_date > self.stored_last_date:
                    review_url_xpath = './a//@href'
                    review_urls = (review_div.xpath(review_url_xpath)).getall()
                    for review_url in review_urls:
                        yield Request(url=review_url, callback=self.parse_items)

        next_page_xpath = '//a[@class="introa_page_buttons"]//@href'
        next_page = response.xpath(next_page_xpath).getall()[-1]

        review_date_xpath = '//div[@class="introa_fulldate"][last()]/text()'
        review_date = self.extract(response.xpath(review_date_xpath))
        oldest_review_date = dateparser.parse(review_date, date_formats=['%d.%m.', '%d.%m.%Y'])

        if next_page:
            if oldest_review_date > self.stored_last_date:
                yield response.follow(next_page, callback=self.parse)
        else:
            print('No next page found: {}'.format(self.stored_last_date))

    def parse_items(self, response):

        review = ReviewItem()
        review['source_internal_id'] = str(response.url).split(".")[3]
        source_internal_id = review['source_internal_id']
        review['ProductName'] = str(self.extract(response.xpath('//*[@class="specs_header"]/text()[1]'))).strip(' (')
        if review['ProductName']:
            product_name = review['ProductName']
        else:
            review['ProductName'] = str(response.url).split('/')[3].split('.')[0].strip('Critique-complete-du-').strip('-Tests-pour-PC-portables-et-de-bureau').strip('carte-graphique').replace("-", " ")
            product_name = review['ProductName']
        date = self.extract(response.xpath("//span[@class='intro-date']/text()"))
        review["TestDateText"] = date_format(date, "%m/%d/%Y")
        review['Author'] = self.extract(response.xpath('//*[@class="intro-author"]/text()[1]'))
        review['DBaseCategoryName'] = "PRO"
        review['TestUrl'] = response.url
        review['TestTitle'] = self.extract(response.xpath("//div[@class='tx-nbc2fe-intro']/div[@class='nbcintro']/h1/text()"))
        test_summary = self.extract(response.xpath('//div[@class="tx-nbc2fe-intro"]/div[@class="nbcintro"]/p[@class="align-justify"]/text()[2]'))
        if test_summary:
            review['TestSummary'] = test_summary
        else:
            review['TestSummary'] = self.extract(response.xpath('//meta[@name="description"]/@content'))
        source_test_rating = self.extract(response.xpath("//*[@id='bewertung']/div/div[15]/div[1]//span[@class='average']/text()"))
        if source_test_rating:
            review['SourceTestRating'] = str(source_test_rating).rstrip('%')
            review['SourceTestScale'] = '100'
        yield review

        product = ProductItem()
        product['source_internal_id'] = source_internal_id
        product['ProductName'] = product_name
        product['TestUrl'] = response.url
        picture_src = self.extract(response.xpath('//meta[@property="og:image"]/@content'))
        if picture_src:
            product['PicURL'] = picture_src
        yield product

        product_id = ProductIdItem()
        product_id['ProductName'] = product_name
        product_id['source_internal_id'] = source_internal_id
        price = response.xpath('//a/div[@class="cell_left"][1]/span[@class="totalprice"]').extract()
        if price:
            product_id['ID_kind'] = 'price'
            product_id['ID_value'] = price
            yield product_id