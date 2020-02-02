# -*- coding: utf8 -*-

import dateparser
from datetime import datetime
from scrapy.http import Request
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem


class Thg_ruSpider(AlaSpider):
    name = 'thg_ru'
    allowed_domains = ['thg.ru']

    def __init__(self, *args, **kwargs):
        super(Thg_ruSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

    def start_requests(self):
        # print " 	...START_REQUESTS: "
        # print " --self.stored_last_date: " + str(self.stored_last_date)

        base_url = 'http://www.thg.ru'
        url_cat_dict = {'laptops and tablets': base_url + '/mobile/index.html',
                        'projectors and monitors': base_url +
                        '/display/index.html',
                        'audio and video': base_url + '/video/index.html',
                        'Smartphone': base_url + '/phone/index.html',
                        'Desktop': base_url + '/desktop/index.html'
                        }

        for cat in url_cat_dict:
            yield Request(url=url_cat_dict[cat],
                          callback=self.parse,
                          meta={'cat': cat})

    def parse(self, response):
        # print " 	...PARSE: " + response.url
        # print " --self.stored_last_date: " + str(self.stored_last_date)

        review_ps_xpath = '//p[@align="justify"]'
        review_ps = response.xpath(review_ps_xpath)

        for p in review_ps:
            date_xpath = './font[1]//text()'
            date = p.xpath(date_xpath).get()
            date = date.strip()
            # date looks like: 23 июня 2017
            date = dateparser.parse(date,
                                    date_formats=['%d %B %Y'],
                                    languages=['ru', 'es'])

            if date > self.stored_last_date:
                url = p.xpath('.//a/@href').get()
                yield response.follow(url=url,
                                      callback=self.parse_product_review,
                                      meta={'date': date.strftime("%Y-%m-%d"),
                                            'cat': response.meta.get('cat')})

    def get_product_name_based_on_title(self, title):
        ''' This function will 'clean' the title of the review
            in order to get the product name '''
        p_name = title

        # Spliting title
        get_first_piece = [u'|']

        for g_f in get_first_piece:
            if g_f in p_name:
                p_name = p_name.split(g_f)[0]

        # Removing unnecessary spaces:
        p_name = p_name.replace('  ', ' ')
        p_name = p_name.strip()

        return p_name

    def parse_product_review(self, response):
        # print "     ...PARSE_PRODUCT_REVIEW: " + response.url

        # If the review has more than one page, let's go to the last one.
        last_page_xpath = '//div/span[@style="font-size: 12px;"]'\
                          '/a[ not(descendant::img)][last()]/@href'
        last_page_url = response.xpath(last_page_xpath).get()

        sending_to_last_page = False
        if last_page_url:
            sending_to_last_page = True
            yield response.follow(url=last_page_url,
                                  callback=self.parse_product_review,
                                  meta={'date': response.meta.get('date'),
                                        'cat': response.meta.get('cat'),
                                        'last_page': True})
        else:
            last_page_xpath = '//div[@style="align: justify;width:400px;"]'\
                              '/span/span[last()]/a/@href'
            last_page_url = response.xpath(last_page_xpath).get()
            if last_page_url:
                sending_to_last_page = True
                yield response.follow(url=last_page_url,
                                      callback=self.parse_product_review,
                                      meta={'date': response.meta.get('date'),
                                            'cat': response.meta.get('cat'),
                                            'last_page': True})

        if sending_to_last_page:
            return

        # This website mixed reviews with news and other types of post.
        # This is our attempt to clean this up before yielding the reviews
        words_to_drop = [u'Лучшие смартфоны',
                         u'лучших альтернатив',
                         u'Лучшие мониторы',
                         u'проектора',
                         u'Лучшие наушники']

        title = response.xpath('//h2[@class="h2_artname2"]//text()').get()
        for word in words_to_drop:
            if word in title:
                return
        # -----------------------------------------------------------------

        # Getting category ------------------------------------------------
        cat = response.meta.get('cat')

        if cat == 'laptops and tablets':
            if u'планшет' in title:
                cat = "Tablet"
            else:
                cat = "Laptop"

        elif cat == 'projectors and monitors':
            cat = 'Monitor'

        elif cat == 'audio and video':
            if u'гарнитуры' in title:
                cat = "Headphone"
            else:
                return
        # -----------------------------------------------------------------

        # REVIEW ITEM -----------------------------------------------------
        review_xpaths = {
            'TestTitle': '//h2[@class="h2_artname2"]//text()',
            'Author': '(//div[@class="art_editors"])[1]//'
                      'a[@class="editors_link"]//text()',
            'TestSummary': '//meta[@name="description"]/@content',
        }

        # Create the review
        review = self.init_item_by_xpaths(response,
                                          "review",
                                          review_xpaths)
        # Author
        if 'THG' in review['Author']:
            review['Author'] = review['Author'].replace('THG', '')
            review['Author'] = review['Author'].strip()

        # 'ProductName'
        title = response.xpath('//title[1]//text()').get()
        # Title looks like: Smartisan U3 Pro | обзор и тест | THG.RU
        p_name = self.get_product_name_based_on_title(title)
        review['ProductName'] = p_name

        # 'TestDateText'
        review['TestDateText'] = response.meta.get('date')

        # 'DBaseCategoryName'
        review['DBaseCategoryName'] = 'PRO'

        # 'TestPros' 'TestCons'
        pros_xpath = u'//h3[text()="Преимущества:"]/following-sibling::'\
                     'ul[1]/li//text()'
        pros = response.xpath(pros_xpath).getall()
        if pros:
            pros = ";".join(pros)
            review['TestPros'] = pros

        cons_xpath = u'//h3[text()="Недостатки:"]/following-sibling::'\
                     'ul[1]/li//text()'
        cons = response.xpath(cons_xpath).getall()
        if cons:
            cons = ";".join(cons)
            review['TestCons'] = cons

        # 'source_internal_id'
        sid = response.url.split('/')[-1]
        if sid == "index.html":
            sid = response.url.split('/')[-2]

        if '.html' in sid:
            sid = sid.replace('.html', '')
        review['source_internal_id'] = sid
        # -----------------------------------------------------------------

        # PRODUCT ITEM ----------------------------------------------------
        product = ProductItem()
        product['source_internal_id'] = review['source_internal_id']
        product['OriginalCategoryName'] = cat
        product['ProductName'] = review['ProductName']

        pic_url_xpath = '//meta[@property="og:image"]/@content'
        pic_url = response.xpath(pic_url_xpath).get()
        product['PicURL'] = pic_url

        product['TestUrl'] = response.url
        # -----------------------------------------------------------------

        yield review
        yield product
