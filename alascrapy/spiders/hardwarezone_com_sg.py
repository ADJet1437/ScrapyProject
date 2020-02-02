# -*- coding: utf8 -*-

from datetime import datetime
import json
from scrapy.http import Request
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem


class Hardwarezone_com_sgSpider(AlaSpider):
    name = 'hardwarezone_com_sg'
    allowed_domains = ['hardwarezone.com.sg']

    start_urls = ['https://www.hardwarezone.com.sg/product-guide/all/reviews']

    def __init__(self, *args, **kwargs):
        super(Hardwarezone_com_sgSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

        # In order to test another stored_last_date
        # self.stored_last_date = datetime(2018, 2, 8)

    def parse(self, response):
        # print "     ...PARSE: " + response.url
        # print "     --self.stored_last_date: " + str(self.stored_last_date)

        post_divs_xpath = '//div[@id="article-highlights"]/div'
        post_divs = response.xpath(post_divs_xpath)

        date = None
        for p in post_divs:
            post_type_xpath = './/div[@class="cat-info"]/a//text()'
            post_type = p.xpath(post_type_xpath).get()

            # Check whether the post is a review
            if post_type and (post_type == 'Review'):
                date_xpath = './/div[@class="article-timestamp"]//'\
                             'div[@class="article-time-user-text"]//'\
                             'span//text()'
                date = p.xpath(date_xpath).get()
                # Date looks like this: 03 Apr 2019

                date = datetime.strptime(date, '%d %b %Y')
                if date > self.stored_last_date:
                    sid = p.xpath('./@id').get()
                    sid = sid.replace('article_', '')

                    review_url_xpath = './div[@class="thumb"]/a/@href'
                    review_url = p.xpath(review_url_xpath).get()

                    yield Request(url=review_url,
                                  callback=self.parse_product_review,
                                  meta={'sid': sid,
                                        'date': date.strftime("%Y-%m-%d")})

        # Checking whether we should scrape the next page
        # date already has the date of the last review of the page
        if not date or (date and (date > self.stored_last_date)):
            next_pg_url_xpath = '//a[@class="next-page pagination-btn"]/@href'
            next_pg_url = response.xpath(next_pg_url_xpath).get()

            if next_pg_url:
                yield response.follow(url=next_pg_url,
                                      callback=self.parse)

    def parse_product_review(self, response):
        # print "     ...PARSE_PRODUCT_REVIEW: " + response.url

        # Checking what's the product category in order to exclude
        # items that are not interesting for us
        html = response.body
        html = " ".join(html.split())
        js_starts = '<script type="text/javascript"> //<![CDATA[ var '\
                    '_hwz_scarabqueue = '
        js_ends = '''; //]]> </script>'''
        js_c = html.split(js_starts)[1]
        js_c = js_c.split(js_ends)[0]

        js_c = json.loads(js_c)
        category = js_c["content_category"]

        if category == 'AV Peripherals and Systems':
            title_xpath = '//meta[@name="title"]/@content'
            title = response.xpath(title_xpath).get()
            title = title.lower()

            key_words = ['headphones', 'earphones', 'earbuds']
            for w in key_words:
                if w in title:
                    category = "Headphones"
                    break

        elif category == 'Wearables':
            title_xpath = '//meta[@name="title"]/@content'
            title = response.xpath(title_xpath).get()
            title = title.lower()

            key_words = ['smartwatch', 'watch', 'fitbit']
            for w in key_words:
                if w in title:
                    category = "Smartwatch"
                    break

        categories_to_scrape = ['Notebooks',
                                'Mobile Phones',
                                'Tablets',
                                'Digital Cameras',
                                'Televisions',
                                'Desktop Systems',
                                'Headphones',
                                'Smartwatch'
                                ]

        if category in categories_to_scrape:
            # REVIEW ITEM -------------------------------------------------
            review_xpaths = {
                'TestTitle': '//meta[@name="title"]/@content',
                'TestSummary': '//meta[@name="description"]/@content',
            }

            # Create the review
            review = self.init_item_by_xpaths(response, "review",
                                              review_xpaths)

            # 'ProductName'
            js_xpath = '//script[@type="application/ld+json"]//text()'
            js = response.xpath(js_xpath).get()
            js = json.loads(js)

            p_name = js["itemReviewed"]["name"]
            review['ProductName'] = p_name

            # 'Author'
            review['Author'] = js["author"][0]["name"]

            # 'TestDateText'
            review['TestDateText'] = response.meta.get('date')

            # 'SourceTestScale' 'SourceTestRating'
            try:
                rating = js["reviewRating"]["ratingValue"]
            except:
                pass
            else:
                review['SourceTestRating'] = rating
                review['SourceTestScale'] = 10

            # 'DBaseCategoryName'
            review['DBaseCategoryName'] = 'PRO'

            # 'TestPros' TestCons'
            pros_xpath = '//div[@class="good"]/div[@class="detail"]//text()'
            pros = response.xpath(pros_xpath).getall()
            if pros:
                pros = ";".join(pros)
                pros = pros.replace('\r', '')
                review['TestPros'] = pros

            cons_xpath = '//div[@class="bad"]/div[@class="detail"]//text()'
            cons = response.xpath(cons_xpath).getall()
            if cons:
                cons = ";".join(cons)
                cons = cons.replace('\r', '')
                review['TestCons'] = cons

            # 'source_internal_id'
            review['source_internal_id'] = response.meta.get('sid')
            # ----------------------------------------------------------------

            # PRODUCT ITEM ---------------------------------------------------
            product = ProductItem()
            product['source_internal_id'] = review['source_internal_id']
            product['OriginalCategoryName'] = category
            product['ProductName'] = review['ProductName']

            pic_url_xpath = '//meta[@property="og:image"]/@content'
            pic_url = response.xpath(pic_url_xpath).get()
            product['PicURL'] = pic_url

            product['TestUrl'] = response.url
            # ----------------------------------------------------------------

            yield review
            yield product
