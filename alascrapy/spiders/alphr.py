# -*- coding: utf8 -*-
from datetime import datetime

from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import CategoryItem, ReviewItem, ProductItem

class AlphrSpider(AlaSpider):
    name = 'alphr'
    allowed_domains = ['alphr.com']
    start_urls = ['http://www.alphr.com/reviews']

    def __init__(self, *args, **kwargs):
        super(AlphrSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):

        review_divs_xpath = "//div[@id='content']/div[@id='block-system-main']"
        review_divs = response.xpath(review_divs_xpath)

        for review_div in review_divs:
            date_xpath = ".//span[@class='date-display-single']/text()"
            dates = (review_div.xpath(date_xpath)).getall()
            for date in dates:
                review_date = datetime.strptime(date, '%d %b %Y')
                if review_date > self.stored_last_date:
                    review_urls_xpath = ".//p//a/@href"
                    review_urls = (review_div.xpath(review_urls_xpath)).getall()
                    for review_url in review_urls:
                        review_url = get_full_url(response, review_url)
                        yield Request(url=review_url, callback=self.parse_items)

        next_page_xpath = "//a[@title='Go to next page']/@href"
        next_page = self.extract(response.xpath(next_page_xpath))
        next_page_url = get_full_url(response, next_page)

        review_date_xpath = "(//div[@id='block-system-main']//span[@class='date-display-single']/text())[last()]"
        review_date = self.extract(response.xpath(review_date_xpath))
        oldest_review_date = datetime.strptime(review_date, "%d %b %Y")

        if next_page:
            if oldest_review_date > self.stored_last_date:
                yield response.follow(next_page_url, callback=self.parse)

    def parse_items(self, response):

        category = CategoryItem()
        category_xpath = "//div[contains(@class,'category-primary')]//a/text()"
        category_url = "//div[contains(@class,'category-primary')]//a/@href"
        category["category_leaf"] = self.extract(response.xpath(category_xpath))
        category["category_path"] = category["category_leaf"]
        category["category_url"] = get_full_url(response, self.extract(response.xpath(category_url)))

        if self.should_skip_category(category):
            return
        yield category
        
        review = ReviewItem()
        source_internal_id = str(self.extract(response.xpath("//meta[@property='og:url']/@content"))).split("/")[4]
        review['source_internal_id'] = source_internal_id
        review["TestTitle"] = self.extract(response.xpath( "//div[@id='page_title_content']/h1[@id='page-title']/text()"))
        if not review["TestTitle"]:
            review["TestTitle"] = self.extract(response.xpath("//main[@id='group-content']/h2[@class='title']"))
            
        if "review" in review["TestTitle"]:
            product_name = review["TestTitle"].split("review")[0]
        elif ":" in review["TestTitle"]:
            product_name = review["TestTitle"].split(":")[0]
        else:
            product_name = (response.url).split("/")[4].replace("review", "").replace("-", " ")
            
        review['ProductName'] = product_name
        review["TestSummary"] = self.extract(response.xpath("//meta[@property='og:description']/@content"))
        review["DBaseCategoryName"] = "PRO"

        date = str(self.extract(response.xpath("//div[@class='field-name-field-published-date']/span[@class='date-display-single']/text()"))).split(",")[0]
        review['TestDateText'] = date_format(date, '%d %b %Y')

        source_test_rating = self.extract(response.xpath("//div[@class='fivestar-basic']"))
        if source_test_rating:
            review['SourceTestRating'] = source_test_rating.count('"on"')
            review['SourceTestScale'] = '5'
        
        review["TestUrl"] = response.url
        review['Author'] = self.extract(response.xpath("//div[@class='field-item even']/a[@class='author-link']/text()")).encode('utf-8')
        if not review['Author']:
            review['Author'] = self.extract(response.xpath("//span[@class='field field-name-field-author field-type-node-reference field-label-hidden']/span[@class='field-item even']/text()")).encode('utf-8')

        test_verdict_xpath_1 = "string( (//h2|//h3)[contains(text(), 'Verdict') or contains(text(), 'verdict')]/following-sibling::p[.//text()][1] )"
        test_verdict_xpath_2 = "string( //span[contains(text(), 'Verdict')]/ancestor::*[1]/following-sibling::p[.//text()][1] )"
        review["TestVerdict"] = self.extract(response.xpath(test_verdict_xpath_1))
        if not review["TestVerdict"]:
            review["TestVerdict"] = self.extract(response.xpath(test_verdict_xpath_2))

        product = ProductItem()
        product['source_internal_id'] = source_internal_id
        product['ProductName'] = product_name
        product['TestUrl'] = response.url
        product['PicURL'] =  self.extract(response.xpath("//*[@property='og:image']/@content"))
        product['ProductManufacturer'] =  self.extract(response.xpath("//li[@typeof='v:Breadcrumb'][2]/a/text()"))
        product["OriginalCategoryName"] = category['category_leaf']

        yield review
        yield product
