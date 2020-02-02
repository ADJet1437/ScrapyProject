# -*- coding: utf8 -*-
from datetime import datetime

from scrapy.http import Request, HtmlResponse

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem, ProductIdItem


class Goodhousekeeping_comSpider(AlaSpider):
    name = 'goodhousekeeping_com'
    allowed_domains = ['goodhousekeeping.com']

    base_url = 'https://www.goodhousekeeping.com'
    start_urls = [
                  base_url + '/electronics/best-speakers/g3760/'
                             'best-wireless-speakers/',
                  base_url + '/electronics/headphone-reviews/g2039/'
                             'best-over-ear-headphones/',
                  base_url + '/electronics/laptop-reviews/g4890/top-laptops/',
                  base_url + '/appliances/dryer-reviews/',
                  base_url + '/appliances/dishwasher-reviews/'
                  ]

    def __init__(self, *args, **kwargs):
        super(Goodhousekeeping_comSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])


    def parse(self, response):
        # print "     ...PARSE: " + response.url

        # This page has 2 main diff layout styles.
        # 1- Present in these pages:
        # 'https://www.goodhousekeeping.com/electronics/best-speakers/g3760/best-wireless-speakers/',
        # 'https://www.goodhousekeeping.com/electronics/headphone-reviews/g2039/best-over-ear-headphones/',
        # 'https://www.goodhousekeeping.com/electronics/laptop-reviews/g4890/top-laptops/',
        reviews_div_xpath = '//div[@class="feed feed-transporter '\
                            'feed-transporter-with-ads"]/div[contains(@class,'\
                            '"transporter-simple-item")]'

        reviews_div = response.xpath(reviews_div_xpath)

        for r_div in reviews_div:
            review_url = r_div.xpath('./a[1]/@href').get()
            yield response.follow(review_url,
                                  callback=self.parse_review_product)

        # If reviews_div = None, it means we have the second layout style
        # 2- Present in these pages:
        # 'https://www.goodhousekeeping.com/appliances/dryer-reviews/',
        # 'https://www.goodhousekeeping.com/appliances/dishwasher-reviews/'
        if not reviews_div:
            review_urls_xpath = '//div[@class="feed feed-list"]//div[@class='\
                                '"full-item "]/a[1]/@href'
            review_urls = response.xpath(review_urls_xpath).getall()

            for url in review_urls:
                yield response.follow(url,
                                      callback=self.parse_review_product)

    def parse_review_product(self, response):
        # print "     ...PARSE_REVIEW_PRODUCT: " + response.url

        date_xpath = '//meta[@name="article:published_time"]/@content'
        date = response.xpath(date_xpath).get()
        date = date.split(' ')[0]
        date = datetime.strptime(date, '%Y-%m-%d')

        # New article
        if date > self.stored_last_date:

            # REVIEW ITEM ===================================================
            review_xpaths = {
                             'TestTitle': '//meta[@name="title"]/@content',
                             'TestSummary': '//meta[@name="description"]'
                                            '/@content'

             }

            review = self.init_item_by_xpaths(response, "review",
                                              review_xpaths)

            review['TestDateText'] = date.strftime("%Y-%m-%d")
            review['DBaseCategoryName'] = 'PRO'

            # They don't have the authors name in many cases.
            # They put the website's name in case there's no person's name
            author_xpath = '//a[@class="byline-name"]//span/text()'
            author = response.xpath(author_xpath).get()
            if author:
                review['Author'] = author

            # PRODUCT NAME -------------------------------------------------
            # It's weird, but "-"  is diff from "–"
            product_name = review['TestTitle']
            if "-" in product_name:
                product_name = review['TestTitle'].split('-')[0]
            elif "–".decode('utf-8') in product_name:
                product_name = review['TestTitle'].\
                               split('–'.decode('utf-8'))[0]

            words_to_remove = ['Review',
                               'Price and Features',
                               'Price, and Features']

            for w in words_to_remove:
                product_name = product_name.replace(w, '')

            product_name = product_name.strip()
            if product_name.endswith(','):
                product_name = product_name[:-1]

            product_name = product_name.strip()
            review['ProductName'] = product_name
            # --------------------------------------------------------------

            review['TestVerdict'] = None

            # RATING -------------------------------------------------------
            rating_xpath = '//div[@data-embed="rating"]/div[@itemprop='\
                           '"ratingValue"]/text()'
            rating = response.xpath(rating_xpath).get()
            if rating:
                review['SourceTestRating'] = rating

            scale_xpath = '//div[@data-embed="rating"]/div[@itemprop='\
                          '"bestRating"]/text()'
            scale = response.xpath(scale_xpath).get()
            if scale:
                review['SourceTestScale'] = scale
            # --------------------------------------------------------------

            pros_xpath = '//h2[text()="Pros"]/following::ul[1]/li/text()'
            pros = response.xpath(pros_xpath).getall()
            if pros:
                pros = ";".join(pros)
                review['TestPros'] = pros

            cons_xpath = '//h2[text()="Cons"]/following::ul[1]/li/text()'
            cons = response.xpath(cons_xpath).getall()
            if cons:
                cons = ";".join(cons)
                review['TestCons'] = cons

            review['source_internal_id'] = response.url.split("/")[-3]
            # ===============================================================

            # PRODUCT ITEM ==================================================
            product = ProductItem()
            product['source_internal_id'] = review['source_internal_id']

            # Since the website doesn't put any information about the
            #  category the user is at for some categories (they are not
            #  consistent), we gonna use their URL to extract that information.
            category_dic = {'best-speakers': 'Speaker',
                            'headphone-reviews': 'Headphone',
                            'laptop-reviews': 'Laptop',
                            'dryer-reviews': 'Dryer',
                            'dishwasher-reviews': 'Dishwasher'}

            category = response.url.split('/')[4]

            product['OriginalCategoryName'] = category_dic[category]

            product['ProductName'] = review['ProductName']

            pic_xpath = '//meta[@name="og:image"]/@content'
            pic_url = response.xpath(pic_xpath).get()
            product['PicURL'] = pic_url

            product['TestUrl'] = response.url
            # ===============================================================

            yield review
            yield product
