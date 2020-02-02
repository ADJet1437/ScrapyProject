
from datetime import datetime

from alascrapy.items import CategoryItem, ProductItem, ReviewItem, \
    ProductIdItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils


class Rtings_comSpider(AlaSpider):
    name = 'rtings_com'
    allowed_domains = ['rtings.com']
    start_urls = ['https://www.rtings.com/headphones/reviews',
                  'https://www.rtings.com/monitor/reviews',
                  'https://www.rtings.com/tv/reviews']

    def __init__(self, *args, **kwargs):
        super(Rtings_comSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

        # Testing another last date
        # self.stored_last_date = datetime(2018, 10, 1)

    def parse(self, response):
        reviews_li_xpath = '//li[@class="silo_reviews_page-product"]'
        reviews_li = response.xpath(reviews_li_xpath)

        for review in reviews_li:
            product_name_xpath = './/a//text()'
            product_name = review.xpath(product_name_xpath).get()

            # 'Lineup' are a comparison of products in the same category,
            #   not individual reviews.
            if product_name != "Lineup":
                review_url_xpath = './/a/@href'
                review_url = review.xpath(review_url_xpath).get()
                # print " review_url: " + review_url

                yield response.follow(url=review_url,
                                      callback=self.parse_review_and_product)

    def parse_review_and_product(self, response):
        # Checking date
        review_date_xpath = '//span[@property="dc:date"]//text()'
        date = response.xpath(review_date_xpath).get()
        date = datetime.strptime(date, '%b %d, %Y')

        # In case the review is new
        if date > self.stored_last_date:
            # Since there's no number we ca use from the page as an ID. We'll
            #   use the name of the product as the 'product_name'
            # The following was tried to get a 'source_internal_id'
            # 1. SKU: more than one data-sku-ids
            #   They are linking to other website's products.
            # 2. Article id: Doesn't exist in the html code
            # 3. Post id: Doesn't exist in the html code
            # 4.Numbers in the URL: URL doesn't have numbers
            #
            # Therefore we are using the last part of the URL
            source_internal_id = response.url.split("reviews/")[-1]

            # Preparing to create a review item ------------------------------
            pros, cons = response.xpath('//div[@class="row summaries"]')
            pros = pros.xpath('./div[@class="col-3_4-c"]/ul//li//'
                              'text()').getall()
            cons = cons.xpath('./div[@class="col-3_4-c"]/ul//li//'
                              'text()').getall()

            product_name = response.xpath('//h1[@class="item"]//'
                                          'text()').get()

            review_xpaths = {"TestTitle": "//meta[@property='og:title']/"
                                          "@content",
                             "TestSummary": "//meta[@property='og:description'"
                                            "]/@content",
                             "Author": "//span[@itemprop='author']/span["
                                       "@itemprop='name']//text()",
                             # "TestVerdict": "",
                             # "SourceTestRating": "", # could not find any.
                             }
            # ---------------------------------------------------------------

            review = self.init_item_by_xpaths(response, "review",
                                              review_xpaths)

            # Setting the rest of review's properties -----------------------
            review['SourceTestScale'] = None
            review['SourceTestRating'] = None
            review['ProductName'] = product_name
            review['TestDateText'] = datetime.strftime(date, '%Y-%m-%d')
            review['TestPros'] = ";".join(pros)
            review['TestCons'] = ";".join(cons)
            review['DBaseCategoryName'] = 'PRO'

            review['source_internal_id'] = source_internal_id
            review['TestUrl'] = response.url
            # ---------------------------------------------------------------

            product = ProductItem()
            # Setting the product's properties ------------------------------
            original_category_name_xpath = '//div[@class="breadcrumbs"]/ol/li'\
                                           '[2]/a/span/text()'
            original_category_name = response.xpath(
                                     original_category_name_xpath).get()

            product['OriginalCategoryName'] = original_category_name
            product['ProductName'] = product_name

            product['source_internal_id'] = source_internal_id
            product['TestUrl'] = response.url

            product_picture_url_xpath = '//meta[@property="og:image"]/@content'
            product_picture_url = response.xpath(
                                            product_picture_url_xpath).get()
            product['PicURL'] = product_picture_url
            # ---------------------------------------------------------------

            yield review
            yield product
