# -*- coding: utf8 -*-
import re
from scrapy.http import Request
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url
from alascrapy.items import CategoryItem, ReviewItem

class Head_fi_orgSpider(AlaSpider):
    name = 'head_fi_org'
    allowed_domains = ['head-fi.org']
    start_urls = ['http://www.head-fi.org/products/']

    def parse(self, response):
        original_url = response.url
        url_xpath = "//ul[@class='subcategories']/li/a/@href"
        urls = self.extract_list(response.xpath(url_xpath))
        for single_url in urls:
            single_url = get_full_url(original_url, single_url)
            request = Request(single_url, callback=self.level_2)
            yield request
    
    def level_2(self, response):
        original_url = response.url

        category = response.meta.get('category', None)
        if not category:
            category_path_xpath = "//div[@id='content-wrapper']/div[1]/div[@id='bc']//*[@class!='bc-bullet' and position()>1]/text()"
            category = CategoryItem()
            category['category_url'] = original_url
            category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
            yield category

        if self.should_skip_category(category):
            return

        url_xpath = "//*[@class='actionbar']/following-sibling::div[1]//a[starts-with(.,'Next')]/@href"
        single_url = self.extract(response.xpath(url_xpath))
        if single_url:
            single_url = get_full_url(original_url, single_url)
            request = Request(single_url, callback=self.level_2)
            request.meta['category'] = category
            yield request

        urls_xpath = "//h4/a/@href"
        urls = self.extract_list(response.xpath(urls_xpath))
        for single_url in urls:
            single_url = get_full_url(original_url, single_url)
            request = Request(single_url, callback=self.level_3)
            request.meta['category'] = category
            yield request
    
    def level_3(self, response):
        category = response.meta['category']
        original_url = response.url
        product_xpaths = {
            "ProductName":"//span[@itemprop='name']/text()",
            "PicURL":"//a[contains(@class,'product-image')]//img[@itemprop='image']/@src",
            "ProductManufacturer":"//div[@itemprop='manufacturer']/a/text()",
            "source_internal_id": "//*[contains(@itemtype, '/Product')]//a[@data-id]/@data-id"
        }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['TestUrl'] = original_url
        picurl = product.get("PicURL", "")
        if picurl and picurl[:2] == "//":
            product["PicURL"] = "https:" + product["PicURL"]
        if picurl and picurl[:1] == "/":
            product["PicURL"] = get_full_url(original_url, picurl)

        product["OriginalCategoryName"] = category['category_path']

        id_value = self.extract(response.xpath("//*[normalize-space(text())='MPN']/following-sibling::td[1]/text()"))
        if id_value:
            product_id = self.product_id(product)
            product_id['ID_kind'] = "MPN"
            product_id['ID_value'] = id_value
            yield product_id
        
        id_value = self.extract(response.xpath("//*[normalize-space(text())='EAN']/following-sibling::td[1]/text()"))
        if id_value:
            product_id = self.product_id(product)
            product_id['ID_kind'] = "EAN"
            product_id['ID_value'] = int(id_value)
            yield product_id
        
        id_value = self.extract(response.xpath("//*[normalize-space(text())='UPC']/following-sibling::td[1]/text()"))
        if id_value:
            product_id = self.product_id(product)
            product_id['ID_kind'] = "UPC"
            product_id['ID_value'] = id_value
            yield product_id

        yield product

        url_xpath = "//div[@class='see-more']/a/@href"
        single_url = self.extract(response.xpath(url_xpath))
        if single_url:
            single_url = get_full_url(original_url, single_url)
            request = Request(single_url, callback=self.level_4)
            request.meta['product'] = product
            yield request
    
    def level_4(self, response):
        product = response.meta['product']
        original_url = response.url

        button_next_url = self.extract(response.xpath("//div[contains(@class, 'bottom')]//a[contains(text(), 'Next')]/@href"))
        if button_next_url:
            button_next_url = get_full_url(original_url, button_next_url)
            request = Request(button_next_url, callback=self.level_4)
            request.meta['product'] = product
            yield request

        containers_xpath = "//section[@id='reviews-all']/article"
        containers = response.xpath(containers_xpath)
        for review_container in containers:
            review = ReviewItem()
            review['ProductName'] = product['ProductName']
            review['SourceTestRating'] = self.extract(review_container.xpath("string(number(substring-before(substring-after(.//div[@class='review-meta']//span[@class='star-color']/@style,'width:'),'%')) div 20)"))
            review['TestDateText'] = self.extract(review_container.xpath(".//time/@datetime"))
            review['TestPros'] = self.extract(review_container.xpath(".//p[@class='review-pros']/text()"))
            review['TestCons'] = self.extract(review_container.xpath(".//p[@class='review-cons']/text()"))
            review['TestSummary'] = self.extract(review_container.xpath(".//section[@class='review-body']/div/text()"))
            review['Author'] = self.extract(review_container.xpath(".//div[@class='review-byline']/a/text()"))
            review['TestTitle'] = self.extract(review_container.xpath(".//section[@class='review-header']/h3/a/span/text()"))
            review['TestUrl'] = self.extract(review_container.xpath(".//section[@class='review-header']/h3/a/@href"))
            review['TestUrl'] = get_full_url(original_url, review['TestUrl'])
            matches = None
            if review["TestDateText"]:
                matches = re.search("(\d[^\s]*(?=T))",
                                    review["TestDateText"], re.IGNORECASE)
            if matches:
                review["TestDateText"] = matches.group(1)
            review["SourceTestScale"] = "5"
            review["DBaseCategoryName"] = "USER"
            yield review
            
        
