__author__ = 'jim'

import re

from scrapy.http import Request

from alascrapy.items import ProductItem, ReviewItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import date_format
from alascrapy.lib.generic import get_full_url


class HispazoneComSpider(AlaSpider):
    name = 'hispazone_com'
    allowed_domains = ['hispazone.com']
    start_urls = ['https://www.hispazone.com/reviews/']
    awards_dict = {"bestxgames": "THE BEST FOR GAMES", "editors": "EDITOR'S CHOICE",
                   "qualityprice": "RECOMENDED QUALITY / PRICE", "recomprod": "RECOMMENDED PRODUCT",
                   "bestperf": "BEST PERFORMANCE"}
            
    def parse(self, response):
        product_urls = self.extract_list(response.xpath(
            '//div[@class="article-list-block"]/div[@class="item"]/div/a/@href'))
        for product_url in product_urls:
            yield Request(url=get_full_url(response, product_url), callback=self.parse_product)
        
    def parse_product(self, response):
        url = response.meta.get('url', response.url)
        summary = response.meta.get('summary', self.extract_all(response.xpath(
            '//div[@class="article-content"]/p[text()][1]//text()')))

        last_page_url = self.extract(response.xpath('//li[@class="lastmesub"]/a/@href'))
        if last_page_url:
            request = Request(url=get_full_url(response, last_page_url), callback=self.parse_product)
            request.meta['url'] = url
            request.meta['TestSummary'] = summary
            yield request
        else:
            product = ProductItem()
            product['TestUrl'] = url
            product['OriginalCategoryName'] = 'Miscellaneous'
            product['ProductName'] = self.extract(response.xpath('//h1/text()'))
            product['PicURL'] = self.extract(response.xpath('//meta[@property="og:image"]/@content'))
            product['ProductManufacturer'] = self.extract(response.xpath('//div[@class="dcol"]/a/text()'))
            yield product

            review = ReviewItem()
            review['DBaseCategoryName'] = "PRO"
            review['ProductName'] = product['ProductName']
            review['TestUrl'] = url
            date = self.extract(response.xpath('//div[@class="article-header"]/span/span[2]/text()'))
            review['TestDateText'] = date_format(date, '%d/%m/%Y')
            review['Author'] = self.extract(response.xpath('//div[@class="article-header"]/span/span[1]/a/text()'))
            review['TestTitle'] = product['ProductName']
            review['TestSummary'] = summary
            review['TestVerdict'] = self.extract_all(response.xpath(
                    '//div[@class="article-content"]/p[text()][last()]//text()'))
            award = self.extract(response.xpath('//div[@class="revPremioImagen"]/img/@src'))
            if award:
                review['AwardPic'] = get_full_url(response, award)
                award_id = re.split('[./]', award)[-2]
                review['award'] = self.awards_dict[award_id]
            yield review
