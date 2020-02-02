__author__ = 'jim'

import re
from datetime import datetime
import dateparser
from scrapy.http import Request
from alascrapy.items import ProductIdItem, ReviewItem, ProductItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format
import alascrapy.lib.dao.incremental_scraping as incremental_utils


class NotebooksbilligerDeSpider(AlaSpider):
    name = 'notebooksbilliger_de'
    allowed_domains = ['notebooksbilliger.de']
    crawlera_enabled = True

    def __init__(self, *args, **kwargs):
        super(NotebooksbilligerDeSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

    def start_requests(self):
        start_urls = {
            'botebook': 'https://www.notebooksbilliger.de/notebooks',
            'monitor': 'https://www.notebooksbilliger.de/tft+monitore',
            'drucker': 'https://www.notebooksbilliger.de/drucker',
            'smarthome': 'https://www.notebooksbilliger.de/netzwerk/smart+home+netzwerk',
            'beamer': 'https://www.notebooksbilliger.de/beamer',
            'pc': 'https://www.notebooksbilliger.de/pc+systeme',
            'smartphones': 'https://www.notebooksbilliger.de/handys+smartphones',
            'tablets': 'https://www.notebooksbilliger.de/tablets'
        }
        for key in start_urls:
            yield Request(url=start_urls[key],
                          callback=self.parse,
                          meta={'category': key})

    def parse(self, response):
        product_content = response.xpath("//div[@class='product_name']")
        category = response.meta.get('category', None)
        for content in product_content:
            review_url = self.extract(content.xpath(
                ".//a[@class='listing_product_title']/@href"))
            product_name = self.extract(content.xpath(
                ".//a[@class='listing_product_title']//text()"))
            yield response.follow(url=review_url,
                                  callback=self.parse_reviews,
                                  meta={"product_name": product_name,
                                        "category": category})
        maximum_pages = self.extract(response.xpath(
            "(//a[contains(@title,'Seite')]//text())[last() - 1]"))
        if maximum_pages:
            for i in range(2, int(maximum_pages) + 1):
                bash_url = response.url
                if 'page' in bash_url:
                    continue
                next_page_url = "{}/page/{}".format(bash_url, i)
                yield Request(url=next_page_url, callback=self.parse)

    def parse_reviews(self, response):
        category = response.meta.get("category", None)
        product_name = response.meta.get("product_name", None)
        data_link = self.extract(response.xpath(
            "//div[@class='text-center read_all_reviews']/a/@href"))
        if data_link:
            yield Request(url=data_link,
                          callback=self.parse_user_reviews,
                          meta={'product_name': product_name,
                                'category': category})

    def parse_user_reviews(self, response):
        product_name = response.meta.get("product_name", None)
        category = response.meta.get("category", None)
        if not product_name:
            product_name = self.extract(response.xpath("//h1/text()"))
        ori_url = response.url

        review = ReviewItem()
        product = ProductItem()

        title = self.extract(response.xpath("//h1/text()"))
        pic_url = self.extract(response.xpath("//img[@id='detailimage']/@src"))
        review_blocks = response.xpath("//div[@class='review_block']")
        for content in review_blocks:
            review_date_str = self.extract(content.xpath(
                ".//div[@class='date_added']//text()"))
            date_time = dateparser.parse(review_date_str, languages=['de'])
            if date_time < self.stored_last_date:
                continue
            date = datetime.strftime(date_time, "%Y-%m-%d")
            review['TestDateText'] = date
            review_id = self.extract(content.xpath("./@id"))
            review_text = self.extract_all(content.xpath(
                './/div[@class="reviews_text break-text"]//text()'))
            # if "Pro" and "Contra" in review_text:
            #     pros = re.findall(r"Pro:(.*?)Contra", review_text)
            #     pros = pros[0]
            #     review['TestPros'] = pros[0]
            #     if "Fazit" in review_text:
            #         summary = re.findall(r"Fazit:.*", review_text)
            #         review['TestSummary'] = summary[0]
            #         review['TestCons'] = review_text.replace(pros, '').replace(summary[0], '')
            #     else:
            #         review['TestCons'] = review_text.replace(pros, '')
            # else:
            review['TestSummary'] = review_text

            rating_str = self.extract(content.xpath(
                './/div[@class="stars"]/span/@title'))
            rating = re.findall(r'Bewertung: (.*?) von', rating_str)
            if rating:
                rating = rating[0]
                review['SourceTestRating'] = rating
                review['SourceTestScale'] = 5
            review['DBaseCategoryName'] = 'USER'
            review['ProductName'] = product_name
            review['source_internal_id'] = review_id
            review['TestUrl'] = ori_url
            review['TestTitle'] = title

            product['ProductName'] = product_name
            product['source_internal_id'] = review_id
            product['TestUrl'] = ori_url
            product['PicURL'] = pic_url
            product['OriginalCategoryName'] = category

            yield product
            yield review
            price = self.extract(response.xpath(
                '//div[@itemprop="price"]/@content'))
            if price:
                yield ProductIdItem.from_product(product,
                                                 kind='price',
                                                 value=price
                                                 )
