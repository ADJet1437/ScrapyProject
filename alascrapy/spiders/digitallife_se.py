# -*- coding: utf8 -*-

from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format, remove_prefix
from alascrapy.items import CategoryItem, ProductIdItem
import json

class Pricerunner_seSpider(AlaSpider):
    name = 'digitallife_se'
    allowed_domains = ['digitallife.se']
    start_url = "http://digitallife.se/api/get_posts/?post_type=teknik&page="

    def start_requests(self):
        page_num = 0
        first_page_url = self.start_url + str(page_num)
        request = Request(first_page_url, callback=self.parse)
        request.meta['page_number'] = page_num
        yield request
    
    def parse(self, response):

        content = json.loads(response.text)
        contents = content['posts']

        if not contents:
            return

        for c in contents:
            if c.get('url', ''):
                request = Request(c['url'], callback=self.level_2)

                if c.get('id', ''):
                    request.meta['source_internal_id'] = c['id']

                if c.get('taxonomy_tech-category', []):
                    raw_type = c['taxonomy_tech-category'][0].get('title', '')
                    request.meta['OriginalCategoryName'] = raw_type.replace('&amp;', '&')

                yield request

        next_page_num = response.meta['page_number'] + 1
        next_page_url = self.start_url + str(next_page_num)
        request = Request(next_page_url, callback=self.parse)
        request.meta['page_number'] = next_page_num
        yield request

    def level_2(self, response):
        original_url = response.url
        
        product_xpaths = {
            "PicURL": "//div[@class='entry-content']/img[1]/@src",
            "ProductName": "//h1[@class='entry-title']/text()"
        }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['TestUrl'] = original_url

        product_name = product.get('ProductName', '')
        product_name = remove_prefix(product_name, 'Test: ')
        product['ProductName'] = product_name

        if product.get('PicURL', ''):
            product['PicURL'] = get_full_url(response, product['PicURL'])

        category_name = response.meta.get('OriginalCategoryName', '')
        if category_name:
            product['OriginalCategoryName'] = response.meta['OriginalCategoryName']
            category_url_xpath = u"//div[@itemtype='http://data-vocabulary.org/Breadcrumb' and .//text()[normalize-space()]='{}']/a/@href".format(category_name)

            category_url = self.extract_xpath(response, category_url_xpath)
            if category_url:
                category = CategoryItem()
                category["category_leaf"] = category_name
                category["category_path"] = category_name
                category["category_url"] = get_full_url(response, category_url)
                yield category

        source_internal_id = response.meta.get('source_internal_id', '')
        if source_internal_id:
            product_id = ProductIdItem()
            product_id['ProductName'] = product_name
            product_id['source_internal_id'] = source_internal_id
            product_id['ID_kind'] = 'digitallife_se_internal_id'
            product_id['ID_value'] = source_internal_id
            yield product_id

            product['source_internal_id'] = source_internal_id

        review_xpaths = {
            "SourceTestRating":"//meta[@itemprop='ratingValue']/@content",
            "TestDateText":"//time[@class='published updated']/@datetime",
            "TestPros":"//div[@class='review-detail product--pros']/ul/li//text()",
            "TestCons":"//div[@class='review-detail product--cons']/ul/li//text()",
            "TestSummary":"//meta[@property='og:description']/@content",
            "Author":"//span[@class='author vcard']//text()[normalize-space()]",
            "TestTitle":"//h1[@class='entry-title']/text()",
            "TestVerdict":"//section[@class='verdict-content']//p[1]//text()"
        }
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        review['TestUrl'] = original_url
        review['ProductName'] = product_name
        review['source_internal_id'] = source_internal_id

        awpic_link = review.get("AwardPic", "")
        if awpic_link and awpic_link[:2] == "//":
            review["AwardPic"] = "https:" + review["AwardPic"]
        if awpic_link and awpic_link[:1] == "/":
            review["AwardPic"] = get_full_url(original_url, awpic_link)

        if review.get('TestDateText', ''):
            review['TestDateText'] = date_format(review['TestDateText'], '')

        review["SourceTestScale"] = "5"
        review["DBaseCategoryName"] = "PRO"

        yield product
        yield review
