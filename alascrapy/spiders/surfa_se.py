# -*- coding: utf8 -*-
from datetime import datetime
import re

from scrapy.http import Request, HtmlResponse
from scrapy.selector import Selector

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import CategoryItem, ProductItem, ReviewItem, ProductIdItem


class Surfa_seSpider(AlaSpider):
    name = 'surfa_se'
    allowed_domains = ['surfa.se']
    start_urls = ['http://surfa.se/kategori/test/']

    def __init__(self, *args, **kwargs):
        super(Surfa_seSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):

        review_urls = response.xpath("//div[@class='td-module-thumb']/a/@href").extract()
        product_url = list(dict.fromkeys(review_urls))
        for r_url in product_url:
            yield response.follow(r_url, callback=self.level_2)

        next_page_xpath = "(//div[@class='page-nav td-pb-padding-side']/a/@href)[last()]"
        next_page = self.extract(response.xpath(next_page_xpath))

        review_date_xpath = "//div[@class='td_module_2 td_module_wrap td-animation-stack']//span/time/@datetime"
        review_date = self.extract(response.xpath(review_date_xpath))
        review_date = str(review_date).split("T")[0]
        oldest_review_date = datetime.strptime(review_date, "%Y-%m-%d")

        if next_page:
            if oldest_review_date < self.stored_last_date:
                yield response.follow(next_page, callback=self.parse)
        else:
            print('No next page found: {}'.format(response.url))
    
    def level_2(self, response):

        date = self.extract(response.xpath("substring-before(//meta[contains(@property,'published_time')]/@content,'T')"))
        review_date = datetime.strptime(date, "%Y-%m-%d")
        if self.stored_last_date > review_date:
            return

        product_xpaths = { 
                "source_internal_id": "substring-after(//link[@rel='shortlink']/@href,'p=')",
                "ProductName":"(//body/descendant-or-self::span[@property='itemReviewed' and normalize-space()][1]//text() | //h1//text())[last()]",
                "OriginalCategoryName":"//ul[contains(@class,'td-category')]/li//text()",                
                "PicURL":"//title/following::meta[@property='og:image'][1]/@content",
                            }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        
        review_xpaths = {               
                "source_internal_id": "substring-after(//link[@rel='shortlink']/@href,'p=')",            
                "ProductName":"(//body/descendant-or-self::span[@property='itemReviewed' and normalize-space()][1]//text() | //h1//text())[last()]",
                "SourceTestRating":"//body/descendant-or-self::div[contains(@class,'score')][1]/span[contains(@class,'overlall') and contains(@class,'value')]//text()",
                "TestPros":"//body/descendant-or-self::div[@class='rwp-pros'][1]//text()",
                "TestCons":"//body/descendant-or-self::div[@class='rwp-cons'][1]//text()",
                "TestSummary":"//div[@class='td-post-content']/p[string-length(normalize-space())>1][1]//text()",
                "Author":"//div[contains(@class,'author')]/a//text()",
                "TestTitle":"//h1//text()",
                            }
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        review['TestPros'] = review['TestPros'].replace('+ ', '')
        review['TestCons'] = review['TestCons'].replace('- ', '')
        review['TestDateText'] = date 

        if review['SourceTestRating']:
            review["SourceTestScale"] = "10"

        review['Author'] = review['Author'].replace('[email protected]', '')
        review["DBaseCategoryName"] = "PRO"
        
        id_value = self.extract(response.xpath("//div[@id='pspy_info_0']/span[@class='pspy_widget_price']/a/text()"))
        if id_value:
            product_id = self.product_id(product)
            product_id['ID_kind'] = "Price"
            product_id['ID_value'] = id_value
            yield product_id

        yield product
        yield review
        