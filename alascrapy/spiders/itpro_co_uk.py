# -*- coding: utf8 -*-
from datetime import datetime
import re

from scrapy.http import Request, HtmlResponse
from scrapy.selector import Selector

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import CategoryItem, ProductItem, ReviewItem, ProductIdItem


class Itpro_co_ukSpider(AlaSpider):
    name = 'itpro_co_uk'
    allowed_domains = ['itpro.co.uk']
    start_urls = ['http://www.itpro.co.uk/reviews']

    def __init__(self, *args, **kwargs):
        super(Itpro_co_ukSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):
        original_url = response.url
        urls_xpath = "//main[contains(@id,'group-content')]//ul[@class='view-rows']//h5//a/@href"
        urls = self.extract_list(response.xpath(urls_xpath))

        for single_url in urls:
            single_url = get_full_url(original_url, single_url)
            request = Request(single_url, callback=self.level_2)
            yield request

        first_date_text = self.extract(response.xpath("(//span[@class='date-display-single'])[1]/text()"))
        if first_date_text:
            first_date = datetime.strptime(first_date_text, '%d %b, %Y')
            print first_date
            if first_date and first_date < self.stored_last_date:
                return

        next_page_url_xpath = "//ul[@class='pager']/li[starts-with(@class,'pager-next')]/a/@href"
        next_page_url = self.extract(response.xpath(next_page_url_xpath))
        if next_page_url:
            next_page_url = get_full_url(original_url, next_page_url)
            request = Request(next_page_url, callback=self.parse)
            yield request
    
    def level_2(self, response):
                                     
        original_url = response.url
        
        category_leaf_xpath = "//nav[starts-with(@class,'breadcrumb')]/ol/li[position()=last()-2]//text()"
        category_path_xpath = "//nav[starts-with(@class,'breadcrumb')]/ol/li[position()<last()]//text()"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = {
                "source_internal_id": "//link[@rel='canonical']/@href",
                "ProductName":"//h1/text()",
                "PicURL":"//meta[@property='og:image']/@content",
        }

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['TestUrl'] = original_url
        picurl = product.get("PicURL", "")
        if picurl and picurl[:2] == "//":
            product["PicURL"] = "https:" + product["PicURL"]
        if picurl and picurl[:1] == "/":
            product["PicURL"] = get_full_url(original_url, picurl)
        manuf = product.get("ProductManufacturer", "")
        if manuf == "" and ""[:2] != "//":
            product["ProductManufacturer"] = ""

        product["OriginalCategoryName"] = category['category_path']

        ocn = product.get("OriginalCategoryName", "")
        if ocn == "" and ""[:2] != "//":
            product["OriginalCategoryName"] = ""
        review_xpaths = {
                "source_internal_id": "//link[@rel='canonical']/@href",
                "ProductName":"//h1/text()",
                "SourceTestRating":"//div[@id='content']//div[@class='fivestar-default']//text()",
                "TestDateText":"substring-before(//span[contains(@datatype,'dateTime')]/@content,'T')",
                "TestPros":"//div[@class='field-label' and starts-with(normalize-space(),'Pros')]/following::div[1]/*/text()",
                "TestCons":"//div[@class='field-label' and starts-with(normalize-space(),'Cons')]/following::div[1]/*/text()",
                "TestSummary":"//meta[@property='og:description']/@content",
                "TestVerdict":"//div[@class='field-label' and starts-with(normalize-space(),'Verdict')]/following::div[1]/*/text()",
                "Author":"//div[@class='content']/descendant-or-self::span[contains(@property,'reviewer') or contains(@class,'field-author')][1]//span//text()",
                "TestTitle":"//h1/text()",
                "award":"//img[@class='award_logo']/@title",
                "AwardPic":"//img[@class='award_logo']/@src"
        }
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        review['TestUrl'] = original_url

        awpic_link = review.get("AwardPic", "")
        if awpic_link and awpic_link[:2] == "//":
            review["AwardPic"] = "https:" + review["AwardPic"]
        if awpic_link and awpic_link[:1] == "/":
            review["AwardPic"] = get_full_url(original_url, awpic_link)

        matches = None
        field_value = product.get("source_internal_id", "")
        if field_value:
            matches = re.search("((?<=\/)\d*\d(?=\/))", field_value, re.IGNORECASE)
        if matches:
            product["source_internal_id"] = matches.group(1)

        try:
            review['ProductName'] = product['ProductName']
            review['source_internal_id'] = product['source_internal_id']
        except:
            pass

        review["DBaseCategoryName"] = "PRO"
        review["SourceTestScale"] = "5"
        yield product
        yield review
