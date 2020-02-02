# -*- coding: utf8 -*-

from datetime import datetime
import dateparser
from scrapy.http import Request
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import date_format
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem


class TomsHardwareItSpider(AlaSpider):
    name = 'tomshardware_it'
    allowed_domains = ['tomshw.it']

    def __init__(self, *args, **kwargs):
        super(TomsHardwareItSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

        # In order to test another stored_last_date
        #self.stored_last_date = datetime(2018, 2, 8)

    def start_requests(self):
        base_url = 'https://www.tomshw.it/'
        url_cat_dict = {'Smartphone': base_url + 'notizie-smartphone/android/',
                        'Headphones, Earphones And Accessories': base_url +
                        'notizie-smartphone/cuffie-auricolari-e-accessori/',
                        'Smartwatch': base_url + '/notizie-'
                        'smartphone/smartwatch/',
                        'Laptops': base_url + 'notizie-hardware/'
                        'computer-portatili/',
                        'Monitors': base_url + '/notizie-hardware/monitor/',
                        'Printers': base_url + '/notizie-hardware/stampanti/'
                        }

        for cat in url_cat_dict:
            yield Request(url=url_cat_dict[cat],
                          callback=self.parse,
                          meta={'cat': cat})

    def parse(self, response):
        review_divs_xpath = '//section[@class="lenzuolo lenzuolo_index  "]'\
                            '//div[@class="col-12"]'
        review_divs = response.xpath(review_divs_xpath)


        date = None
        for r_div in review_divs:
            date_xpath = './/meta[@class="d-none"]/@content'
            date = r_div.xpath(date_xpath).get()
            # date looks like: 2019-08-26
            if date:  # if there's no date, it means the post is not a review.
                date = datetime.strptime(date, '%Y-%m-%d')
                if date > self.stored_last_date:
                    review_url_xpath = './/h3[@itemprop="name headline"]'\
                                        '/a/@href'
                    review_url = r_div.xpath(review_url_xpath).get()
                    yield Request(url=review_url,
                                  callback=self.parse_product_review,
                                  meta={'cat': response.meta.get('cat'),
                                        'date': date.strftime("%Y-%m-%d")})

        # Checking whether we shoudl scrape the next page
        if date and date > self.stored_last_date:
            next_page_url_xpath = '//a[@class="next page-numbers"]/@href'
            next_page_url = response.xpath(next_page_url_xpath).get()

            if next_page_url:
                yield Request(url=next_page_url,
                              callback=self.parse,
                              meta={'cat': response.meta.get('cat')})

    def parse_product_review(self, response):

        # REVIEW -------------------------------------------------------------
        review_xpaths = {
            'TestTitle': '//meta[@property="og:title"]/@content',
            'TestSummary': '//meta[@property="og:description"]/@content',
        }

        # Create the review
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        review['TestTitle'] = review['TestTitle'].replace(" | Tom's Hardware", "")

        # 'ProductName'
        review['ProductName'] = review['TestTitle'].replace(" | Tom's Hardware", "")

        # Author
        author_xpath = "//div[@class='article_author_name']/strong/a/text()"
        author = self.extract(response.xpath(author_xpath))
        if author:
            author = author
        else:
            author = u"Tom's Hardware"
        review['Author'] = author

        # 'TestDateText'
        date = response.meta.get('date')
        if not date:
            r_date = self.extract(response.xpath("//div[@class='article_author_right']/span/text()"))
            date = dateparser.parse(r_date)
            date = str(date).split(" ")[0]

        review['TestDateText'] = date

        # 'DBaseCategoryName'
        review['DBaseCategoryName'] = 'PRO'

        # 'source_internal_id'
        review['source_internal_id'] = response.url.split('/')[-2]
        # --------------------------------------------------------------------

        # PRODUCT ITEM -------------------------------------------------------
        product = ProductItem()
        product['source_internal_id'] = review['source_internal_id']
        product['OriginalCategoryName'] = response.meta.get('cat')
        product['ProductName'] = review['ProductName']
        manu_xpath = "(//div[@class='article_tags']/ul[@class='vert_hover']/li/a/text())[last()]"
        product['ProductManufacturer'] = self.extract(response.xpath(manu_xpath))
        pic_url_xpath = '//meta[@property="og:image"]/@content'
        pic_url = response.xpath(pic_url_xpath).get()
        product['PicURL'] = pic_url

        product['TestUrl'] = response.url
        # --------------------------------------------------------------------

        if review:
            yield review
            yield product
