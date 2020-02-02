import re
from scrapy.http import Request

from alascrapy.items import ProductItem, ReviewItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url

#BazaarVoice reviews
'''
url:
http://api.bazaarvoice.com/data/batch.json?passkey=lalbuvsywhdk5nouwvfd9pwe4&apiversion=5.5&displaycode=10030-no_no
&resource.q0=products&filter.q0=id%3Aeq%3ANO51245&stats.q0=reviews&filteredstats.q0=reviews
&filter_reviews.q0=contentlocale%3Aeq%3Ano_NO%2Csv_SE&filter_reviewcomments.q0=contentlocale%3Aeq%3Ano_NO%2Csv_SE&resource.q1=reviews&filter.q1=isratingsonly%3Aeq%3Afalse
&filter.q1=productid%3Aeq%3ANO51245&filter.q1=contentlocale%3Aeq%3Ano_NO%2Csv_SE&sort.q1=rating%3Adesc&stats.q1=reviews&filteredstats.q1=reviews&include.q1=authors%2Cproducts%2Ccomments
&filter_reviews.q1=contentlocale%3Aeq%3Ano_NO%2Csv_SE&filter_reviewcomments.q1=contentlocale%3Aeq%3Ano_NO%2Csv_SE&filter_comments.q1=contentlocale%3Aeq%3Ano_NO%2Csv_SE&limit.q1=8
&offset.q1=0&limit_comments.q1=3&resource.q2=reviews
&filter.q2=productid%3Aeq%3ANO51245&filter.q2=contentlocale%3Aeq%3Ano_NO%2Csv_SE&limit.q2=1&resource.q3=reviews&filter.q3=productid%3Aeq%3ANO51245&filter.q3=isratingsonly%3Aeq%3Afalse
&filter.q3=rating%3Agt%3A3&filter.q3=totalpositivefeedbackcount%3Agte%3A3
&filter.q3=contentlocale%3Aeq%3Ano_NO%2Csv_SE
&sort.q3=totalpositivefeedbackcount%3Adesc&include.q3=authors%2Creviews%2Cproducts
&filter_reviews.q3=contentlocale%3Aeq%3Ano_NO%2Csv_SE&limit.q3=1
&resource.q4=reviews&filter.q4=productid%3Aeq%3ANO51245&filter.q4=isratingsonly%3Aeq%3Afalse&filter.q4=rating%3Alte%3A3
&filter.q4=totalpositivefeedbackcount%3Agte%3A3&filter.q4=contentlocale%3Aeq%3Ano_NO%2Csv_SE&sort.q4=totalpositivefeedbackcount%3Adesc&include.q4=authors%2Creviews%2Cproducts
&filter_reviews.q4=contentlocale%3Aeq%3Ano_NO%2Csv_SE&limit.q4=1&callback=bv_1111_24360
'''
class SibaNoSpider(AlaSpider):
    name = 'siba_no_reviews'
    allowed_domains = ['komplett.no']
    start_urls = ['http://www.siba.no/tv-lyd-bilde/tv/smart-tv/lg-32lh604v-129717']

    def parse(self, response):

        product = ProductItem()

        productname_xpath = "//div[@class='product-title']//text()"
        ocn_xpath = "//ul[@id='breadcrumb']//li[contains(@class, 'child level')]//text()"
        picurl_xpath = "//div[@class='product-main-image']/a/img/@data-src"
        productid_xpath = "//input[@class='js-buybutton btn green big']/@data-item-id"

        product['TestUrl'] = response.url
        product['OriginalCategoryName'] = self.extract_all(response.xpath(ocn_xpath), '->')
        product['ProductName'] = self.extract(response.xpath(productname_xpath))
        print product['ProductName']
        product['PicURL'] = get_full_url(response, self.extract(response.xpath(picurl_xpath)))
        product['source_internal_id'] = self.extract(response.xpath(productid_xpath))
        yield product

        reviews_xpath = "//div[@class='review-page']//div[@itemprop='review']"
        testTitle_xpath = ".//h3[@class='review-title']/text()"
        testSummary_xpath = ".//div[@itemprop='reviewBody']/text()"
        testRating_xpath = ".//meta[@itemprop='ratingValue']/@content"
        testAuthor_xpath = ".//span[@itemprop='author']/text()"
        testDate_xpath = ".//p[@itemprop='datePublished']/text()"


        reviews = response.xpath(reviews_xpath)

        for review_div in reviews:
            review = ReviewItem()
            review['DBaseCategoryName'] = "USER"
            review['ProductName'] = product['ProductName']
            review['TestUrl'] = product['TestUrl']
            review['source_internal_id'] = product['source_internal_id']
            review['SourceTestRating'] = self.extract(review_div.xpath(testRating_xpath))
            review['Author'] = self.extract(review_div.xpath(testAuthor_xpath))
            review['TestTitle'] = self.extract(review_div.xpath(testTitle_xpath))
            review['TestSummary'] = self.extract(review_div.xpath(testSummary_xpath))
            review['TestDateText'] = self.extract(review_div.xpath(testDate_xpath))
            yield review

     #   category_urls = self.extract_list(response.xpath(
     #       "//ul[@class='category-list']/li/a/@href"))
     #   for category_url in category_urls:
     #       yield Request(url=get_full_url(response, category_url), callback=self.parse_category)

    def parse_category(self, response):

        product_list_xpath = "//div[@class='product-list-item ']/a/@href"
        product_urls = self.extract_list(response.xpath(product_list_xpath))
        for product_url in product_urls:
            product_url = get_full_url(response, product_url)
            yield Request(url=product_url, callback=self.parse_review)


    def parse_review(self, response):

        product = ProductItem()

        productname_xpath = "//section[@class='product-main-info']//h1[@itemprop='name']/text()"
        ocn_xpath = "//script[@id='breadcrumbsScript']/@data-model"
        picurl_xpath = "//meta[@itemprop='image']/@content"
        productid_xpath = "//div[@class='product-main-info-partnumber-store']/span[@itemprop='sku']//text()"

        product['TestUrl'] = response.url
        product['OriginalCategoryName'] = re.search('(?<=:").*(?="})', self.extract(response.xpath(ocn_xpath))).group(0)
        product['ProductName'] = self.extract(response.xpath(productname_xpath))
        product['PicURL'] = get_full_url(response, self.extract(response.xpath(picurl_xpath)))
        product['source_internal_id'] = self.extract(response.xpath(productid_xpath))
        yield product

        reviews_xpath = "//div[@class='review-page']//div[@itemprop='review']"
        testTitle_xpath = ".//h3[@class='review-title']/text()"
        testSummary_xpath = ".//div[@itemprop='reviewBody']/text()"
        testRating_xpath = ".//meta[@itemprop='ratingValue']/@content"
        testAuthor_xpath = ".//span[@itemprop='author']/text()"
        testDate_xpath = ".//p[@itemprop='datePublished']/text()"


        reviews = response.xpath(reviews_xpath)

        for review_div in reviews:
            review = ReviewItem()
            review['DBaseCategoryName'] = "USER"
            review['ProductName'] = product['ProductName']
            review['TestUrl'] = product['TestUrl']
            review['source_internal_id'] = product['source_internal_id']
            review['SourceTestRating'] = self.extract(review_div.xpath(testRating_xpath))
            review['Author'] = self.extract(review_div.xpath(testAuthor_xpath))
            review['TestTitle'] = self.extract(review_div.xpath(testTitle_xpath))
            review['TestSummary'] = self.extract(review_div.xpath(testSummary_xpath))
            review['TestDateText'] = self.extract(review_div.xpath(testDate_xpath))
            yield review


