# -*- coding: utf8 -*-
from datetime import datetime
import js2xml

from alascrapy.lib.dao import incremental_scraping as incremental_utils
from alascrapy.spiders.base_spiders import ala_spider as spiders


class LeMondeNumeriqueComSpider(spiders.AlaSpider):
    name = 'lemondenumerique_com'
    allowed_domains = ['lemondenumerique.com']
    start_urls = ['https://www.lemondenumerique.com/tests/']

    def __init__(self, *args, **kwargs):
        super(LeMondeNumeriqueComSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf['source_id'])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def get_rating(self, response, sii):
        rating_script_xpath = '//div[@class="article-content"]/' \
            'script[contains(text(), "\'.{sii}\'")]/text()'.format(sii=sii)
        rating_script_text = self.extract_xpath(response, rating_script_xpath)
        # When the score is empty the website sends invalid javascript
        # to fix that, I'm replacing 'score:}' with 'score:null}'
        rating_script_text = rating_script_text.replace(
            'score:}', 'score:null}')
        parsed = js2xml.parse(rating_script_text)

        rating_value_xpath = '//body/functioncall[' \
            './/functioncall/arguments/string[text()=".{sii}"]' \
            ']//property[@name="score"]/number/@value'.format(sii=sii)
        rating = parsed.xpath(rating_value_xpath)
        if len(rating) == 0:
            return None

        return rating[0]

    def parse(self, response):
        next_page_xpath = '//a[@rel="next"]/@href'
        next_page_link = response.xpath(next_page_xpath).extract()
        if len(next_page_link) > 0:
            yield response.follow(url=next_page_link[0], callback=self.parse)

        reviews_xpath = '//div[@class="search-product"]//@href'
        review_links = response.xpath(reviews_xpath).extract()
        for link in review_links:
            yield response.follow(url=link, callback=self.parse_review_page)

    def parse_review_page(self, response):
        product = self.parse_product(response)
        review = self.parse_review(response)
        yield product
        yield review

    def parse_product(self, response):
        product_xpaths = {
            'OriginalCategoryName': '//div[@class="article-info"]/p/a/text()',
            'PicURL': '//meta[@property="og:image"]/@content',
            'ProductName': '//div[@class="js-kelkoo-widget"]/@data-kw-keyword',

            'source_internal_id': 'substring-after('
            '//link[@rel="shortlink"]/@href, "=")',
        }
        product = self.init_item_by_xpaths(response, 'product', product_xpaths)

        product['TestUrl'] = response.url
        product['source_id'] = self.spider_conf['source_id']

        return product

    def parse_review(self, response):
        review_xpaths = {
            'Author': '(//span[@class="author vcard"])[1]/*/text()',
            'ProductName': '//div[@class="js-kelkoo-widget"]/@data-kw-keyword',
            'TestCons': '//div[@class="inconvenients"]//li/text()',
            'TestDateText': 'substring-before(//time[1]/@datetime, "T")',
            'TestPros': '//div[@class="avantages"]//li/text()',
            'TestSummary': '//meta[@property="og:description"]/@content',
            'TestTitle': '//meta[@property="og:title"]/@content',
            'TestVerdict': '//div[@class="avis_test"]/text()',

            'source_internal_id': 'substring-after('
            '//link[@rel="shortlink"]/@href, "=")',
        }

        review = self.init_item_by_xpaths(response, 'review', review_xpaths)

        review['TestUrl'] = response.url
        review['source_id'] = self.spider_conf['source_id']
        review['DBaseCategoryName'] = 'PRO'  # 'USER'
        rating = self.get_rating(response, review['source_internal_id'])
        if rating is not None:
            review['SourceTestRating'] = rating
            review['SourceTestScale'] = 5  # ratings on this website scale 5

        return review
