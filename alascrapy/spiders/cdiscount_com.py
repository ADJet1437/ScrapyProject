__author__ = 'jim'
import dateparser
import re
from scrapy.http import Request

from alascrapy.items import ProductItem, CategoryItem, ReviewItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, set_query_parameter
from alascrapy.lib.dao.incremental_scraping import get_latest_user_review_date_by_sii


class CdiscountComSpider(AlaSpider):
    name = 'cdiscount_com'
    allowed_domains = ['cdiscount.com']
    start_urls = ['http://www.cdiscount.com/plan-du-site.asp']

    def parse(self, response):
        category_url_xpath = "//ul[@id='navV']/li/a/@href"
        category_urls = self.extract_list(response.xpath(category_url_xpath))

        for category_url in category_urls:
            category_url = get_full_url(response, category_url)
            yield Request(url=category_url, callback=self.parse_category)

    def parse_category(self, response):
        category_url_xpath = '//div[@class="mvNavSub"]/ul/li/a/@href'
        category_urls = self.extract_list(response.xpath(category_url_xpath))

        for category_url in category_urls:
            category_url = get_full_url(response, category_url)
            yield Request(url=category_url, callback=self.parse_category)

        if category_urls:
            return

        category = None
        if "category" in response.meta:
            category = response.meta['category']

        if not category:
            category = CategoryItem()
            category['category_path'] = self.extract_all(response.xpath('//div[@id="bc"]/nav//text()'), ' > ')
            category['category_leaf'] = self.extract(response.xpath('//div[@id="bc"]/nav/ul/li[last()]/text()'))
            category['category_url'] = response.url
            yield category

        if not self.should_skip_category(category):
            product_urls = self.extract_list(response.xpath(
                '//div[@class="prdtBStar"][div]/ancestor::li[@data-sku]/div/a/@href'))
            for product_url in product_urls:
                product_url = get_full_url(response, product_url)
                request = Request(url=product_url, callback=self.parse_product)
                request.meta['category'] = category
                yield request

            next_page_url = self.extract(response.xpath('//a[contains(@class,"pgNext")]/@href'))
            if next_page_url:
                next_page_url = get_full_url(response, next_page_url)
                request = Request(url=next_page_url, callback=self.parse_category)
                request.meta['category'] = category
                yield request

    def parse_product(self, response):
        sii_re = '-([^\-]+).html'
        product = ProductItem()

        product['TestUrl'] = response.url.split('#')[0]
        product['OriginalCategoryName'] = response.meta['category']['category_path']
        product['ProductName'] = self.extract(response.xpath('//h1/text()'))
        product['PicURL'] = self.extract(response.xpath('//a[@itemprop="image"]/@href'))
        product['ProductManufacturer'] = self.extract(response.xpath('//span[@itemprop="brand"]/a/span/text()'))

        match = re.search(sii_re, response.url)
        if not match:
            return
        source_internal_id = match.group(1)
        product['source_internal_id'] = source_internal_id
        yield product

        review_xpath = "//ul[@class='pagNum']/@data-action"
        total_page_xpath = "//ul[@class='pagNum']/li[@class='next']/preceding-sibling::li[1]/text()"

        review_url = self.extract_xpath(response, review_xpath)
        total_pages = self.extract_xpath(response, total_page_xpath)
        if not total_pages:
            total_pages=1
        latest_db_date = get_latest_user_review_date_by_sii(self.mysql_manager,
                                                            self.spider_conf[
                                                                "source_id"],
                                                           source_internal_id)
        if review_url:
            set_query_parameter(review_url, 'ReviewOrdering', '2')
            review_url = get_full_url(response, review_url)
            request = Request(url=review_url, callback=self.parse_reviews)
            request.meta['product'] = product
            request.meta['current_page'] = 1
            if total_pages:
                request.meta['total_pages'] = total_pages
            request.meta['latest_db_date'] = latest_db_date
            yield request

    def parse_reviews(self, response):
        reviews = response.xpath('//div[contains(@class,"detRating")]')
        product = response.meta['product']
        date_xpath = './/div[@class="date"]/@content'
        rating_xpath = './/div[@class="rat"]/span[1]/text()'
        title_xpath = './/div[@class="title"]//text()'
        summary_xpath = './/div[@class="comm"]//text()'
        date=None
        for review in reviews:
            date = self.extract_xpath(review, date_xpath)
            rating = self.extract_xpath(review, rating_xpath)
            title = self.extract_xpath(review, title_xpath)
            summary = self.extract_all_xpath(review, summary_xpath)
            user_review = ReviewItem.from_product(product=product, tp='USER', date=date,
                                                  rating=rating, title=title, summary=summary)
            yield user_review

        current_page = response.meta['current_page']
        total_pages = response.meta['total_pages']
        latest_db_date = response.meta['latest_db_date']

        if not date:
            return
        latest_date_page = dateparser.parse(date, ["%Y-%m-%d"])

        if not total_pages:
            return

        if current_page==total_pages:
            return

        if latest_db_date:
            if latest_db_date > latest_date_page:
                return

        next_page = current_page+1
        next_page_url = set_query_parameter(response.url, 'CurrentPage',
                                            next_page)
        print next_page_url

        request = Request(url=next_page_url, callback=self.parse_reviews)
        request.meta['product'] = product
        request.meta['current_page'] = next_page
        request.meta['total_pages'] = total_pages
        request.meta['latest_db_date'] = latest_db_date
        yield request

