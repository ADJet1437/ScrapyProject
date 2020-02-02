# -*- coding: utf8 -*-

from scrapy.http import Request
from datetime import datetime
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem


class Diskidee_beSpider(AlaSpider):
    name = 'diskidee_be'
    allowed_domains = ['diskidee.be']

    def __init__(self, *args, **kwargs):
        super(Diskidee_beSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

        # In order to test another stored_last_date
        # self.stored_last_date = datetime(2018, 1, 3)

    def start_requests(self):
        # print "     START_REQUESTS"

        base_url = 'https://www.diskidee.be/tag'

        category_url = {
            'Laptop': '/laptops/',
            'Tablet': '/tablets/',
            'Smartphone': '/smartphones/',
            'Monitor': '/beeldschermen/',
            'Camera': '/digitale-cameras/',
            'Headset': '/headsets/',
            'Headphone': '/hoofdtelefoons/',
            'Printer': '/printers/',
            'Scanner': '/scanners/',
            'Smartwatch': '/smartwatches/'
        }

        for c in category_url:
            yield Request(url=base_url + category_url[c],
                          callback=self.parse,
                          meta={'category': c})

    def get_date(self, review_div):
        # The only place the website put the date of the post
        #  in on the URL for the post page. That's where we are
        #  going to extract the date from:
        date_xpath = './/div/h3/a/@href'
        date = review_div.xpath(date_xpath).get()
        date = date.split('https://www.diskidee.be/')[1]
        date = date.split('/')[:3]
        date = "-".join(date)
        # Date in datetime format
        date_dt = datetime.strptime(date, '%Y-%m-%d')

        return date_dt

    def parse(self, response):
        # print "     ...PARSE: " + response.url

        review_divs_xpath = '//div[@class="td-block-span6"]'
        review_divs = response.xpath(review_divs_xpath)

        for r_div in review_divs:
            # Check date
            date_dt = self.get_date(r_div)
            date = date_dt.strftime("%Y-%m-%d")

            if date_dt > self.stored_last_date:
                url = r_div.xpath('.//div/h3/a/@href').get()
                category = response.meta.get('category')
                yield Request(url=url,
                              callback=self.parse_product_review,
                              meta={'category': category,
                                    'date': date})

        # Checking whether we should scrape the next page
        date_dt = self.get_date(review_divs[-1])

        if date_dt > self.stored_last_date:
            category = response.meta.get('category')

            # Here we'll check whether there's a <a> which contains a
            # <i class="td-icon-menu-right". In that case, it means we have
            # a next page button
            is_there_next_page_xpath = '//div[@class="page-nav td-pb-'\
                                       'padding-side"]//a/i[@class="td-'\
                                       'icon-menu-right"]'
            is_there_next_page = response.xpath(is_there_next_page_xpath)

            if is_there_next_page:
                next_page_url_xpath = '//div[@class="page-nav td-pb-padding-'\
                                      'side"]//a[last()]//@href'

                next_page_url = response.xpath(next_page_url_xpath).get()

                yield Request(url=next_page_url,
                              callback=self.parse,
                              meta={'category': category})

    def parse_product_review(self, response):
        # print "     ...PARSE_PRODUCT_REVIEW: " + response.url

        # This website doesn't have a clear way of stating whether the post
        #  is a review or not. We are making this decision by checking the
        #  classes of the first content div. The reviews follow the following
        #  rule/pattern: <div id="wppr-review-45320" ... >
        main_div_id_xpath = '//div[@class="td-post-content"]/div[1]/@id'
        main_div_id = response.xpath(main_div_id_xpath).get()

        # In case the post is a review
        if main_div_id and ('review' in main_div_id.split('-')):

            # REVIEW ITEM ---------------------------------------------------
            review_xpaths = {
                'TestTitle': '//h1[@class="entry-title"]//text()',
                'TestSummary': '//meta[@property="og:description"]/@content',
                'ProductName': '//meta[@property="og:title"]//@content',
                'Author': '//div[@class="td-post-author-name"]//a//text()'
            }

            review = self.init_item_by_xpaths(response, "review",
                                              review_xpaths)

            # 'ProductName'
            words_to_remove = ['review', '|', 'DISKIDEE']
            for word in words_to_remove:
                review['ProductName'] = review['ProductName'].replace(word, '')
            review['ProductName'] = review['ProductName'].strip()

            # 'TestDateText'
            review['TestDateText'] = response.meta.get('date')

            # 'SourceTestScale' and 'SourceTestRating'
            rate_xpath = '//div[@class="review-wu-grade"]/div/div/span//text()'
            rate = response.xpath(rate_xpath).get()
            review['SourceTestRating'] = rate
            if review['SourceTestRating']:
                review['SourceTestScale'] = 10

            # 'DBaseCategoryName'
            review['DBaseCategoryName'] = 'PRO'

            # 'TestPros' and 'TestCons'
            pros_xpath = '//div[@class=" pros"]//ul//li//text()'
            pros = response.xpath(pros_xpath).getall()
            pros = ";".join(pros)
            review['TestPros'] = pros

            cons_xpath = '//div[@class=" cons"]//ul//li//text()'
            cons = response.xpath(cons_xpath).getall()
            cons = ";".join(cons)
            review['TestCons'] = cons

            # 'source_internal_id'
            sid = main_div_id.split('-')[-1]
            review['source_internal_id'] = sid
            # ---------------------------------------------------------------

            # PRODUCT ITEM --------------------------------------------------
            product = ProductItem()
            product['source_internal_id'] = review['source_internal_id']
            product['OriginalCategoryName'] = response.meta.get('category')
            product['ProductName'] = review['ProductName']
            pic_xpath = '//meta[@property="og:image"]//@content'
            pic_url = response.xpath(pic_xpath).get()
            product['PicURL'] = pic_url
            product['TestUrl'] = response.url
            # ---------------------------------------------------------------

            yield review
            yield product
