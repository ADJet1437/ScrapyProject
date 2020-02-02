from datetime import datetime
from alascrapy.items import ProductItem, ReviewItem
import re
from alascrapy.lib.generic import date_format
from dateparser import parse
from alascrapy.lib.dao import incremental_scraping as incremental_utils
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider


class Tweakers_netSpider(AlaSpider):
    name = 'tweakers_net'
    allowed_domains = ['tweakers.net']
    start_urls = ['https://tweakers.net/reviews/']
    PRO_FILTER = 'q1bKLEnNDaksSC1Wsoo2jNVRyi9KSS1yy0zNSVGyUir'\
                 'JzE1V0lEqSExPDc6sSlWyMjQw0FEqSizJzEv3zcxTsjKoBQA'
    USER_FILER = 'q1bKLEnNDaksSC1Wsoo2NDAyidVRyi9KSS1yy0zNSVGyUir'\
                 'JzE1V0lEqSExPDc6sSlWyMjQw0FEqSizJzEv3zcxTsjKoBQA'

    def __init__(self, *args, **kwargs):
        super(Tweakers_netSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):
        print('start url {}'.format(response.url))
        cat_xpaths = '//li[contains(@class, "more")]//div[contains(@class,"sublist")]//ul//li//a/@href'
        cat_links = response.xpath(cat_xpaths).extract()

        must_include_cats = ['822', '215', '496', '713', '621', '453', '436',
                             '930', '959', '344']

        for important_cat in must_include_cats:
            for cat in cat_links:
                if important_cat not in cat:
                    continue
                pro_review_urls = cat + '?currFilters=' + self.PRO_FILTER
                user_review_urls = cat + '?currFilters=' + self.USER_FILER
                yield response.follow(url=pro_review_urls,
                                      callback=self.incremental)
                yield response.follow(url=user_review_urls,
                                      callback=self.incremental)

    def get_date_format(self, date_str):
        if date_str.format("%m-'%Y"):
            date1 = date_str.replace("'", "20")
            date = parse(date1, settings={'PREFER_DAY_OF_MONTH': 'first'})
            return date
        else:
            date = parse(date_str, settings={'PREFER_DATES_FROM': 'past'})
            return date

    def get_review_type(self, response):
        url = response.url
        if self.PRO_FILTER in url:
            review_type = 'PRO'
            return review_type
        if self.USER_FILER in url:
            review_type = 'USER'
            return review_type
        return None

    def incremental(self, response):
        contents = response.xpath("//table[@class='listing useVisitedState']")
        for content in contents:
            date_str = self.extract(content.xpath(".//span[@class='date']/text()"))
            date = self.get_date_format(date_str)
            #print("entering next page, the date is: {}".format(date))
            if date > self.stored_last_date:
                review_type = self.get_review_type(response)
                review_urls = content.xpath('.//p[contains(@class, "title")]/a/@href').extract()
                for review_url in review_urls:
                    if review_type == 'PRO':
                        yield response.follow(url=review_url,
                                              callback=self.parse_pro_review)
                    if review_type == 'USER':
                        yield response.follow(url=review_url,
                                              callback=self.parse_user_review)

        # next page
        next_page_xpath = '//a[@class="next"]/@href'
        next_page_link = self.extract(response.xpath(next_page_xpath))
        if next_page_link:
            date_str = self.extract(response.xpath("(//span[@class='date']/text())[last()]"))
            date = self.get_date_format(date_str)
            #print("entering next page, the date is: {}".format(date))
            if date > self.stored_last_date:
            #print("entering next page, the url is: {}".format(next_page_link))
                yield response.follow(url=next_page_link, callback=self.incremental)

    def get_product_name(self, response):
        title_xpath = '//header[@class="title"]/h1/text() |'\
                      ' //header/h1/a/text()'
        title = self.extract(response.xpath(title_xpath))
        product_name = title

        if not title:
            return None
        if 'Review' in title:
            product_name = title.split('Review')[0].strip()
        if '<h1>' in product_name:
            product_name = product_name.split('<h1>')[1]
        return product_name

    def get_source_rating(self, response):
        rating_xpath = '//img[@class="score-shield"]//@title'
        rating = self.extract(response.xpath(rating_xpath))
        if rating and ':' in rating:
            rating = rating.split(':')[1].strip()
            rating = rating.replace(',', '.')
            return rating
        else:
            return 0

    def parse_pro_review(self, response):
        review_xpaths = {
            'Author': '//p[@class="name"]/a/font/font/text()'
                      ' | //p[@class="name"]/a/text() | '
                      '//p[@class="name"]/text()',
            'TestCons': '//div[@class="cons"]/ul/li//text()',
            'TestPros': '//div[@class="pros"]/ul/li//text()',
            'TestSummary': '//meta[@property="og:description"]/@content',
            'TestTitle': '//meta[@property="og:title"]/@content',
            'TestVerdict': '//div[@class="bottomline"]//text()',
        }

        review = self.init_item_by_xpaths(response, 'review', review_xpaths)
        print(response.url)

        review["ProductName"] = self.get_product_name(response)
        TESTSCALE = 10

        rating = self.get_source_rating(response)
        if rating:
            review['SourceTestRating'] = rating
            review['SourceTestScale'] = TESTSCALE
        review['source_internal_id'] = str(response.url).split('/')[4]

        review['DBaseCategoryName'] = 'PRO'

        date_xpath = '//span[@class="articleMeta"]/span/text()'
        full_date = self.extract(response.xpath(date_xpath))
        f_date = full_date.lstrip()
        date = f_date[2:12]
        date_str = date_format(date, "%d %m %Y")
        review_date = datetime.strptime(date_str, "%Y-%m-%d")
        if self.stored_last_date > review_date:
            return

        review['TestDateText'] = date_str
        review['source_internal_id'] = str(response.url).split('/')[4]
        s_i_d = review['source_internal_id']

        product_xpaths = {
            'TestUrl': '//meta[@property="og:url"]/@content',
            'PicURL': '//meta[@property="og:image"]/@content',
            'OriginalCategoryName': '//li[@id="tweakbaseBreadcrumbCategory"]/'
                                    'a/text()'
        }

        product = self.init_item_by_xpaths(response, 'product', product_xpaths)
        product["ProductName"] = self.get_product_name(response)
        product['source_internal_id'] = s_i_d

        yield review
        yield product

    def parse_user_review(self, response):
        review_xpaths = {
            'Author': '//a[@class="username"]/font/font/text() |'
                      ' //a[@class="username"]/text()',
            'TestCons': '//div[@class="cons"]/ul/li//text()',
            'TestPros': '//div[@class="pros"]/ul/li//text()',
            'TestSummary': '//meta[@property="og:description"]/@content',
            'TestTitle': '//meta[@property="og:title"]/@content',
            'TestVerdict': '//div[@class="bottomline"]//text()'
        }

        review = self.init_item_by_xpaths(response, 'review', review_xpaths)
        review["ProductName"] = self.get_product_name(response)
        review['DBaseCategoryName'] = 'USER'
        USER_SCALE = 5

        rating_xpath = '//div[@class="scoreEmblem"]/span//text()'
        rating = self.extract(response.xpath(rating_xpath))
        if rating:
            full_rate = str(rating).split(' ')[1]
            review['SourceTestRating'] = full_rate
            review['SourceTestScale'] = USER_SCALE

        date_xpath = 'substring-before(//span[@class="date"]/text(),",")'
        date = self.extract(response.xpath(date_xpath))
        date_str = date_format(date, "%d %b %Y")
        review_date = datetime.strptime(date_str, "%Y-%m-%d")
        if self.stored_last_date > review_date:
            return
        review['TestDateText'] = date_str
        review['source_internal_id'] = str(response.url).split('/')[4]
        s_i_d = review['source_internal_id']

        product_xpaths = {
            'TestUrl': '//meta[@property="og:url"]/@content',
            'PicURL': '//meta[@property="og:image"]/@content',
            'OriginalCategoryName': '//li[@id="tweakbaseBreadcrumbCategory"]/'
                                    'a/text()'
        }

        product = self.init_item_by_xpaths(response, 'product', product_xpaths)
        product["ProductName"] = self.get_product_name(response)
        product['source_internal_id'] = s_i_d

        yield review
        yield product