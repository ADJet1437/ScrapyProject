# -*- coding: utf8 -*-
import re
import traceback
from datetime import datetime

from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.lib.selenium_browser import get_award_image_screenshot

from alascrapy.items import CategoryItem

class Mobil_seSpider(AlaSpider):
    name = 'mobil_se'
    allowed_domains = ['mobil.se']
    start_urls = ['http://www.mobil.se/tester','http://www.mobil.se/appar']
    months = ['jan', 'feb', 'mar', 'apr', 'maj', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov', 'dec']

    def __init__(self, *args, **kwargs):
        super(Mobil_seSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970,1,1)

    def parse(self, response):
        original_url = response.url
        reviews = response.xpath("//div[@class='kol1']//div[contains(@class, 'views-row-')]")
        date = ''
        for review in reviews:
            date = self.str_as_datetime(self.extract(review.xpath(".//span[@class='date']//text()")))
            title = self.extract(review.xpath(".//h2//text()"))
            url = self.extract(review.xpath(".//h2/a/@href"))
            rating = self.extract(review.xpath(".//div[contains(@class,'numeric-grade')]//text()"))
            if rating[-3:] == "/10":
                rating = float(rating[:-3])
            elif rating[-1:] == "%" and len(rating) > 1:
                rating = float(rating[:-1])/10.
            if isinstance(rating, float):
                request = Request(url, callback=self.level_2)
                request.meta["infos"] = {
                    "date" : date,
                    "title" : title,
                    "rating" : rating
                }
                award_xpath_in_review = ".//div[contains(@class,'numeric-grade')]/following-sibling::div[not(contains(@class, 'os-list'))]/@class"
                award = self.extract(review.xpath(award_xpath_in_review))
                try:
                    if award:
                        award_global_xpath = "//div[contains(@class,'" + award + "')]"
                        award_text = "Mobil_" + award
                        award_file_name = re.sub(r'\W', '', award_text)

                        request.meta["award"] = {
                            "name" : award_text,
                            "pic" : get_award_image_screenshot(self, response, award_global_xpath,
                                                               self.spider_conf['source_id'],
                                                               award_file_name)
                        }
                except Exception:
                    self.logger.error('Failed to get award image screenshot, review page: {}'.format(response.url))
                    self.logger.error(traceback.format_exc())
                yield request

        if date and date < self.stored_last_date:
            return

        url_xpath = "//ul[@class='pager']//li[@class='pager-next']/a/@href"
        single_url = self.extract(response.xpath(url_xpath))
        if single_url:
            single_url = get_full_url(original_url, single_url)
            yield Request(single_url, callback=self.parse)

    def str_as_datetime(self, str_date):
        split_date = str_date.split(" ")
        day = int(split_date[0])
        year = int(split_date[2])
        month = int(self.months.index(split_date[1]) +1)
        return datetime(year, month, day)

    def level_2(self, response):
        original_url = response.url
        product_xpaths = {
            "source_internal_id":"//div[@id='disqus_thread']/@data-nid",
            "OriginalCategoryName":"//div[contains(@class, 'produkttyp')]//a/text()",
            "PicURL":"//ul[@class='fancybox-gallery']//img/@src | //div[@class='pane-content']/h2[count(//ul[@class='fancybox-gallery']//img)=0]/following::img[1]/@src",
            "ProductManufacturer":"//div[contains(@class,'field-name-field-tillverkare')]//text()",
        }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product["ProductName"] = response.meta["infos"]["title"]
        product['TestUrl'] = original_url

        category_path = product.get('OriginalCategoryName')
        if category_path:
            category = CategoryItem()
            category['category_path'] = category_path
            yield category

            if self.should_skip_category(category):
                return

        review_xpaths = {
            "source_internal_id":"//div[@id='disqus_thread']/@data-nid",
            "TestSummary":"//div[@id='col-1']/div[contains(@class,'lead')]//div[contains(@class, 'field-item')]/text()",
            "TestVerdict":"(//div[@property='content:encoded']//p[string-length(.//text())>2][last()])[last()]//text()",
            "Author":"//span[@class='author-name']//text()",
            "TestTitle":"//div[contains(@class, 'pane-node-title')]/h2//text()",
        }
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        
        review["ProductName"] = response.meta["infos"]["title"]
        review["SourceTestRating"] = response.meta["infos"]["rating"]
        review["TestDateText"] = response.meta["infos"]["date"].isoformat().split("T")[0]
        review['TestUrl'] = original_url
        try:
            review['ProductName'] = product['ProductName']
            review['source_internal_id'] = product['source_internal_id']
        except:
            pass

        review["DBaseCategoryName"] = "PRO"
        review["SourceTestScale"] = "10"

        if "award" in response.meta.keys():
            review['award'] = response.meta["award"]["name"]
            review['AwardPic'] = response.meta["award"]["pic"]

        yield product
        yield review
