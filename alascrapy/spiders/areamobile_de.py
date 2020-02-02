# -*- coding: utf8 -*-
import re

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format
from alascrapy.items import CategoryItem, ProductItem, ReviewItem, ProductIdItem


class Areamobile_deSpider(AlaSpider):
    name = 'areamobile_de'
    allowed_domains = ['areamobile.de']
    start_urls = ['http://www.areamobile.de/testberichte',
                  'http://www.areamobile.de/tablets/tablet-testberichte']

    def parse(self, response):

        original_url = response.url

        urls_xpath = "//ul[contains(@class,'handyList')]/li/div[@class='data']/span[contains(@class,'ml')]/a/@href"
        urls = self.extract_list(response.xpath(urls_xpath))

        for single_url in urls:
            single_url = get_full_url(original_url, single_url)
            yield response.follow(url=single_url, callback=self.parse_product)

        url_xpath = "(//div[contains(@class,'pagination') and contains(@class,'txtR')])[last()]/span[@class='p-next']/a[@class='arrowr']/@href"
        single_url = self.extract(response.xpath(url_xpath))
        if single_url:
            single_url = get_full_url(original_url, single_url)
            yield response.follow(url=single_url, callback=self.parse)

    def parse_product(self, response):

        original_url = response.url

        category_leaf_xpath = "//div[@id='breadcrumb']/span[not(.//text()='Testbericht')][last()]//text()"
        category_path_xpath = "//div[@id='breadcrumb']/span//text()[not(.='Testbericht')]"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = {
                "ProductName":"//*[@class='h1']//text() \
                                | //meta[name='keywords']/@content",
                "OriginalCategoryName":"//div[@id='breadcrumb']/span//text()[not(.='Testbericht')]",
                "PicURL":"(//div[@id='informerLogo']//img)[1]/@src",
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

        try:
            product["OriginalCategoryName"] = category['category_path']
        except:
            pass
        ocn = product.get("OriginalCategoryName", "")
        if ocn == "" and "//div[@id='breadcrumb']/span//text()[not(.='Testbericht')]"[:2] != "//":
            product["OriginalCategoryName"] = "//div[@id='breadcrumb']/span//text()[not(.='Testbericht')]"

        # get rid of Testbericht
        if not product.get('ProductName', ''):
            product_name = self.extract(response.xpath('(//h1)[1]/text()')).replace('Testbericht', '').strip()
            product['ProductName'] = product_name
        yield product

        review_xpaths = {
                "SourceTestRating":"(//span[@itemprop='rating'])[1]/meta[@itemprop='average']/@content",
                "TestDateText": "(//a[@rel='author']/following::text()[string-length(.)>2][1] \
                                | //time[@datetime]//text())[1] \
                                | //text()[contains(.,'Autor')][count((//a[@rel='author']/following::text()[string-length(.)>2][1] \
                                | //time[@datetime]//text())[1])=0]/following-sibling::text()[1]",
                "TestPros": "//ul[@class='topflop'][.//li[contains(.//text(),'Tops')]]/li[position()>1]//text()",
                "TestCons": "//ul[@class='topflop'][.//li[contains(.//text(),'Flops')]]/li[position()>1]//text()",
                "TestSummary": "//p[@itemprop='description']/text()",
                "TestVerdict": "//h2[contains(.//text(),'Fazit')]/following::p[string-length(.//text())>2][1]//text() \
                                | //meta[@name='description']/@content",
                "Author": "//text()[contains(.,'Autor')]/following::a[1]//text()  \
                                | //span[@itemprop='reviewer'][count(//text()[contains(.,'Autor')]/following::a[1])=0]//text()",
                "TestTitle": "//meta[@property='og:title']/@content",
                            }
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        review['TestUrl'] = original_url

        # some title are in the format of: 'title | areamobile.de'
        if review['TestTitle']:
            review['TestTitle'] = review['TestTitle'].split('|')[0].strip()
        
        try:
            print('>>>>>>>>>> getting review title')
            print(product['ProductName'])
            print(response.url)
            print('>>>>>>>>>> got review title')
            review['ProductName'] = product.get('ProductName', review.get('TestTitle', ''))
            review['source_internal_id'] = product['source_internal_id']
        except:
            pass

        awpic_link = review.get("AwardPic", "")
        if awpic_link and awpic_link[:2] == "//":
            review["AwardPic"] = "https:" + review["AwardPic"]
        if awpic_link and awpic_link[:1] == "/":
            review["AwardPic"] = get_full_url(original_url, awpic_link)

        review["SourceTestScale"] = "100"

        matches = None
        field_value = review.get("SourceTestRating", "")
        if field_value:
            matches = re.search("(\d*)", field_value, re.IGNORECASE)
        if matches:
            review["SourceTestRating"] = matches.group(1)

        matches = None
        field_value = review.get("TestDateText", "")
        if field_value:
            matches = re.search("(\d{2}\.\d{2}\.\d{4})", field_value, re.IGNORECASE)
        if matches:
            review["TestDateText"] = matches.group(1)

        if review["TestDateText"]:
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(review["TestDateText"], "%d.%b.%Y", ["en"])

        review["DBaseCategoryName"] = "PRO"
        yield review

