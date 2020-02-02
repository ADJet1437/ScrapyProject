# -*- coding: utf8 -*-

from datetime import datetime
from scrapy.http import Request
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem, ProductIdItem


class WareableSpider(AlaSpider):
    name = 'wareable'
    allowed_domains = ['wareable.com']

    start_urls = ['https://www.wareable.com/archive/reviews']

    def __init__(self, *args, **kwargs):
        super(WareableSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

        # In order to test another stored_last_date
        # self.stored_last_date = datetime(2018, 2, 8)

    def parse(self, response):
        # print " 	...PARSE: " + response.url
        # print " --self.stored_last_date: " + str(self.stored_last_date)

        date_section_xpath = '//div[@class="col-md-6 col-lg-12"]'
        date_section = response.xpath(date_section_xpath)
        for s in date_section:
            year = int(s.xpath('.//h2//text()').get())
            if year >= self.stored_last_date.year:
                periods_url_xpath = './/ul//li/a/@href'
                periods_url = s.xpath(periods_url_xpath).getall()
                for p_url in periods_url:
                    p_url = p_url.strip()
                    yield Request(url=p_url,
                                  callback=self.parse_2,
                                  meta={'year': year})

    def parse_2(self, response):
        # print "     ...PARSE_2: " + response.url

        dates_xpath = '//h2[@class="up-widget__title--sm font-body '\
                      'font-weight-bold font-2 pb-2"]'
        dates = response.xpath(dates_xpath)
        for d in dates:
            date = d.xpath('.//text()').get()
            date = str(response.meta.get('year')) + " " + date
            # date looks like: 2018 December 12
            date = datetime.strptime(date, '%Y %B %d')
            if date > self.stored_last_date:
                review_url_xpath = './following-sibling::ul/li/a/@href'
                review_url = d.xpath(review_url_xpath).get()
                yield Request(url=review_url,
                              callback=self.parse_product_review,
                              meta={'date': date.strftime("%Y-%m-%d")})

    def get_product_name_based_on_title(self, title):
        ''' This function will 'clean' the title of the review
            in order to get the product name '''
        p_name = title

        # Removing certain words
        words_to_remove = ['review']
        for w in words_to_remove:
            if w in title:
                p_name = p_name.replace(w, '')

        # Removing unnecessary spaces:
        p_name = p_name.replace('  ', ' ')
        p_name = p_name.strip()

        return p_name

    def parse_product_review(self, response):
        # print "     ...PARSE_PRODUCT_REVIEW: " + response.url

        tags_xpath = '//div[@class="tagged"]/a//text()'
        tags = response.xpath(tags_xpath).getall()

        cat = None

        tags_to_exclude = ['VR', 'Fitness trackers', 'AR']
        for w in tags_to_exclude:
            if w in tags:
                return

        smartwatches_keywords = ['Hybrid smartwatches ', 'Smartwatches']
        for w in smartwatches_keywords:
            if w in tags:
                cat = 'Smartwatch'
                break

        if not cat:
            if 'Hearables' in tags:
                cat = 'Headphone'
            elif 'Cameras' in tags:
                cat = 'Camera'

        # REVIEW ITEM -----------------------------------------------
        review_xpaths = {
            'TestTitle': '//meta[@property="og:title"]/@content',
            'Author': '(//a[@rel="author"])[1]/span//text()',
            'TestSummary': '//meta[@property="og:description"]/@content',
        }

        # Create the review
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        # 'TestSummary'
        if not review['TestSummary']:
            summary_xpath = '//meta[@name="description"]/@content'
            summary = response.xpath(summary_xpath).get()
            review['TestSummary'] = summary

        # 'ProductName'
        title = review['TestTitle']
        review['ProductName'] = self.get_product_name_based_on_title(title)

        # 'TestDateText'
        review['TestDateText'] = response.meta.get('date')

        # 'SourceTestScale' and 'SourceTestRating'
        full_star_xpath = '//div[@class="float-right rating"]'\
                          '/i[@class="icon-star icon-star--full"]'
        half_star_xpath = '//div[@class="float-right rating"]'\
                          '/i[@class="icon-star icon-star--half"]'

        n_full_star = len(response.xpath(full_star_xpath))
        n_half_star = len(response.xpath(half_star_xpath))
        rating = n_full_star + 0.5*n_half_star
        review['SourceTestScale'] = 5
        review['SourceTestRating'] = rating

        # 'DBaseCategoryName'
        review['DBaseCategoryName'] = 'PRO'

        # 'TestPros' and 'TestCons'
        pros_xpath = '//div[@class="float-left hit"]/ul/li//text()'
        # pros = self.extract_all(response.xpath(pros_xpath))
        pros = response.xpath(pros_xpath).getall()
        pros = ';'.join(x.strip() for x in pros)

        cons_xpath = '//div[@class="float-right miss"]/ul/li//text()'
        # cons = self.extract_all(response.xpath(cons_xpath))
        cons = response.xpath(cons_xpath).getall()
        cons = ';'.join(x.strip() for x in cons)

        review['TestPros'] = pros
        review['TestCons'] = cons

        # 'source_internal_id'
        sid_xpath = '//meta[@property="article:published_time"]/@content'
        sid = response.xpath(sid_xpath).get()
        # sid looks like: 2019-03-22 18:51:55
        sid = sid.replace('-', '')
        sid = sid.replace(' ', '')
        sid = sid.replace(':', '')
        review['source_internal_id'] = sid
        # -----------------------------------------------------------

        # PRODUCT ITEM ----------------------------------------------
        product = ProductItem()
        product['source_internal_id'] = review['source_internal_id']

        if not cat:
            product['OriginalCategoryName'] = 'unkown'
        else:
            product['OriginalCategoryName'] = cat

        product['ProductName'] = review['ProductName']

        pic_url_xpath = '//meta[@property="og:image"]/@content'
        pic_url = response.xpath(pic_url_xpath).get()
        product['PicURL'] = pic_url

        product['TestUrl'] = response.url
        # -----------------------------------------------------------

        # PRICE - PRODUCT ID ITEM -----------------------------------
        price_xpath = '//span[@class="pricebox-price '\
                      'fonts-pricebox-price"]//text()'
        price = response.xpath(price_xpath).get()
        if price:
            yield ProductIdItem.from_product(product,
                                             kind='price',
                                             value=price
                                             )
        # -----------------------------------------------------------

        yield review
        yield product
