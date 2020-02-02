# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.lib.generic import date_format
from datetime import datetime


class PhonescoopComSpider(AlaSpider):
    name = 'phonescoop_com'
    allowed_domains = ['www.phonescoop.com']
    start_urls = ['https://www.phonescoop.com/articles/reviews.php']

    def __init__(self, *args, **kwargs):
        super(PhonescoopComSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

    def parse(self, response):
        urls_xpath = '//h2/a/@href'
        urls = self.extract_list(response.xpath(urls_xpath))

        for url in urls:
            yield response.follow(url, callback=self.parse_review)

        # incremental
        last_date_xpath = 'substring-before(//p[@class="newsmeta"], " by")'
        last_test_day = self.extract(response.xpath(last_date_xpath))
        date_str = date_format(last_test_day, '%Y-%m-%d')
        date_time = datetime.strptime(date_str, '%Y-%m-%d')
        if date_time < self.stored_last_date:
            return


        next_page_xpath = '//div[@class="pgbn"]/a/@href'
        next_page = self.extract(response.xpath(next_page_xpath))

        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_review(self, response):
        product_xpaths = {
            'PicURL': '//meta[@property="og:image"]/@content',
            'OriginalCategoryName': '//div[@id="breadcru"]/a[2]/text()',
            'TestUrl': '//meta[@property="og:url"]/@content'
        }

        review_xpaths = {
            'TestSummary': '//meta[@name="twitter:description"]/@content',

            'Author': '//div[@id="content"]/p[2]/a[1]/text()',
            'TestUrl': '//meta[@property="og:url"]/@content',
            'TestVerdict': '//div[@id="artpgarea"]/p[last()]/text()'
        }

        product = self.init_item_by_xpaths(response, 'product', product_xpaths)
        review = self.init_item_by_xpaths(response, 'review', review_xpaths)

        title_xpath = '//meta[@property="og:title"]/@content'
        title = self.extract(response.xpath(title_xpath))

        if ": " in title:
            productname = title.split(': ')[1]

        else:
            productname = title

        date_xpath = 'substring-before(//p[@class="tab-bar"]/'\
                     'following-sibling::p[1], " by")'
        test_day = self.extract(response.xpath(date_xpath))[:-2]
        date_str = date_format(test_day, '%Y-%m-%d')
        date_time = datetime.strptime(date_str, '%Y-%m-%d')
        d_time = date_time.strftime('%Y-%m-%d')

        review['TestTitle'] = title
        review['ProductName'] = productname

        product['ProductName'] = productname

        source_intid = response.url
        source_int_id = source_intid.split('a=')[1]

        review['source_internal_id'] = source_int_id
        product['source_internal_id'] = source_int_id
        review['TestDateText'] = d_time

        rating_xpath = '//div[@class="halfcolt ratings"]/div/div/nobr/img/@alt'
        rating = self.extract(response.xpath(rating_xpath))
        SCALE = 5

        if rating:
            review['SourceTestRating'] = rating
            review['SourceTestScale'] = SCALE

        review['DBaseCategoryName'] = 'PRO'

        verdict_page_xapth = '//a[contains(., "Wrap-Up")]/@href'
        verdict_page = self.extract(response.xpath(verdict_page_xapth))

        if verdict_page:
            verdict_page = response.urljoin(verdict_page)
            yield scrapy.Request(verdict_page,
                                 callback=self.parse_verdict,
                                 meta={'review': review})

        else:
            yield review

        yield product

    def parse_verdict(self, response):
        review = response.meta.get('review')

        verdict_xpath = '//p[@id="pgraph1"]/text()'
        verdict = self.extract(response.xpath(verdict_xpath))

        rating_xpath = '//div[@class="halfcolt ratings"]/div/div/nobr/img/@alt'
        rating = self.extract(response.xpath(rating_xpath))
        SCALE = 5

        if rating:
            review['SourceTestRating'] = rating
            review['SourceTestScale'] = SCALE

        review['TestVerdict'] = verdict

        yield review
