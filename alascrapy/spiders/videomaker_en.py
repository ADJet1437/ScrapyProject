# -*- coding: utf8 -*-

from datetime import datetime
from scrapy.http import Request
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem, ProductIdItem


class Videomaker_enSpider(AlaSpider):
    name = 'videomaker_en'
    allowed_domains = ['videomaker.com']
    page_number = 1
    start_urls = ['https://www.videomaker.com/category/reviews/']

    def __init__(self, *args, **kwargs):
        super(Videomaker_enSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

        # In order to test another stored_last_date
        # self.stored_last_date = datetime(2018, 2, 8)

    def parse(self, response):
        # print " 	...PARSE: " + response.url
        # print " --self.stored_last_date: " + str(self.stored_last_date)

        review_divs_xpath = '//div[@class="td_module_19 td_module_wrap '\
                            'td-animation-stack td-meta-info-hide"]'
        review_divs = response.xpath(review_divs_xpath)

        review_url_xpath = './/div[@class="td-module-thumb"]/a/@href'
        for r_div in review_divs[:-1]:
            review_url = r_div.xpath(review_url_xpath).get()

            yield Request(url=review_url,
                          callback=self.parse_product_review,
                          meta={'next_page_url': None})

        # Last review of the page
        review_url = review_divs[-1].xpath(review_url_xpath).get()
        self.page_number += 1
        next_page_url = 'https://www.videomaker.com/category/'\
                        'reviews/page/{}/'.format(self.page_number)
        yield Request(url=review_url,
                      callback=self.parse_product_review,
                      meta={'next_page_url': next_page_url})

    def get_product_name_based_on_title(self, title):
        ''' This function will 'clean' the title of the review
            in order to get the product name '''
        p_name = title

        # Title begins with unnecessary sentence
        discart_beggings = ['Review: ']

        for s in discart_beggings:
            if p_name.startswith(s):
                p_name = p_name.replace(s, '')

        # Spliting title
        get_first_piece = [u' - ', u'review:', u'- Hands On Review -',
                           'Review:']

        for g_f in get_first_piece:
            if g_f in p_name:
                p_name = p_name.split(g_f)[0]

        # Removing certain words
        words_to_remove = ['- Hands-on Review']
        for w in words_to_remove:
            if w in title:
                p_name = p_name.replace(w, '')

        # Removing unnecessary spaces:
        p_name = p_name.replace('  ', ' ')
        p_name = p_name.strip()

        return p_name

    def parse_product_review(self, response):
        # print "     ...PARSE_PRODUCT_REVIEW: " + response.url

        date_xpath = '//time[@class="entry-date updated '\
                     'td-module-date"]/@datetime'
        date = response.xpath(date_xpath).get()
        # date looks like: "2019-04-01T11:00:00+00:00"
        date = date.split('T')[0]
        date = datetime.strptime(date, '%Y-%m-%d')

        if date > self.stored_last_date:
            # REVIEW ITEM ---------------------------------------------------
            review_xpaths = {
                'TestTitle': '//meta[@property="og:title"]/@content',
                'Author': '//div[@class="td-post-author-name"]/a//text()',
                'TestSummary': '//meta[@name="description"]/@content',
            }

            # Create the review
            review = self.init_item_by_xpaths(response,
                                              "review",
                                              review_xpaths)

            # 'TestTitle'
            if ' - Videomaker' in review['TestTitle']:
                review['TestTitle'] = review['TestTitle']\
                    .replace(' - Videomaker', '')

            # 'ProductName'
            title = review['TestTitle']
            review['ProductName'] = self.get_product_name_based_on_title(title)

            # 'TestDateText'
            review['TestDateText'] = date.strftime("%Y-%m-%d")

            # 'DBaseCategoryName'
            review['DBaseCategoryName'] = 'PRO'

            # 'TestPros' and 'TestCons'
            pros_xpath = '//p[b[text()="STRENGTHS:"]]/following-sibling::'\
                         'ul[1]/li//text()'
            pros = response.xpath(pros_xpath).getall()
            if not pros:
                pros_xpath = '//p[strong[text()="STRENGTHS:"]]/following-'\
                             'sibling::ul[1]/li//text()'
                pros = response.xpath(pros_xpath).getall()

            cons_xpath = '//p[b[text()="WEAKNESSES:"]]/following-sibling::'\
                         'ul[1]/li//text()'
            cons = response.xpath(cons_xpath).getall()
            if not cons:
                cons_xpath = '//p[strong[text()="WEAKNESSES:"]]/following-'\
                             'sibling::ul[1]/li//text()'
                cons = response.xpath(cons_xpath).getall()

            if pros:
                pros = ";".join(pros)
                review['TestPros'] = pros
            if cons:
                cons = ";".join(cons)
                review['TestCons'] = cons

            # 'source_internal_id'
            sid_xpath = '//link[@rel="shortlink"]/@href'
            sid = response.xpath(sid_xpath).get()
            # sid looks like: "https://wp.me/pa6U6j-4S8jW"
            sid = sid.split('pa6U6j-')[-1]
            review['source_internal_id'] = sid
            # ---------------------------------------------------------------

            # PRODUCT ITEM --------------------------------------------------
            product = ProductItem()
            product['source_internal_id'] = review['source_internal_id']

            category_xpath = '//div[@class="entry-crumbs"]/'\
                             'span[last()]//text()'
            category = response.xpath(category_xpath).get()
            product['OriginalCategoryName'] = category

            product['ProductName'] = review['ProductName']

            pic_url_xpath = '//meta[@property="og:image"]/@content'
            pic_url = response.xpath(pic_url_xpath).get()
            product['PicURL'] = pic_url

            product['TestUrl'] = response.url
            # ---------------------------------------------------------------

            # PRICE ---------------------------------------------------------
            price_xpath = '//b[text()="PRICE: "]/following-sibling::'\
                          'span//text()'
            price = response.xpath(price_xpath).get()
            if price:
                    price = price.strip()
                    yield ProductIdItem.from_product(product,
                                                     kind='price',
                                                     value=price
                                                     )
            # ---------------------------------------------------------------

            yield review
            yield product

            # Scraping the next page in case the last review of the page is new
            if response.meta.get('next_page_url'):
                yield Request(url=response.meta.get('next_page_url'),
                              callback=self.parse)
