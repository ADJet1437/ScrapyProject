# -*- coding: utf8 -*-
from datetime import datetime


from alascrapy.lib.dao import incremental_scraping as incremental_utils
from alascrapy.spiders.base_spiders import ala_spider as spiders


class XatakaComSpider(spiders.AlaSpider):
    name = 'xataka_com'
    allowed_domains = ['xataka.com']
    start_urls = ['https://www.xataka.com/categoria/analisis']

    def __init__(self, *args, **kwargs):
        super(XatakaComSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):
        xpaths = {
            'review_links': '//h2[@class="abstract-title"]/a/@href',
            'next_page': '//li/a[@rel="next"]/@href'
        }
        review_links = response.xpath(xpaths['review_links']).extract()
        next_page_link = response.xpath(xpaths['next_page']).extract()

        if len(next_page_link) > 0:
            last_date_xpath = 'substring-before(//article[@class="recent-'\
                'abstract abstract-article m-featured"]'\
                '/div/footer//time/@datetime, "T")'

            last_date = self.extract(response.xpath(last_date_xpath))
            date_time = datetime.strptime(last_date, '%Y-%m-%d')
            if date_time > self.stored_last_date:
                yield response.follow(url=next_page_link[0],
                                      callback=self.parse)

            # yield response.follow(url=next_page_link[0], callback=self.parse)

        for link in review_links:
            yield response.follow(url=link, callback=self.parse_review_page)

    def parse_review_page(self, response):
        product_xpaths = {
            'PicURL': '//meta[@property="og:image"]/@content',
        }

        review_xpaths = {
            'TestDateText': 'substring-before(//meta'
            '[@property="og:updated_time"]/@content, "T")',

            'TestSummary': '//meta[@property="og:description"]/@content',
            'TestTitle': '//meta[@property="og:title"]/@content',
            'Author': '//a[@class="article-author-link"]//text()',
        }

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        product_name_xpath_alt = '//meta[@property="og:title"]/@content'
        title = self.extract(response.xpath(product_name_xpath_alt))

        if ',' in title:
            productname = title.split(',')[0]

        else:
            productname = title

        review['ProductName'] = productname
        product['ProductName'] = productname

        pic_url = self.extract(response.xpath(
            '//meta[@property="og:image"]/@content'))
        # https://i.blogs.es/b70e41/galaxy-s9-05/840_560.jpg
        # Split result: ['https:', '', 'i.blogs.es', 'b70e41', ...]
        # Gets 4th attribute (array index 3) as to use as ssi
        SSI_SPLIT_INDEX = 3
        sid = pic_url.split('/')[SSI_SPLIT_INDEX]

        product['source_internal_id'] = sid
        review['source_internal_id'] = sid

        ocn_xpath = '//div[@class="article-topics-list"]/ul'\
                    '[@class="article-topics-categories"]/li[1]//text()'
        ocn = self.extract(response.xpath(ocn_xpath))
        product['OriginalCategoryName'] = ocn

        product['TestUrl'] = response.url
        review['TestUrl'] = response.url

        SCALE = 10

        rating_xpath = '//div[@class="nota-analisis"]/p//text()'

        rating = self.extract(response.xpath(rating_xpath))
        if rating:
            review['SourceTestRating'] = rating
            review['SourceTestScale'] = SCALE

        review['DBaseCategoryName'] = 'PRO'

        yield product
        yield review
