# -*- coding: utf8 -*-

from datetime import datetime

from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem


class HomecinemachoiceComSpider(AlaSpider):
    name = 'homecinemachoice_com'
    allowed_domains = ['homecinemachoice.com']
    start_urls = ['https://www.homecinemachoice.com/category/televisions']

    def __init__(self, *args, **kwargs):
        super(HomecinemachoiceComSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

        # In order to test another stored_last_date
        # self.stored_last_date = datetime(2000, 2, 8)

    def parse(self, response):
        # print "     ....PARSE: " + response.url
        review_divs_xpath = '//div[@class="view-content"]/div'
        review_divs = response.xpath(review_divs_xpath)

        date = None
        for r_div in review_divs:
            date_xpath = './/span[@class="views-field views-field-created"]'\
                         '/span//text()'
            date_str = r_div.xpath(date_xpath).get()
            date = datetime.strptime(date_str, '%b %d, %Y')
            if date > self.stored_last_date:
                review_url_xpath = './div[@class="views-field views-field-'\
                                   'title"]/span[@class="field-content"]/a/'\
                                   '@href'

                review_url = r_div.xpath(review_url_xpath).get()
                date_str = date.strftime("%Y-%m-%d")
                yield response.follow(url=review_url,
                                      callback=self.parse_product_review,
                                      meta={'date': date_str})

        # Checking whether we should scrape the next page.
        next_page_url_xpath = '//a[@title="Go to next page"]/@href'
        next_page_url = response.xpath(next_page_url_xpath).get()

        # In case we have a next page option:
        if next_page_url:
            # 'date' contains the date of the last review since it was got
            #  that was the value it was set in the last loop in the 'for' loop
            if date and (date > self.stored_last_date):
                yield response.follow(url=next_page_url,
                                      callback=self.parse)

    def parse_product_review(self, response):
        # print "     ....PARSE_PRODUCT_REVIEW: " + response.url

        # REVIEW ITEM ------------------------------------
        review_xpaths = {
            'TestTitle': '//meta[@property="og:title"]/@content',
            'Author': '//div[@class="submitted-author-story"]/a//text()',
            'TestSummary': '//meta[@name="description"]/@content',
        }

        # Create the review
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        # 'ProductName'
        words_to_remove = ['review']
        review['ProductName'] = review['TestTitle']

        for word in words_to_remove:
            review['ProductName'] = review['ProductName'].replace(word, '')

        review['ProductName'] = review['ProductName'].strip()

        # 'TestDateText'
        review['TestDateText'] = response.meta.get('date')

        # 'SourceTestScale' and 'SourceTestRating'
        rating_xpath = '//b[text()="Overall: "]/following-sibling::text()'
        rating = response.xpath(rating_xpath).get()

        if not rating:
            # Sometimes the website put "Overall:" instead of "Overall: "
            rating_xpath = '//b[text()="Overall:"]/following-sibling::text()'
            rating = response.xpath(rating_xpath).get()

        if rating:
            scale = rating.split('/')[-1]
            scale = scale.strip()
            rating = rating.split('/')[0]
            rating = rating.strip()

            review['SourceTestScale'] = scale
            review['SourceTestRating'] = rating

        # 'DBaseCategoryName'
        review['DBaseCategoryName'] = 'PRO'

        # 'source_internal_id'
        # This website doesn't have an ID for each review
        sid = response.url.split('/')[-1]
        if '-review' in sid:
            sid = sid.replace('-review', '')
        review['source_internal_id'] = sid
        # -------------------------------------------------

        # PRODUCT ITEM ------------------------------------
        product = ProductItem()
        product['source_internal_id'] = review['source_internal_id']

        category_xpath = '//div[@class="meta"]//h1/a//text()'
        category = response.xpath(category_xpath).get()
        product['OriginalCategoryName'] = category

        product['ProductName'] = review['ProductName']

        pic_url_xpath = '//meta[@property="og:image"]/@content'
        pic_url = response.xpath(pic_url_xpath).get()
        product['PicURL'] = pic_url

        product['TestUrl'] = response.url
        # -------------------------------------------------

        yield review
        yield product
