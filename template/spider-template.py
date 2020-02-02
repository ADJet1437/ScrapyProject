from alascrapy.spiders.base_spiders import ala_spider as spiders


class NameSpider(spiders.AlaSpider):
    name = 'name_com'
    allowed_domains = ['name.com']
    start_urls = ['https://www.name.com/reviews']

    def parse(self, response):
        next_page_xpath = '//a[@class="next"]/@href'
        next_page_link = self.extract(response.xpath(next_page_xpath))
        if next_page_link:
            print('Next page link:', next_page_link)
            yield response.follow(url=next_page_link, callback=self.parse)

        reviews_xpath = '//a[@class="review"]/@href'
        review_links = response.xpath(reviews_xpath).extract()
        for link in review_links:
            print('Review link:', link)
            yield response.follow(url=link, callback=self.parse_review_page)

    def parse_review_page(self, response):
        print('URL:', response.url)
        product = self.parse_product(response)
        review = self.parse_review(response)
        print(product)
        print(review)
        yield product
        yield review

    def get_product_name(self, response):
        product_name_xpath = ''
        product_name = self.extract(response.xpath(product_name_xpath))
        product_name = product_name.trim()
        return product_name

    def get_source_internal_id(self, response):
        sii_xpath = ''
        sii = self.extract(response.xpath(sii_xpath))
        return sii

    def parse_product(self, response):
        product_xpaths = {
            'OriginalCategoryName': '',
            'PicURL': '',
            'ProductManufacturer': '',
            'ProductName': '',
            'source_id': '',
            'source_internal_id': '',
            'TestUrl': '',
        }
        product = self.init_item_by_xpaths(response, 'product', product_xpaths)

        product['ProductName'] = self.get_product_name(response)
        product['source_internal_id'] = self.get_source_internal_id(response)
        product['source_id'] = self.spider_conf['source_id']

        return product

    def parse_review(self, response):
        review_xpaths = {
            'Author': '',
            'award': '',
            'AwardPic': '',
            'countries': '',
            'DBaseCategoryName': '',
            'ProductName': '',
            'source_id': '',
            'source_internal_id': '',
            'SourceTestRating': '',
            'SourceTestScale': '',
            'TestCons': '',
            'TestDateText': '',
            'TestPros': '',
            'TestSummary': '',
            'TestTitle': '',
            'TestUrl': '',
            'TestVerdict': '',
        }

        review = self.init_item_by_xpaths(response, 'review', review_xpaths)

        review['ProductName'] = self.get_product_name(response)
        review['source_internal_id'] = self.get_source_internal_id(response)
        review['source_id'] = self.spider_conf['source_id']
        review['DBaseCategoryName'] = 'PRO'

        return review
