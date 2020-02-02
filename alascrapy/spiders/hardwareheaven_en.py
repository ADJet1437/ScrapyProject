# -*- coding: utf8 -*-
from datetime import datetime
import re
from scrapy.http import Request, HtmlResponse
from scrapy.selector import Selector

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import CategoryItem, ProductItem, ReviewItem, ProductIdItem


class Hardwareheaven_enSpider(AlaSpider):
    name = 'hardwareheaven_en'
    allowed_domains = ['hardwareheaven.com']
    start_urls = ['https://www.hardwareheaven.com/cat/reviews/']

    def __init__(self, *args, **kwargs):
        super(Hardwareheaven_enSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):

        for product_url in response.xpath(
                '//h2[@class="title title20"]/a/@href').extract():
            yield Request(url=product_url, callback=self.level_2)

        next_page_xpath = '//div[@class="pagination"]//a[last()-1]/@href'
        next_page = self.extract(response.xpath(next_page_xpath))

        review_date_xpath = '//*[@id="post-big"][12]/div/div[3]/time[@datetime]'
        review_date = self.extract_list(response.xpath(review_date_xpath))
        review_date = str(review_date).split("\"")[1]
        oldest_review_date = datetime.strptime(review_date, "%Y-%m-%d")

        if next_page:
            if oldest_review_date < self.stored_last_date:
                yield response.follow(next_page, callback=self.parse)
        else:
            print('No next page found: {}'.format(response.url))

    def level_2(self, response):

        original_url = response.url

        category_leaf_xpath = "//div[@class='breadcrumbs']/a[@rel='category tag'][last()]/text()"
        category_path_xpath = "//div[@class='breadcrumbs']//text()"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(
            response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(
            response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = {"PicURL": "//meta[@property='og:image']/@content", }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['source_internal_id'] = str(response.url).split(
            '/')[3].replace("-", "").replace(" ", "")[:15]
        product['ProductName'] = str(response.xpath(
            '//span[1][@itemprop="name"]/text()').extract()).split(',')[0].split('\'')[1].replace("Review", "")
        picurl = product.get("PicURL", "")
        if picurl and picurl[:2] == "//":
            product["PicURL"] = "https:" + product["PicURL"]
        if picurl and picurl[:1] == "/":
            product["PicURL"] = get_full_url(original_url, picurl)

        try:
            product["OriginalCategoryName"] = category['category_leaf']
        except BaseException:
            pass

        review_xpaths = {
            "TestDateText": "(//div[@class='snippet-data']/time/text() | //time//span/@datetime)[1]",
            "TestSummary": "(( //p[contains(.,'Summary')]//text() | //div[@class='single-post-ad']/following-sibling::p[text()][1]//text())[1] | //div[@class='single-post-content']//p[text()][1]//text())",
            "Author": "//h5/text()",
            "TestTitle": "//h1[contains(@class,'title')]/span[@itemprop='name']/text()",
            "TestPros": "//div[@class='single-post-content']/ul[1]/*/text()",
            "TestCons": "//div[@class='single-post-content']/ul[2]/*/text()",
        }
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        try:
            review['ProductName'] = product['ProductName']
            review['source_internal_id'] = product['source_internal_id']
        except BaseException:
            pass

        review["DBaseCategoryName"] = "PRO"

        review['TestPros'] = self.extract_all(response.xpath(
            '//div[@class="single-post-content"]/ul[1]/*/text()'))
        review['TestCons'] = self.extract_all(response.xpath(
            '//div[@class="single-post-content"]/ul[2]/*/text()'))

        test_verdict_xpath = '//*[contains(.,"Conclusion")]/following-sibling::p[text()][1]//text()'

        review["TestVerdict"] = self.extract(
            response.xpath(test_verdict_xpath))

        yield review

        yield product
