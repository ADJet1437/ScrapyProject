# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from alascrapy.spiders.base_spiders.ala_crawl import AlaSpider
from alascrapy.items import ProductItem, ProductIdItem, ReviewItem


class AllesbesteDeSpider(AlaSpider):
    name = 'allesbeste_de'
    allowed_domains = ['allesbeste.de']
    start_urls = ['https://www.allesbeste.de/ab-alatest-feed/']

    def parse(self, response):
        product_ = ProductItem()
        product_id = ProductIdItem()
        review = ReviewItem()
        contents = response.xpath("//Product")
        for product in contents:
            product_name = self.extract(product.xpath(".//ProductName/text()")).strip()
            testurl = self.extract(product.xpath(".//TestUrl[1]/text()")).strip()
            manufacturer = self.extract(product.xpath(".//ProductManufacturer/text()")).strip()
            pic_url = self.extract(product.xpath('.//PicUrl/text()')).strip()
            ocn = self.extract(product.xpath('.//OriginalCategoryName/text()')).strip()
            rating = self.extract(product.xpath('.//SourceTestRating/text()')).strip()
            scale = self.extract(product.xpath('.//SourceTestScale/text()')).strip()
            pro = self.extract_all(product.xpath('.//TestPros/text()'))
            con = self.extract_all(product.xpath('.//TestCons/text()'))
            pro = ''.join(x.rstrip('\n') for x in pro)
            con = ''.join(x.rstrip('\n') for x in con)
            summary = self.extract_all(product.xpath('.//TestSummary/text()')).strip()
            verdict = self.extract_all(product.xpath('.//TestVerdict/text()')).strip()
            date = self.extract(product.xpath(".//TestDateText/text()")).strip()
            author = self.extract(product.xpath('.//Author/text()')).strip()
            dbcn = self.extract(product.xpath('.//DBaseCategoryName/text()')).strip()
            id_kinds = self.extract_list(product.xpath(".//product_ids//ID_kind/text()"))
            id_values = self.extract_list(product.xpath(".//product_ids//ID_value/text()"))
            # product item
            product_name = self.cleanup_product_names(product_name)
            product_['ProductName'] = product_name
            product_['OriginalCategoryName'] = ocn
            product_['TestUrl'] = testurl
            product_['PicURL'] = pic_url
            product_['ProductManufacturer'] = manufacturer
            # # review item
            review['ProductName'] = product_name
            review['TestUrl'] = testurl
            review['SourceTestRating'] = rating
            review['SourceTestScale'] =scale
            review['TestPros'] = pro
            review['TestCons'] = con
            review['TestSummary'] = summary
            review['TestVerdict'] = verdict
            review['TestDateText'] = date
            review['Author'] = author
            review['DBaseCategoryName'] = dbcn
            # # product id items
            for id_kind, id_value in zip(id_kinds, id_values):
                # if id_kind == 'EAN':
                #     product_['source_internal_id'] = id_value
                #     review['source_internal_id'] = id_value
                product_id = ProductIdItem.from_product(product,
                                                       kind=id_kind,
                                                       value=id_value)
                yield product_id
            yield product_
            yield review
    
    def cleanup_product_names(self, product_name):
        if u'»' in product_name:
            product_name = product_name.replace(u'»', '').replace(u'«', '')
        if '"' in product_name:
            product_name = product_name.replace('"', '').rstrip('\n')
        return product_name
        

