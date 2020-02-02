__author__ = 'jim'

from scrapy.http import Request
import json

import dateparser
from alascrapy.items import ProductItem, ReviewItem, CategoryItem, ProductIdItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import date_format, get_query_parameter
from scrapy.selector import Selector
import alascrapy.lib.dao.incremental_scraping as incremental_utils

class RakutenComSpider(AlaSpider):
    name = 'rakuten_com'
    allowed_domains = ['rakuten.com']
    start_urls = ['http://www.rakuten.com/SR/search/GetSearchResults?from=2&sid={0}'.format(str(i)) for i in [1, 8, 9, 27, 28, 30]]

    def parse(self, response):
        jsonresponse = json.loads(response.body_as_unicode())
        categories_html = jsonresponse['FacetsHtml']
        categories_selector = Selector(text=categories_html)
        subCategories_selector = categories_selector.xpath('//li[contains(@data-breadcrumb,"tcid")][not(contains(@class,"noselect"))]')
        is_leaf_category = self.extract(categories_selector.xpath('//li[contains(@data-breadcrumb,"tcid")][contains(@class,"noselect")]'))
        sid = get_query_parameter(response.url, 'sid')
        tcid = get_query_parameter(response.url, 'tcid')

        if is_leaf_category:
            category = CategoryItem()
            category['category_path'] = response.meta['path']
            category['category_leaf'] = category['category_path'].split(' | ')[-1]
            category['category_url'] = response.url
            yield category

            if not self.should_skip_category(category):
                yield Request('http://www.rakuten.com/SR/search/GetSearchResults?from=6&sid={0}&tcid={1}'.format(sid,tcid), callback=self.parse_products)

        else:
            for subSelector in subCategories_selector:
                name = self.extract(subSelector.xpath('.//a/text()'))
                child_tcid = json.loads(self.extract(subSelector.xpath('.//@data-breadcrumb')))['tcid']
                urlDataSubCategory = 'http://www.rakuten.com/SR/search/GetSearchResults?from=2&sid={0}&tcid={1}'.format(sid,child_tcid)
                dic = response.meta
                oldPath = dic.get('path', '')
                dic['path'] = oldPath + ' | ' + name if oldPath else name
                yield Request(urlDataSubCategory, callback=self.parse, meta=dic)

    def parse_products(self, response):
        jsonresponse = json.loads(response.body_as_unicode())
        products = jsonresponse['Products']
        for product in products:
            if product['RatingCount']:
                request = Request(url=product['ProductUrl'], callback=self.parse_product)
                yield request

        # pagination : if products we try next page
        if products:
            sid = get_query_parameter(response.url, 'sid')
            tcid = get_query_parameter(response.url, 'tcid')
            page = get_query_parameter(response.url, 'page')
            if not page:
                page = 0
            nextPage = int(page) + 1
            yield Request(
                'http://www.rakuten.com/SR/search/GetSearchResults?from=6&sid={0}&tcid={1}&page={2}'.format(sid, tcid, nextPage),
                callback=self.parse_products
            )
                
    def parse_product(self, response):
        product = ProductItem()
        product['TestUrl'] = response.url
        product['OriginalCategoryName'] = self.extract_all(
                response.xpath('//div[@class="product-breadcrumbs"]//li//text()'), ' > ')
        product['ProductName'] = self.extract(response.xpath('//h1[@id]/text()'))
        product['source_internal_id'] = self.extract(
                response.xpath('//th[contains(text(),"SKU")]/parent::tr/td/text()'))
        product['PicURL'] = self.extract(response.xpath('//img[@id="productmain"]/@src'))
        product["ProductManufacturer"] = self.extract(
                response.xpath('//th[contains(text(),"Manufacturer")]/parent::tr/td//text()'))
        yield product

        product_id = None
        mpn_id = self.extract(response.xpath('//th[contains(text(),"Mfg")]/parent::tr/td/text()'))
        if mpn_id:
            mpn = ProductIdItem()
            mpn['source_internal_id'] = product["source_internal_id"]
            mpn['ProductName'] = product["ProductName"]
            mpn['ID_kind'] = "MPN"
            mpn['ID_value'] = mpn_id
            product_id = mpn
            yield mpn
        
        upc_id = self.extract(response.xpath('//th[text()="UPC"]/parent::tr/td/text()'))
        if upc_id:
            upc = ProductIdItem()
            upc['source_internal_id'] = product["source_internal_id"]
            upc['ProductName'] = product["ProductName"]
            upc['ID_kind'] = "UPC"
            upc['ID_value'] = upc_id
            product_id = upc
            yield upc

        last_user_review = incremental_utils.get_latest_user_review_date(
            self.mysql_manager, self.spider_conf['source_id'],
            product_id["ID_kind"], product_id['ID_value']
        )

        reviews = response.xpath('//article[@id]')
        for review in reviews:
            dateRaw = self.extract(review.xpath('.//@data-created')).split(' ')[0]
            dateFormatted = date_format(dateRaw, "%m/%d/%Y")

            if dateFormatted:
                dateParsed = dateparser.parse(dateFormatted, date_formats=['%Y-%m-%d'])

                if dateParsed and last_user_review < dateParsed:
                    user_review = ReviewItem()
                    user_review['DBaseCategoryName'] = "USER"
                    user_review['ProductName'] = product['ProductName']
                    user_review['TestUrl'] = product['TestUrl']
                    user_review['TestDateText'] = dateFormatted
                    user_review['SourceTestRating'] = self.extract(review.xpath('./@class')).strip('s')
                    user_review['Author'] = self.extract(review.xpath('.//div/span/em/text()'))
                    user_review['TestTitle'] = self.extract(review.xpath('.//h4/text()'))
                    user_review['TestSummary'] = self.extract_all(review.xpath('.//p[@id]/text()'))
                    user_review['source_internal_id'] = product['source_internal_id']
                    yield user_review
