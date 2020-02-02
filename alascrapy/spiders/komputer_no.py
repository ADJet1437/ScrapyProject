import json
from scrapy.http import Request
from alascrapy.items import ProductItem, CategoryItem, ReviewItem, ProductIdItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format

class KomputerNoSpider(AlaSpider):
    name = 'komputer_no_reviews'
    start_urls = ['http://test.komputer.no/test/telefon/sony/sony-xperia-z5-compact/'] #http://test.komputer.no/cms/wp-admin/admin-ajax.php?action=product-search&types[]=Telefon&orderby=relevance&order=desc&page=1
    allowed_domains = ['test.komputer.no']

##Start with parsing maybe use curl to get content
    def parse(self, response):
        print "at least tries"
        request = Request(response.url, callback=self.parse_review)
        request.meta['category'] = 'Telefon'
        yield request
        '''
        #product_url_xpath = "//tr[@class='prod_list_row']//td[not(@*)]/a/@href"
        #product_urls = self.extract_list(response.xpath(product_url_xpath))

        #jsonObject = json.loads(response.body)

        #if jsonObject['success'] == 'true':
        #    print "fine"
        #else:
        #    print "not how it goes"
               if not product_urls:
            request = self._retry(response.request)
            yield request
            return

        for product_url in product_urls:
            product_url = get_full_url(response, product_url)
            request = Request(product_url, callback=self.parse_product)
            yield request

        next_page_xpath = "//span[@class='next']/a/@href"
        next_page = self.extract(response.xpath(next_page_xpath))
        if next_page:
            next_page = get_full_url(response, next_page)
            request = Request(next_page, callback=self.parse)
            yield request
'''
    def parse_review(self, response):

        product = ProductItem()

        product_name_xpath = "//hearder[@class='gutter-top']/h1[@itemprop='name']/text()"
        ocn_xpath = "//div[@class='gutter-vertical']//span[@class='tags']/atext()"
        pic_url_xpath = "//meta[@property='og:image']/text()"

        product['ProductName'] = self.extract(response.xpath(product_name_xpath))
        product['OriginalCategoryName'] = response.meta['category']
        product['PicURL'] = self.extract(response.xpath(pic_url_xpath))

        yield product

        testTitle_xpath = "//meta[@property='og:title']/text()"
        testSummary_xpath = "//div[@class='segment-article gutter-bottom-lg']div[class='row']/div/p/text()"
        author_xpath = ".//span[@class='review-created-by']/text()"
        testDateText_xpath = ".//span[@class='review-created-by']/text()"
        sourceTestRating_xpath = ".//span[@class='review-rating']/img/@src"

        review = ReviewItem()
        review["TestUrl"] = response.url
        review["DBaseCategoryName"] = "USER"
        review["SourceTestScale"] = "5";
        review["ProductName"] = product["ProductName"]
        review["TestTitle"] = self.extract_all(response.xpath(testTitle_xpath))
        review["TestSummary"] = self.extract_all(response.xpath(testSummary_xpath), " ")
        review["Author"] = self.extract(response.xpath(author_xpath))
        review["TestDateText"] = self.extract(response.xpath(testDateText_xpath))


'''
    def parse_review(self, response):
        print "REVIEW"
        product = response.meta['product']

        testSummary_xpath = ".//div[@class='review-text']/p/text()"
        author_xpath = ".//span[@class='review-created-by']/text()"
        testDateText_xpath = ".//span[@class='review-created-by']/text()"
        sourceTestRating_xpath = ".//span[@class='review-rating']/img/@src"

        divs = response.xpath("//div[@class='reviews']")
        for div in divs.xpath("./div"):
            review = ReviewItem()
            review["TestUrl"] = response.url
            review["DBaseCategoryName"] = "USER"
            review["SourceTestScale"] = "5";
            review["ProductName"] = product["ProductName"]
            review["TestTitle"] = product["ProductName"]
            review["TestSummary"] = self.extract(response.xpath(testSummary_xpath))
            review["Author"] = self.extract(div.xpath(author_xpath))
            review["TestDateText"] = self.extract(div.xpath(testDateText_xpath))

            review["SourceTestRating"] = self.extract(div.xpath(sourceTestRating_xpath))
            if review["SourceTestRating"] != '':
                review["SourceTestRating"] = self.clear_score(review["SourceTestRating"])

            if review["Author"] != '':
                yield review '''