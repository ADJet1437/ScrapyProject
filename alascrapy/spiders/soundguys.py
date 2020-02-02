# -*- coding: utf-8 -*-
import scrapy
import json

from scrapy.http import FormRequest, Request
from scrapy.selector import Selector
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.items import ProductIdItem


class SoundguysSpider(AlaSpider):
    name = 'soundguys'
    allowed_domains = ['soundguys.com']
    start_urls = ['https://www.soundguys.com/reviews']
    # temporary value for the last page
    MAX_PAGES = 10
    # number of pages that eventually increments
    PAGE_INCR = 1
    pagination_url = 'https://www.soundguys.com/wp-admin/admin-ajax.php'

    def parse(self, response):
        pass
        sel = Selector(response)
        if self.PAGE_INCR > 1:
            json_data = json.loads(response.body)
            sel = Selector(text=json_data.get('content', ''))

        link_xpaths = '//div[@class="loop-info"]/a[@class="overlay-link"]/'\
                      '@href'
        review_links = sel.xpath(link_xpaths).extract()
        for link in review_links:
            yield Request(
                url=link,
                callback=self.parse_review)

        while self.PAGE_INCR <= self.MAX_PAGES:
            self.PAGE_INCR = self.PAGE_INCR + 1
            formdata = {
                'action': 'aa-itajax-sort',
                'loop': 'main',
                'location': 'product_type_archive',
                'thumbnail': '1',
                'rating': '',
                'meta': '1',
                'award': '',
                'badge': '',
                'authorship': '',
                'icon': '1',
                'excerpt': '',
                'sorter': 'recent',
                'numarticles': '12',
                'numpages': '24',
                'paginated': str(self.PAGE_INCR),
                'currentquery[category_name]': 'reviews',
                'aa_is_mobile': 'false'}
            # the final value of the last page
            self.MAX_PAGES = int(formdata.get('numpages'))
            yield FormRequest(
                url=self.pagination_url,
                formdata=formdata,
                callback=self.parse
            )
        else:
            return

    def parse_review(self, response):
        product_xpaths = {'PicURL': '//meta[@property="og:image"]/@content',
                          'TestUrl': '//meta[@property="og:url"]/@content',
                          'source_internal_id': '//body/@data-post-id',
                          }

        review_xpaths = {
            'TestSummary': '//*[@property="og:description"]/@content',
            'Author': '//a[@class="aa_postauthor_link"]/span/span/text()',

            'TestVerdict': '//div[@class="bottomline"]/p/text()',

            'TestDateText': 'substring-before(//meta'
                            '[@property="article:published_time"]'
                            '/@content, "T")',

            'source_internal_id': '//body/@data-post-id',
        }

        review = self.init_item_by_xpaths(response, 'review', review_xpaths)
        product = self.init_item_by_xpaths(response, 'product', product_xpaths)

        title_xpath = '//h1[@class]/text()'
        title = self.extract(response.xpath(title_xpath))

        product_name = title.split(":")[0]
        product_name = product_name.replace(' review', '').strip()
        product_name = product_name.replace(' Review', '').strip()

        ocn_xpath = '//meta[@property="article:section"]/@content'
        ocn = self.extract(response.xpath(ocn_xpath))

        TEST_SCALE = 10

        rating_xpath = '//div[@class="title_postinfo_wrapper"]/'\
                       'div[@class="sg_rating_block"]/figure/figcaption/text()'
        rating = self.extract(response.xpath(rating_xpath))

        if rating:
            review['SourceTestRating'] = rating
            review['SourceTestScale'] = TEST_SCALE

        review['ProductName'] = product_name
        review['DBaseCategoryName'] = 'PRO'
        review['TestTitle'] = title

        yield review

        product['ProductName'] = product_name
        product['OriginalCategoryName'] = ocn

        yield product

        product_id = self.parse_price(product, response)
        yield product_id

    # function to get the prices of the products
    def parse_price(self, product, response):
        price_xpath = '//span[@class="sg_rv_price"]/text()'
        price = self.extract(response.xpath(price_xpath))

        if price:
            return ProductIdItem.from_product(
                product,
                kind='price',
                value=price
            )
