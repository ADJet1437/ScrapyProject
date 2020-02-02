# -*- coding: utf-8 -*-
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.lib.generic import date_format
from datetime import datetime


class CnetUKSpider(AlaSpider):
    name = 'cnet_au'
    allowed_domains = ['cnet.com']
    start_urls = ['https://www.cnet.com/au/reviews/']
    custom_settings = {'COOKIES_ENABLED': True}

    def __init__(self, *args, **kwargs):
        super(CnetUKSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

    def parse(self, response):
        links_xpath = '//div[@class="assetText"]/a/@href'
        links = self.extract_list(response.xpath(links_xpath))

        for url in links:
            url = response.urljoin(url)
            yield response.follow(url, callback=self.parse_page)

        url = response.xpath("//a[@class='next']/@href").extract_first()
        next_page = response.urljoin(url)
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        else:
            print('\t NO NEXT_PAGE FOUND, HIT THE ROCK!!!!!')

    def get_product_name(self, response):
        """
        Got product name from the review page URL
        i.e. 
        typical URL: https://www.cnet.com/au/products/sony-xperia-ear-duo/preview/
        target_str: sony xperia ear duo
        """
        product_name = response.url.split('products')[-1] 
        product_name = product_name.split('/')[1]
        product_name = product_name.replace('-', ' ')

        # backup product_name
        headline_xpath = '//h1[@class="headline"]/'\
            'span/span[@class="itemreviewed"]/text() | '\
            '//meta[@property="og:title"]/@content'
        headline = self.extract(response.xpath(headline_xpath))

        if not product_name:
            product_name = headline

        return product_name

    def parse_page(self, response):
        src_int_id_xpath = "//div[@data-social='disqus']/@data-id"
        src_internal_id = self.extract(response.xpath(src_int_id_xpath))

        # get product name
        product_name = self.get_product_name(response)

        # product
        # ------------------------------------------------------------
        product_xpaths = {
            'PicURL': '//meta[@property="og:image"]/@content',
            'TestUrl': '//meta[@property="og:url"]/@content',
        }
        product = self.init_item_by_xpaths(response, 'product', product_xpaths)
        product['source_internal_id'] = src_internal_id
        product['ProductName'] = product_name

        # ocn 
        ocn1_xpath = 'substring-before(//meta[@name="news_keywords"]'\
            '/@content, ",")'
        ocn2_xpath = '//a[@class="topic-tag"]/text()'
        ocn1 = self.extract(response.xpath(ocn1_xpath))
        ocn2 = self.extract(response.xpath(ocn2_xpath))

        if ocn1:
            product['OriginalCategoryName'] = ocn1
        else:
            product['OriginalCategoryName'] = ocn2

        # review
        # ------------------------------------------------------------
        review_xpaths = {
            'TestSummary': '//meta[@property="og:description"]/@content',
            'Author': '//a[@rel="author"]/span/text()',

            'TestDateText': 'substring-before(//meta[@property="article'
            ':published_time"]/@content, "T")',

            'TestVerdict': '//p[@class="theBottomLine"]/span/text()',

            'TestPros': '//p[@class="theGood"]/span/text()',
            'TestCons': '//p[@class="theBad"]/span/text()',
            'TestTitle': '//meta[@property="og:title"]/@content'
        }
        review = self.init_item_by_xpaths(response, 'review', review_xpaths)

        # incremental
        test_day = review['TestDateText']
        date_str = date_format(test_day, '%Y-%m-%d')
        date_time = datetime.strptime(date_str, '%Y-%m-%d')
        if date_time < self.stored_last_date:
            return

        review['source_internal_id'] = src_internal_id
        review['ProductName'] = product_name
        review['DBaseCategoryName'] = 'PRO'

        # rating
        RATING_SCALE = 10
        rating_xpath = '//div[@class="col-1 overall"]/div/span/text()'
        rating = self.extract(response.xpath(rating_xpath))
        if rating:
            review['SourceTestRating'] = rating
            review['SourceTestScale'] = RATING_SCALE

        yield review
        yield product
