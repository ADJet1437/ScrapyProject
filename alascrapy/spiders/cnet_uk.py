# -*- coding: utf-8 -*-
import scrapy

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider


class CnetUKSpider(AlaSpider):
    name = 'cnet_uk'
    allowed_domains = ['cnet.com']
    start_urls = ['https://www.cnet.com/uk/reviews/']

    def parse(self, response):
        links_xpath = '//div[@class="assetText"]/a/@href'
        links = self.extract_list(response.xpath(links_xpath))

        for url in links:
            url = response.urljoin(url)
            yield response.follow(url, callback=self.parse_page)

        url = response.xpath('//a[@class="load-more"]/@href').extract_first()
        next_page = response.urljoin(url)
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_page(self, response):
        product_xpaths = {
            'PicURL': '//meta[@property="og:image"]/@content',

            'TestUrl': '//meta[@property="og:url"]/@content',
            'OriginalCategoryName': 'substring-before(//meta'
                                    '[@name="news_keywords"]/@content, ",")'

        }

        review_xpaths = {
            'TestSummary': '//meta[@property="og:description"]/@content',
            'Author': '//a[@rel="author"]/span/text()',

            'TestDateText': 'substring-before(//time[@class="dtreviewed"]'
                            '/@datetime, "T")',

            'TestVerdict': '//p[@class="theBottomLine"]/span/text()',

            'TestPros': '//p[@class="theGood"]/span/text()',
            'TestCons': '//p[@class="theBad"]/span/text()',

        }

        review = self.init_item_by_xpaths(response, 'review', review_xpaths)
        product = self.init_item_by_xpaths(response, 'product', product_xpaths)

        title_xpath = '//meta[@property="og:title"]/@content'
        title = self.extract(response.xpath(title_xpath))
        name_xpath = '//h1[@class="headline"]/'\
            'span/span[@class="itemreviewed"]/text() | '\
            '//meta[@property="og:title"]/@content'
        product_name = self.extract(response.xpath(name_xpath))

        if product_name:
            product['ProductName'] = product_name

        else:
            product['ProductName'] = title

        RATING_SCALE = 10
        rating_xpath = '//div[@class="col-1 overall"]/div/span/text()'
        rating = self.extract(response.xpath(rating_xpath))
        if rating:
            review['SourceTestRating'] = rating
            review['SourceTestScale'] = RATING_SCALE

        db_cat = 'PRO'

        review['DBaseCategoryName'] = db_cat
        review['TestTitle'] = title
        review['ProductName'] = product_name
        yield review
        yield product
