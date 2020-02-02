__author__ = 'jim'

import re

from scrapy.http import Request

from alascrapy.items import ProductItem, ReviewItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format


class AttComSpider(AlaSpider):
    name = 'att_com'
    allowed_domains = ['att.com', 'bazaarvoice.com']
    start_urls = ['https://www.att.com/shop/wireless/devices/cellphones.deviceListView.json',
                  'https://www.att.com/shop/wireless/devices/tablets.deviceListView.json',
                  'https://www.att.com/shop/wireless/devices/internetdevices.deviceListView.json']

    bv_key = '9v8vw9jrx3krjtkp26homrdl8'
    bv_version = '5.5'
    bv_code = '4773-en_us'

    def parse(self, response):
        content = self.extract_all(response.xpath('//body//text()'))
        product_urls = re.findall('href="([^"#]+)[^<>]+Review\(s\)', content)
        for product_url in product_urls:
            product_url = get_full_url(response, product_url)
            request = Request(url=product_url, callback=self.parse_product)
            yield request

    def parse_product(self, response):
        content = self.extract(response.xpath('//div[@ng-controller="breadCrumbsController"]/@ng-init'))
        info = re.findall('\[(.+)\]', content)
        info_list = info[0].split('"')
        product = ProductItem()
        product['TestUrl'] = response.url
        product['OriginalCategoryName'] = info_list[19]
        if len(info_list) > 33:
            product['ProductName'] = info_list[35]
        else:
            product['ProductName'] = info_list[27]
        product['PicURL'] = self.extract(response.xpath('//meta[@property="og:image"]/@content'))
        brand = self.extract(response.xpath('//script[@type="text/javascript"][contains(text(),"brand")]/text()'))
        brand_match = re.findall("brand: '([^']+)'", brand)
        if brand_match:
            product['ProductManufacturer'] = brand_match[0]
        yield product

        sku = self.extract(response.xpath('//meta[@name="MDVext.page.attributes.sku"]/@content'))

        test_url = 'http://api.bazaarvoice.com/data/batch.json?passkey=%s&apiversion=%s' \
                   '&displaycode=%s&resource.q0=reviews&filter.q0=isratingsonly:eq:false' \
                   '&filter.q0=productid:eq:%s' \
                   '&filter.q0=contentlocale:eq:en_US&sort.q0=submissiontime:desc&limit.q0=100&offset.q0=0' % \
                   (self.bv_key, self.bv_version, self.bv_code, sku)

        request = Request(url=test_url, callback=self.parse_reviews)
        request.meta['product'] = product
        yield request

    @staticmethod
    def parse_reviews(response):
        reviews = re.findall(r'"CID":(((?!("Badges")).)+)}', response.body)

        for item in reviews:
            try:
                review = item[0]
                user_review = ReviewItem()
                user_review['DBaseCategoryName'] = "USER"
                user_review['ProductName'] = response.meta['product']['ProductName']
                user_review['TestUrl'] = response.meta['product']['TestUrl']
                date = re.findall(r'"SubmissionTime":"([\d-]+)', review)
                user_review['TestDateText'] = date_format(date[0], "%Y-%m-%d")
                rate = re.findall(r'"Rating":([\d])', review)
                user_review['SourceTestRating'] = rate[0]
                author = re.findall(r'"UserNickname":"([^"]+)', review)
                if author:
                    user_review['Author'] = author[0]
                title = re.findall(r'"Title":"([^"]+)', review)
                if title:
                    user_review['TestTitle'] = title[0]
                summary = re.findall(r'"ReviewText":"([^"]+)', review)
                if summary:
                    user_review['TestSummary'] = summary[0]
                yield user_review
            except:
                pass
