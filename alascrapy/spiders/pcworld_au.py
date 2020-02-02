import scrapy

from urllib import unquote
import re
from datetime import datetime

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.items import ProductItem, CategoryItem, ReviewItem
from alascrapy.items import ProductIdItem
from alascrapy.lib.generic import date_format
import alascrapy.lib.dao.incremental_scraping as incremental_utils


class PcworldAuSpider(AlaSpider):
    name = 'pcworld_au'
    allowed_domains = ['pcworld.idg.com.au']
    start_urls = ['http://pcworld.idg.com.au/']

    next_page = None

    def __init__(self, *args, **kwargs):
        super(PcworldAuSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):
        cat_urls = self.extract_list(
            response.xpath
            ("//nav[@class='navbar primary-menu']//ul//li//a//@href"))
        for cat_url in cat_urls:
            yield response.follow(url=cat_url,
                                  callback=self.parse_cat_and_go_to_review)

    def parse_cat_and_go_to_review(self, response):
        category = CategoryItem()
        category_url = response.url
        category['category_url'] = category_url
        category['category_path'] = self.extract(response.xpath(
            "//div[@id='main_content']//h1/text()"))

        if not self.should_skip_category(category):
            yield category
            latest_review_url = self.extract(
                response.xpath
                ("// a[contains(text(), 'Reviews')] / @href")) + '?sort=latest'
            yield response.follow(url=latest_review_url,
                                  callback=self.parse_review_urls)

    def parse_review_urls(self, response):
        review_urls = self.extract_list(
            response.xpath("// h3[@class='review-list-name']/a /@href"))
        if review_urls:
            for review_url in review_urls:
                yield response.follow(url=review_url,
                                      callback=self.parse_review)
            next_link_url = self.extract(response.xpath(
                "(//li[@class='next']/a/@href)[1]"))
            if next_link_url:
                self.next_page = next_link_url
                last_review_url = review_urls[-1]
                yield response.follow(url=last_review_url,
                                      callback=self.parse_next_page)

    def _get_datetime_str(self, response):
        script = self.extract_all(response.xpath(
            "//script[contains(text(),'first_page_context_data')]/text()"))
        date_match = re.findall(r"publication_datetime':\"([^,]*)\"", script)
        date = ''
        if date_match:
            date = date_match[0]
            date = date.replace('+00:00', '')
            date = date_format(date, "%Y-%m-%dT%H:%M:%S")
        return date

    def _should_continue_crawl(self, date_str):
        date_time_to_compare = datetime.strptime(date_str, '%Y-%m-%d')
        return date_time_to_compare > self.stored_last_date

    def parse_next_page(self, response):
        date_str = self._get_datetime_str(response)
        if not date_str:
            return
        if self._should_continue_crawl(date_str):
            next_page_full_url = 'https://www.pcworld.idg.com' + self.next_page
            yield scrapy.Request(url=next_page_full_url,
                                 callback=self.parse_review_urls)

    def parse_review(self, response):
        product_xpaths = {
            "PicURL": "//meta[@property='og:image']/@content",
            "OriginalCategoryName":
            "// ol[@itemprop= 'breadcrumb']/ li[3]/a/span/text()"
        }

        review_xpaths = {
            "TestPros": "//div[@class='snapshot-pros']/ul//li/text()",
            "TestCons": "//div[@class='snapshot-cons']/ul//li/text()",
            "TestSummary":
            "//div[@class='review-journobox-finalword']/p/text()",
            "TestTitle": "//meta[@property='og:title']/@content",
            "SourceTestRating":
            "// span[@class= 'pcw-box-textrating']/span[1]/text()"
        }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        date_str = self._get_datetime_str(response)
        if not date_str:
            return

        if not self._should_continue_crawl(date_str):
            return
        review['TestDateText'] = date_str

        REVIEW_STRING_LENGTH = 2
        if len(review.get('TestPros')) > REVIEW_STRING_LENGTH:
            # filter out:
            #  https://www.pcworld.idg.com.au/review/panasonic/lumix_dmc-tz30_camera_preview/415904/
            TestUrl = response.url
            source_internal_id = unquote(TestUrl).split('/')[-2]
            review['source_internal_id'] = source_internal_id
            TestTitle = self.extract(response.xpath(
                "//meta[@property='og:title']/@content"))
            ProductName = TestTitle.split(':')[0]
            pattern = 'review' or 'Review'
            if pattern in ProductName:
                ProductName = ProductName.replace(pattern, '')
            review['ProductName'] = ProductName
            review['DBaseCategoryName'] = 'PRO'
            if review.get('SourceTestRating', ''):
                TESTSCALE = '5'
                review['SourceTestScale'] = TESTSCALE
            yield review

            product['ProductName'] = ProductName
            product['source_internal_id'] = source_internal_id
            yield product

            product_id = ProductIdItem()
            product_id['source_internal_id'] = source_internal_id
            product_id['ProductName'] = ProductName
            product_id['ID_kind'] = 'pcworld_id'
            product_id['ID_value'] = source_internal_id
            yield product_id
