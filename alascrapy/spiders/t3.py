# -*- coding: utf8 -*-
from datetime import datetime
import dateutil.parser
import js2xml
import time
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.spiders.base_spiders import ala_spider as spiders


class T3ComSpider(spiders.AlaSpider):
    name = 't3'
    allowed_domains = ['t3.com']
    start_urls = ['https://www.t3.com/reviews']

    def __init__(self, *args, **kwargs):
        super(T3ComSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(2019, 06, 1)

    def parse(self, response):

        review_divs_xpath = "//section"
        review_divs = response.xpath(review_divs_xpath)

        for review_div in review_divs:
            date_xpath = "./a//time[@class='published-date relative-date']/@datetime"
            dates = (review_div.xpath(date_xpath)).getall()
            for date in dates:
                date_str = str(date).split("T")[0]
            	review_date = datetime.strptime(date_str, '%Y-%m-%d')
                if review_date > self.stored_last_date:
			        reviews_xpath = './a[@class="listing__link"]/@href'
			        review_links = review_div.xpath(reviews_xpath).extract()
			        for link in review_links:
			            yield response.follow(url=link, callback=self.parse_review_page)

        next_page_link = self.get_next_page_link(response)
        if next_page_link:
            last_date = self.extract(response.xpath('(//a//time[@class="published-date relative-date"]/@datetime)[last()]'))
            date = str(last_date).split("T")[0]
            date_time = datetime.strptime(date, '%Y-%m-%d')
            if date_time > self.stored_last_date:
                yield response.follow(url=next_page_link, callback=self.parse)

    def get_next_page_link(self, response):
        # fetches the result based on the date of the last review
        last_post_time_xpath = '(//*[contains(@class, "listing__item")]' \
            '//time)[last()]/@datetime'
        last_time = self.extract(response.xpath(last_post_time_xpath))

        if not last_time:
            return None

        # Gets the date transformed in seconds out of the last post
        date = dateutil.parser.parse(last_time)
        seconds = time.mktime(date.timetuple())
        seconds_string = str(int(seconds))

        url = 'https://www.t3.com/more/reviews/latest/' + seconds_string
        return url

    def parse_review_page(self, response):
        product = self.parse_product(response)
        review = self.parse_review(response)
        yield product
        yield review
      
    def parse_product(self, response):
        product_xpaths = {
            'PicURL': '//meta[@property="og:image"]/@content'
        }
        product = self.init_item_by_xpaths(response, 'product', product_xpaths)
        if not product['PicURL']:
        	product['PicURL'] = self.extract(response.xpath("//div[@class='image image--hero']/img/@src"))
        product['ProductName'] = self.get_product_name(response)
        product['source_internal_id'] = str(response.url).split('/')[4]

        return product

    def parse_review(self, response):
        review_xpaths = {
            'Author': '//a[@class="byline__authorname"]/text()',
            'TestSummary': '//meta[@property="og:description"]/@content',
            'ProductName': '//meta[@property="og:title"]/@content',
            'TestTitle': '//meta[@property="og:title"]/@content',

            'TestPros': '//h4[contains(@class,"plus")]/following-sibling::ul'
            '//li/p/text()',

            'TestCons': '//h4[contains(@class,"minus")]/following-sibling::ul'
            '//li/p/text()',

            'TestDateText': 'substring-before('
            '//meta[@name="pub_date"]/@content, "T")',
        }

        review = self.init_item_by_xpaths(response, 'review', review_xpaths)
        review['source_internal_id'] = str(response.url).split('/')[4]
        review['ProductName'] = self.get_product_name(response)
        review['DBaseCategoryName'] = 'PRO'
        self.update_review_rating(response, review)

        return review

    def get_product_name(self, response):
        xpath = '//script[contains(text(), "var dfp_config")]/text()'
        product_name_xpath = '//property[@name="product"]/string/text()'

        js_text = self.extract_xpath(response, xpath)
        parsed = js2xml.parse(js_text)
        product_name = parsed.xpath(product_name_xpath)

        if len(product_name) > 0 and product_name[0]:
            return product_name[0]

        # If couldn't fetch from JavaScript, fetches from URL, example
        # https://www.t3.com/reviews/nintendo-snes-classic-mini-review
        product_name = response.url.split('/')[-1]
        product_name = product_name.replace('review', '')
        product_name = product_name.replace('-', ' ')
        product_name = product_name.strip()

        return product_name

    def update_review_rating(self, response, review):
        # maps the class names to the raing value it represents
        rating_xpath = '//div[@class="rating"]/span/@class'
        ratings = response.xpath(rating_xpath).extract()

        if len(ratings) == 0:
            return

        rating_class_value_map = {
            'rating__star': 1,
            'rating__star rating__star--half': 0.5,
            'rating__star rating__star--empty': 0,
        }

        SourceTestRating = 0
        for rating in ratings:
            SourceTestRating += rating_class_value_map.get(rating, 0)

        if SourceTestRating == 0:
            return

        review['SourceTestRating'] = SourceTestRating
        review['SourceTestScale'] = len(ratings)
