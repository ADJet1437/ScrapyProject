# -*- coding: utf8 -*-

from datetime import datetime
from scrapy.http import Request
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem, ProductIdItem


class Androidpit_deSpider(AlaSpider):
    name = 'androidpit_de'
    allowed_domains = ['androidpit.de']

    def __init__(self, *args, **kwargs):
        super(Androidpit_deSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

        # In order to test another stored_last_date
        # self.stored_last_date = datetime(2000, 2, 8)

    def start_requests(self):
        # print " 	...START_REQUESTS: "

        base_url = 'https://www.androidpit.de'
        url_cat_dict = {'Smartphone': base_url + '/smartphone-tests',
                        'Smartwatch': base_url + '/smartwatch-tests',
                        'Tablet': base_url + '/tablet-tests',
                        'Headphone': base_url + '/kopfhoerer-tests',
                        'Notebook': base_url + '/notebook-tests',
                        'Wearable': base_url + '/wearable-tests',
                        'Fitness Tracker': base_url + '/fitness-tracker-tests',
                        }

        for cat in url_cat_dict:
            yield Request(url=url_cat_dict[cat],
                          callback=self.parse,
                          meta={'cat': cat})

    def parse(self, response):
        # print " 	...PARSE: " + response.url
        # print " --self.stored_last_date: " + str(self.stored_last_date)

        review_articles_xpath = '//section[@class="mainContent"]/article'
        review_articles = response.xpath(review_articles_xpath)

        date = None
        for r_art in review_articles:
            date_xpath = './/span[@class="articleTeaserTimestamp"]/@title'
            date = r_art.xpath(date_xpath).get()
            # date looks like: 30.10.2016, 16:00:01
            date = date.split(',')[0]
            date = datetime.strptime(date, '%d.%m.%Y')

            if date > self.stored_last_date:
                review_url_xpath = './a/@href'
                review_url = r_art.xpath(review_url_xpath).get()

                yield response.follow(url=review_url,
                                      callback=self.parse_product_review,
                                      meta={'cat': response.meta.get('cat'),
                                            'date': date.strftime("%Y-%m-%d")})

        # Check whether we should scrape next page
        if date and date > self.stored_last_date:
            next_page_url_xpath = u'(//a[@class="arrow"])[text()="»"]/@href'
            next_page_url = response.xpath(next_page_url_xpath).get()

            if next_page_url:
                yield response.follow(url=next_page_url,
                                      callback=self.parse,
                                      meta={'cat': response.meta.get('cat')})

    def get_product_name_based_on_title(self, title):
        ''' This function will 'clean' the title of the review
            in order to get the product name '''
        p_name = title

        # Spliting title
        get_first_piece = [u'im Test:', u':']

        for g_f in get_first_piece:
            if g_f in p_name:
                p_name = p_name.split(g_f)[0]

        # Removing unnecessary spaces:
        p_name = p_name.replace('  ', ' ')
        p_name = p_name.strip()

        return p_name

    def parse_product_review(self, response):
        # print "     ...PARSE_PRODUCT_REVIEW: " + response.url

        # REVIEW ITEM ---------------------------------------------------------
        review_xpaths = {
            'TestTitle': '//meta[@property="og:title"]/@content',
            'Author': '//span[@class="articleAuthorLinkText"]//text()',
            'TestSummary': '//meta[@property="og:description"]/@content',
        }

        # Create the review
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        # 'TestTitle'
        if u'| AndroidPIT' in review['TestTitle']:
            review['TestTitle'] = review['TestTitle'].\
                replace(u'| AndroidPIT', '')

        # 'Author'
        if 'vor' in review['Author']:
            review['Author'] = review['Author'].split('vor')[0]
            review['Author'] = review['Author'].strip()

        # 'ProductName'
        title = review['TestTitle']
        review['ProductName'] = self.get_product_name_based_on_title(title)

        # 'TestDateText'
        review['TestDateText'] = response.meta.get('date')

        # 'DBaseCategoryName'
        review['DBaseCategoryName'] = 'PRO'

        # 'source_internal_id'
        sid = response.url.split('/')[-1]
        review['source_internal_id'] = sid
        # ---------------------------------------------------------------------

        # PRODUCT ITEM --------------------------------------------------------
        product = ProductItem()
        product['source_internal_id'] = review['source_internal_id']
        product['OriginalCategoryName'] = response.meta.get('cat')
        product['ProductName'] = review['ProductName']

        pic_url_xpath = '//meta[@property="og:image"]/@content'
        pic_url = response.xpath(pic_url_xpath).get()
        product['PicURL'] = pic_url

        product['TestUrl'] = response.url
        # ---------------------------------------------------------------------

        # PRICE ITEM ----------------------------------------------------------
        price_xpath = '(//div[@class="offerTable otRedesign otVariant2"]//'\
                      'span[@class="otProductPriceProduct affiliateOfferPrice'\
                      '"])[1]/*/text()'

        price = response.xpath(price_xpath).getall()
        price = ''.join(price)

        if price:
                if u'€' in price:
                    price = price.replace(u'€', u' €')
                price = price.strip()
                yield ProductIdItem.from_product(product,
                                                 kind='price',
                                                 value=price
                                                 )
        # ---------------------------------------------------------------------

        yield review
        yield product
