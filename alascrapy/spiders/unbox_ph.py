# -*- coding: utf8 -*-
from datetime import datetime
import re

from scrapy.http import Request, HtmlResponse
from scrapy.selector import Selector

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import date_format
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import CategoryItem, ProductItem, ReviewItem, ProductIdItem


class Unbox_phSpider(AlaSpider):
    name = 'unbox_ph'
    allowed_domains = ['unbox.ph']
    start_urls = ['http://www.unbox.ph/category/editorials/reviews/']

    def __init__(self, *args, **kwargs):
        super(Unbox_phSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):

        for product_url in response.xpath(
                "//div[@class='td_module_10 td_module_wrap td-animation-stack']/div/h3/a/@href").extract():
            yield Request(url=product_url, callback=self.level_2)

        last_page=30
        for i in range(2, last_page+1):
            next_page_url = 'https://www.unbox.ph/category/editorials/reviews/page/'+str(i)
            if next_page_url:
                request = Request(next_page_url, callback=self.parse)
                yield request
    
    def level_2(self, response):

        r_date = self.extract(response.xpath("//time[@class='entry-date updated td-module-date']/@datetime"))
        date = str(r_date).split("T")[0]
        review_date = datetime.strptime(date, "%Y-%m-%d")
        if self.stored_last_date > review_date:
            return

        category_leaf_xpath = "//div[@id='crumbs']/descendant-or-self::a[last()]//text()"
        category_path_xpath = "//div[@id='crumbs']//a//text()"
        category = CategoryItem()
        category['category_url'] = response.url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = {
                "source_internal_id": "substring-after(//link[@rel='shortlink']/@href,'p=')",
                
                "OriginalCategoryName":"//div[@id='crumbs']//a//text()",
                
                "PicURL":"//meta[@property='og:image']/@content",
                          }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        picurl = product.get("PicURL", "")
        if picurl and picurl[:2] == "//":
            product["PicURL"] = "https:" + product["PicURL"]
        if picurl and picurl[:1] == "/":
            product["PicURL"] = get_full_url(original_url, picurl)
        manuf = product.get("ProductManufacturer", "")
        if manuf == "" and ""[:2] != "//":
            product["ProductManufacturer"] = ""
        try:
            product["OriginalCategoryName"] = category['category_path']
        except:
            pass
        ocn = product.get("OriginalCategoryName", "")
        if ocn == "" and "//div[@id='crumbs']//a//text()"[:2] != "//":
            product["OriginalCategoryName"] = "//div[@id='crumbs']//a//text()"     
        
        review_xpaths = {                               
                "TestVerdict":"//div[@class='td-ss-main-content']/div[@class='td-post-content']/ul/li/text()",
                
                "Author":"//div[@class='td-post-author-name']/a/text()",
                
                "TestTitle":"//h1[contains(@class,'title')]//text()",
                            }
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        review['source_internal_id'] = product['source_internal_id']
       
        productname = review['TestTitle'].split(':')[0].replace('Review', '').replace('Quick', '').replace('Review', '').replace('Hands-on', '').rstrip(' ')
        product['ProductName'] = productname
        review['ProductName'] = product['ProductName']

        test_summary = self.extract(response.xpath("(//div[@class='td-post-content']/p/text())[1]"))
        if not test_summary:
            test_summary = self.extract(response.xpath("(//div[@class='td-post-content']/p/span//text())[1]"))
            if not test_summary:
                test_summary = self.extract(response.xpath("(//div[@class='td-post-content']/p//text())[2]"))
                if not test_summary:
                    test_summary = self.extract(response.xpath("(//div[@class='td-post-content']/div//text())[1]"))

        review['TestSummary'] = test_summary
        if not review['TestSummary']:
            review['TestSummary'] = review['TestTitle']
        
        review["DBaseCategoryName"] = "PRO"
        review["TestDateText"] = date    

        yield review
        yield product
        
