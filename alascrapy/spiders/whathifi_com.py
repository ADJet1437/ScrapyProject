# -*- coding: utf-8 -*-

from datetime import datetime


from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils


class Whathifi_comSpider(AlaSpider):
    name = 'whathifi_com'
    allowed_domains = ['www.whathifi.com']
    start_urls = ['https://www.whathifi.com/products/headphones',
                  'https://www.whathifi.com/products/tvs',
                  'https://www.whathifi.com/products/tablets-and-smartphones',
                  'https://www.whathifi.com/products/home-cinema',
                  'https://www.whathifi.com/products/portable',
                  'https://www.whathifi.com/products/digital-tv-boxes',
                  'https://www.whathifi.com/products/all-in-one-systems',
                  'https://www.whathifi.com/products/games-consoles',
                  'https://www.whathifi.com/products/streaming',
                  'https://www.whathifi.com/products/hi-fi', ]

    def __init__(self, *args, **kwargs):
        super(Whathifi_comSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):
        ocn_xpath = '//h1/text()'
        ocn = self.extract(response.xpath(ocn_xpath))

        category = ocn.split(' reviews')[0]

        urls_xpath = '//div[@data-page="1"]/a/@href'
        urls = self.extract_list(response.xpath(urls_xpath))

        for url in urls:
            yield response.follow(url, callback=self.parse_page,
                                  meta={'category': category})

    def parse_page(self, response):
        product_xpaths = {
            'PicURL': '//meta[@property="og:image"]/@content',
            'TestUrl': '//meta[@property="og:url"]/@content'
        }

        review_xpaths = {
            'TestSummary': '//meta[@property="og:description"]/@content',

            'Author': '//span[@class="no-wrap by-author"]//text()',

            'TestDateText': 'substring-before(//time/@datetime, "T")',

            'TestUrl': '//meta[@property="og:url"]/@content',
            'TestVerdict': '//div[@class="sub-box full"]/p/text()',
            'TestPros': '//div[@class="sub-box"][1]/ul/li/text()',
            'TestCons': '//div[@class="sub-box"][2]/ul/li/text()',
        }

        product = self.init_item_by_xpaths(response, 'product', product_xpaths)
        review = self.init_item_by_xpaths(response, 'review', review_xpaths)

        title_xpath = '//h1/text()'
        title = self.extract(response.xpath(title_xpath))
        productname = title.split(' review')[0]
        if 'Hands on:' in productname:
            productname = productname.split(': ')[1]
        else:
            productname = productname

        category = response.meta.get('category')
        product['OriginalCategoryName'] = category

        review['TestTitle'] = title
        review['ProductName'] = productname
        product['ProductName'] = productname

        rating_xpath = '//meta[@itemprop="ratingValue"]/@content'
        rating = self.extract(response.xpath(rating_xpath))

        SCALE = 5

        if rating:
            review['SourceTestRating'] = rating
            review['SourceTestScale'] = SCALE

        review['DBaseCategoryName'] = 'PRO'
        source_int_id = response.url
        source_internal_id = source_int_id.split('/')[-1]

        review['source_internal_id'] = source_internal_id
        product['source_internal_id'] = source_internal_id

        review_date = datetime.strptime(review['TestDateText'], "%Y-%m-%d")

        if review_date > self.stored_last_date:
            yield review
            yield product
