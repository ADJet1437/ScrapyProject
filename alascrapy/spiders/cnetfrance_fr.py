# -*- coding: utf8 -*-

from datetime import datetime
from scrapy.http import Request
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem, ProductIdItem
import json


class Cnetfrance_frSpider(AlaSpider):
    name = 'cnetfrance_fr'
    allowed_domains = ['cnetfrance.fr']

    def __init__(self, *args, **kwargs):
        super(Cnetfrance_frSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

        # In order to test another stored_last_date
        # self.stored_last_date = datetime(2018, 2, 8)

    def start_requests(self):
        # print " 	...START_REQUESTS: "

        base_url = 'https://www.cnetfrance.fr/produits/'
        url_cat_dict = {'Smartphones': base_url + 'telephones-mobiles/',
                        'Laptops/Tablets': base_url + 'pc-portables-netbooks/',
                        'Photo/Video': base_url + 'appareils-photo-'
                                                  'numeriques/',
                        'Audio': base_url + 'produits/audio/',
                        'TV': base_url + 'produits/tv-hd/',
                        'PC/Mac': base_url + 'pc-desktops-nettops/',
                        'Printers': base_url + 'imprimantes-multifonctions/'}

        for cat in url_cat_dict:
            yield Request(url=url_cat_dict[cat],
                          callback=self.parse,
                          meta={'cat': cat})

    def parse(self, response):
        # print " 	...PARSE: " + response.url
        # print " --self.stored_last_date: " + str(self.stored_last_date)

        review_divs_xpath = '//div[@class="riverPost reviewPost"]'
        review_divs = response.xpath(review_divs_xpath)

        author_xpath = './/span[@class="editorName"]//text()'
        review_url_xpath = './/figure[@class="img"]//a[@class='\
                           '"storyTitle"]/@href'

        for r_div in review_divs[:-1]:
            # Author -----------------------------------------------
            author = r_div.xpath(author_xpath).get()
            # Looks like "Par L'équipe CNET France"
            remove = ['Par', 'CNET France', u"L'équipe", 'CNET.com',
                      'avec', 'cnet.com']
            for w in remove:
                if w in author:
                    author = author.replace(w, '')
            author = author.strip()
            if author == "":
                author = None

            # Review
            review_url = r_div.xpath(review_url_xpath).get()
            yield response.follow(url=review_url,
                                  callback=self.parse_product_review,
                                  meta={'author': author,
                                        'try_next_page': False,
                                        'cat': response.meta.get('cat')})

        # Author -----------------------------------------------
        author = r_div.xpath(author_xpath).get()
        # Looks like "Par L'équipe CNET France"
        remove = ['Par', 'CNET France', u"L'équipe", 'CNET.com',
                  'avec', 'cnet.com']
        for w in remove:
            if w in author:
                author = author.replace(w, '')
        author = author.strip()
        if author == "":
            author = None

        # Review
        review_url = r_div.xpath(review_url_xpath).get()

        next_page_url_xpath = '//li[@class="next"]/a/@href'
        next_page_url = response.xpath(next_page_url_xpath).get()

        yield response.follow(url=review_url,
                              callback=self.parse_product_review,
                              meta={'author': author,
                                    'try_next_page': True,
                                    'next_page_url': next_page_url,
                                    'cat': response.meta.get('cat')})

    def parse_product_review(self, response):
        # print "...PARSE_PRODUCT_REVIEW: " + response.url

        date_xpath = '//time//@datetime'
        date = response.xpath(date_xpath).get()
        # date looks like: "2012-03-19 à 17:13"
        date = date.split(u'à')[0]
        date = date.strip()
        date = datetime.strptime(date, '%Y-%m-%d')

        if date > self.stored_last_date:
            # REVIEW ITEM ---------------------------------------------------
            review_xpaths = {
                'TestSummary': '//meta[@name="description"]/@content',
            }

            # Create the review
            review = self.init_item_by_xpaths(response,
                                              "review",
                                              review_xpaths)

            # 'TestTitle'
            js_xpath = '//script[@type="text/javascript" and not(@src) '\
                       'and not(@async)]//text()'
            js = response.xpath(js_xpath).get()
            js = js.split('_dataLayer = [')[-1]
            js = js.split('];')[0]
            js = js
            js = js.strip()
            js = json.loads(js)
            review['TestTitle'] = js["pageInfo"]["additional"]

            #  'ProductName'
            js2_xpath = '(//script[@type="application/ld+json"])[3]//text()'
            js2 = response.xpath(js2_xpath).get()
            js2 = json.loads(js2)
            try:
                p_name = js2["name"]
                review['ProductName'] = p_name
            except:
                review['ProductName'] = review['TestTitle']

            # Author
            review['Author'] = response.meta.get('author')

            # 'TestDateText'
            review['TestDateText'] = date.strftime("%Y-%m-%d")

            # 'SourceTestScale' and 'SourceTestRating'
            try:
                review['SourceTestRating'] = js["pageInfo"]["note"]
                if review['SourceTestRating']:
                    review['SourceTestScale'] = 100
            except:
                review['SourceTestRating'] = None
                review['SourceTestScale'] = None

            # 'DBaseCategoryName'
            review['DBaseCategoryName'] = 'PRO'

            # 'source_internal_id'
            sid_xpath = '//div[@class="wtb"]/@data-product-id'
            sid = response.xpath(sid_xpath).get()
            if sid:
                review['source_internal_id'] = sid
            else:
                return
            # ---------------------------------------------------------------

            # PRODUCT ITEM --------------------------------------------------
            product = ProductItem()
            product['source_internal_id'] = review['source_internal_id']
            product['OriginalCategoryName'] = response.meta.get('cat')
            product['ProductName'] = review['ProductName']

            pic_url_xpath = '//meta[@property="og:image"]/@content'
            pic_url = response.xpath(pic_url_xpath).get()
            product['PicURL'] = pic_url

            product['TestUrl'] = response.url
            # ---------------------------------------------------------------

            yield review
            yield product

            # PRICE ITEM ----------------------------------------------------
            cid_xpath = '//input[@name="current_channel_id"]/@value'
            cid = response.xpath(cid_xpath).get()

            # They use an API do get the prices of the products
            price_url = 'https://www.cnetfrance.fr/api/prices.html?'\
                        'pids={}&cid={}'.format(sid, cid)

            yield Request(url=price_url,
                          callback=self.parse_product_review2,
                          meta={'product': product})

            if response.meta.get('try_next_page'):
                yield Request(url=response.meta.get('next_page_url'),
                              callback=self.parse,
                              meta={'cat': response.meta.get('cat')})

    def parse_product_review2(self, response):
        # print "     ...PARSE_PRODUCT_REVIEW2: " + response.url

        product = response.meta.get('product')

        js = json.loads(response.body)

        price = None
        try:
            price = js["prices"][0]["price"] + u' €'
        except:
            pass

        if price:
            price = price.strip()
            yield ProductIdItem.from_product(product,
                                             kind='price',
                                             value=price)
