# -*- coding: utf8 -*-
from datetime import datetime
import re


from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils


class Smarthouse_com_auSpider(AlaSpider):
    name = 'smarthouse_com_au'
    allowed_domains = ['smarthouse.com.au']
    start_urls = ['https://www.smarthouse.com.au/category/reviews/']

    def __init__(self, *args, **kwargs):
        super(Smarthouse_com_auSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):

        urls_xpath = '//div[@class="cb-meta clearfix"]/h2/a/@href'
        urls = self.extract_list(response.xpath(urls_xpath))
        for url in urls:
            yield response.follow(url, callback=self.parse_page)

        next_page_xpath = '//nav/a/@href'
        next_page = response.xpath(next_page_xpath).get()

        if next_page:
            last_date_xpath = '//article[@id][last()]//@datetime'
            last_date = self.extract(response.xpath(last_date_xpath))
            date_time = datetime.strptime(last_date, '%Y-%m-%d')
            if date_time > self.stored_last_date:
                yield response.follow(next_page, callback=self.parse)

    def parse_page(self, response):

        product_xpaths = {
            'PicURL': '//meta[@property="og:image"]/@content',
            'TestUrl': '//meta[@property="og:url"]/@content',

            'OriginalCategoryName': '//meta[@property="article:tag"]'
                                    '[last()]/@content|//span[@class'
                                    '="cb-category cb-element"][last()]'
                                    '/a/text()',
        }

        review_xpaths = {

            'TestSummary': '//meta[@property="og:description"]/@content',

            'TestDateText': 'substring-before(//meta[@property='
                            '"article:published_time"]/@content, "T")',

            'TestVerdict': '//span[@itemprop="reviewBody"]/p[last()-1]/text()|'
                           '//span[@itemprop="reviewBody"]/p[last()-2]/text()|'
                           '//strong[text()="Conclusion"]/following::p[1]//'
                           'text()',

            'Author': '//span[@class="cb-byline"]/text() |'
                      ' //span[@class="fn"]/text()',

            'TestUrl': '//meta[@property="og:url"]/@content',
        }

        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        product = self.init_item_by_xpaths(response, "product", product_xpaths)

        title_xpath = '//h1/text()'
        title = self.extract(response.xpath(title_xpath))
        if ': ' in title:
            productname = title.split(': ')[1]
        else:
            productname = title
        review["DBaseCategoryName"] = "PRO"
        review['TestTitle'] = title
        review['ProductName'] = productname
        product['ProductName'] = productname
        source_int_id_xpath = '//body/@class'
        source_int_id = self.extract(response.xpath(source_int_id_xpath))
        s_internal_id = re.search('postid-(.*) single-format', source_int_id)
        source_internal_id = s_internal_id.group(1)
        review['source_internal_id'] = source_internal_id
        product['source_internal_id'] = source_internal_id

        rating1_xpath = '//span[@class="score"]/text()'

        rating1 = self.extract(response.xpath(rating1_xpath))

        SCALE = 10

        if rating1:
            review['SourceTestRating'] = rating1
            review['SourceTestScale'] = SCALE

        yield review
        yield product
