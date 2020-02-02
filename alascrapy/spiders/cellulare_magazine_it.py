#!/usr/bin/env python

from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format

class CellulareMagazineItSpider(AlaSpider):
    name = 'cellulare_magazine_it'
    allowed_domains = ["cellulare-magazine.it"]
    start_urls = ['http://www.cellulare-magazine.it/recensioni.php']
    
    def parse(self, response):
        brand_name_xpath = './text()'
        brand_url_xpath = './@value'
        brand_list_sel = response.xpath("//select[@id='selProduttore']/option[not(@selected)]")

        for brand in brand_list_sel:
            brand_name = self.extract(brand.xpath(brand_name_xpath))
            brand_url = self.extract(brand.xpath(brand_url_xpath))
            brand_url = get_full_url(response.url, brand_url)
            request = Request(brand_url, callback=self.parse_brand_list)
            request.meta['brand']=brand_name
            yield request

    def parse_brand_list(self, response):
        review_urls_xpath = "//*[@id='HM_topic']//h1/a/@href"
        next_page_xpath = "//a[@id='loadmore']/@href"

        review_urls = self.extract_list(response.xpath(review_urls_xpath))
        for review_url in review_urls:
            review_url = get_full_url(response.url, review_url)
            request = Request(review_url, callback=self.parse_review)
            request.meta['brand']=response.meta['brand']
            yield request

        next_page_url = self.extract(response.xpath(next_page_xpath))
        if next_page_url:
            next_page_url = get_full_url(response.url, next_page_url)
            request = Request(next_page_url, callback=self.parse_brand_list)
            request.meta['brand']=response.meta['brand']
            yield request
    

    def parse_review(self, response):
        product_xpaths = { "PicURL": "//div[@class='grid_2']/img/@src",
                           "ProductName": "//h2/center/text()"
                         }

        review_xpaths = { "TestTitle": "//div[@id='NWS_container']//h1/text()",
                          "TestSummary": "//div[@id='NWS_content']/p[1]/text()",
                          "TestDateText": "//div[@id='NWS_subtitle']/date/text()"
                        }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        
        #other field
        product["PicURL"] = get_full_url(response.url, product["PicURL"])
        product["OriginalCategoryName"] = 'Cellulari'
        product["ProductManufacturer"] = response.meta['brand']

        review["TestUrl"] = product["TestUrl"]
        review["ProductName"] = product["ProductName"]
        review["DBaseCategoryName"] = "PRO"
        review["TestDateText"] = date_format(review["TestDateText"], "%d %b %Y")
        yield product
        yield review

