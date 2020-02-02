
# -*- coding: utf8 -*-

from datetime import datetime
from scrapy.http import Request
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem, ProductIdItem
import json


class The_gadgeteerSpider(AlaSpider):
    name = 'the_gadgeteer'
    allowed_domains = ['the-gadgeteer.com']

    start_urls = ['https://the-gadgeteer.com/category/reviews/']

    def __init__(self, *args, **kwargs):
        super(The_gadgeteerSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

        # In order to test another stored_last_date
        # self.stored_last_date = datetime(2018, 2, 8)

    def parse(self, response):
        # print " 	...PARSE: " + response.url
        # print " --self.stored_last_date: " + str(self.stored_last_date)

        review_articles = response.xpath('//article')

        date = None
        for r_article in review_articles:
            post_type_xpath = './/span[@class="cat-links"]//text()'
            post_type = r_article.xpath(post_type_xpath).get()
            if post_type == 'Reviews':
                date_xpath = './/span[@class="published"]//text()'
                date = r_article.xpath(date_xpath).get()
                # date looks like: November 17, 2018
                date = date.strip()
                date = datetime.strptime(date, '%B %d, %Y')

                if date > self.stored_last_date:
                    author_xpath = './/span[@class="author-name"]//text()'
                    author = r_article.xpath(author_xpath).get()

                    img_xpath = './/img/@src'
                    img = r_article.xpath(img_xpath).get()

                    review_url_xpath = './/h2[@class="entry-title"]/a/@href'
                    review_url = r_article.xpath(review_url_xpath).get()

                    cat_xpath = './/span[@class="tags-links"]/*//text()'
                    cat = r_article.xpath(cat_xpath).getall()
                    cat = ", ".join(cat)
                    yield Request(url=review_url,
                                  callback=self.parse_product_review,
                                  meta={'author': author,
                                        'cat': response.meta.get('cat'),
                                        'date': date.strftime("%Y-%m-%d"),
                                        'img': img,
                                        'cat': cat})

        # Check whether we should scrape the next page.
        if date and date > self.stored_last_date:
            next_page_url_xpath = '//a[@class="next page-numbers"]/@href'
            next_page_url = response.xpath(next_page_url_xpath).get()

            yield Request(url=next_page_url,
                          callback=self.parse)

    def get_product_name_based_on_title(self, title):
        ''' This function will 'clean' the title of the review
            in order to get the product name '''
        p_name = title

        # Spliting title
        get_first_piece = [u' – ']

        for g_f in get_first_piece:
            if g_f in p_name:
                p_name = p_name.split(g_f)[0]

        # Removing certain words
        words_to_remove = ['Review',
                           'review',
                           'smartphone',
                           '(part 1- first impressions)',
                           'smartwatch',
                           'Smartwatch',
                           'dashcam',
                           'Dashcam',
                           'dash cam',
                           'Dash Cam']

        for w in words_to_remove:
            if w in title:
                p_name = p_name.replace(w, '')

        # Removing unnecessary spaces:
        p_name = p_name.replace('  ', ' ')
        p_name = p_name.strip()

        return p_name

    def parse_product_review(self, response):
        # print "     ...PARSE_PRODUCT_REVIEW: " + response.url

        # REVIEW ITEM -----------------------------------------------
        review_xpaths = {
            'TestTitle': '//title//text()'
        }

        # Create the review
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        # 'ProductName'
        js_xpath = '//span[@data-type="in-text"]/@data-config'
        js = response.xpath(js_xpath).get()
        if js:
            js = json.loads(js)
            # js looks like:
            #  {"nameKeywords": "Meridio Vintage Apple Watch Band ",
            #   "price": 104}
            p_name = js['nameKeywords']
            review['ProductName'] = p_name
        else:
            title = review['TestTitle']
            review['ProductName'] = self.get_product_name_based_on_title(title)

        # 'Author'
        review['Author'] = response.meta.get('author')

        # 'TestSummary'
        summary_xpath = '//h2[text()="Final thoughts"]/following::p//text()'
        summary = response.xpath(summary_xpath).get()
        if not summary:
            summary_xpath = 'string(//h2[text()="Final Thoughts"]'\
                            '/following::p)'
            summary = response.xpath(summary_xpath).get()
        if not summary:
            summary_xpath = '//h3[text()="Final thoughts"]'\
                            '/following::p//text()'
            summary = response.xpath(summary_xpath).get()

        if not summary:
            ps_xpath = '//h3[text()="Conclusion"]/following-sibling::p'
            ps = response.xpath(ps_xpath)

            alltext = ''
            for p in ps:
                alltext += p.xpath('string(.)').get()
            summary = alltext
        if not summary:
            summary_xpath = 'string(//p[img]/following::p)'
            summary = response.xpath(summary_xpath).get()
        if not summary:
            summary_xpath = '//div[@class="entry-content clear"]/p[1]'\
                            '/following::p[1]//text()'
            summary = response.xpath(summary_xpath).get()
        if not summary:
            summary_xpath = '//p[a[img]]//text()'
            summary = response.xpath(summary_xpath).get()
        review['TestSummary'] = summary

        # 'TestDateText'
        review['TestDateText'] = response.meta.get('date')

        # 'DBaseCategoryName'
        review['DBaseCategoryName'] = 'PRO'

        # 'TestPros' and 'TestCons'
        pros_xpath = '//h2[text()="What I like"]/following::ul[1]/li//text()'
        pros = response.xpath(pros_xpath).getall()
        if not pros:
            pros_xpath = '//h2/strong[text()="What I like"]'\
                         '/following::ul[1]/li//text()'
            pros = response.xpath(pros_xpath).getall()
        pros = ";".join(pros)

        cons_xpath = '//h2[text()="What needs to be improved"]'\
                     '/following::ul[1]/li//text()'
        cons = response.xpath(cons_xpath).getall()
        if not cons:
            cons_xpath = '//h2/strong[text()="What needs to be improved"]'\
                         '/following::ul[1]/li//text()'
            cons = response.xpath(cons_xpath).getall()
        cons = ";".join(cons)

        review['TestPros'] = pros
        review['TestCons'] = cons

        # 'source_internal_id'
        sid_xpath = '//link[@rel="shortlink"]/@href'
        sid = response.xpath(sid_xpath).get()
        # sid looks like: href="https://the-gadgeteer.com/?p=270265"
        sid = sid.split('?p=')[-1]
        review['source_internal_id'] = sid
        # -----------------------------------------------------------

        # PRODUCT ITEM ----------------------------------------------
        product = ProductItem()
        product['source_internal_id'] = review['source_internal_id']
        if response.meta.get('cat'):
            product['OriginalCategoryName'] = response.meta.get('cat')
        else:
            product['OriginalCategoryName'] = 'Unkown'
        product['ProductName'] = review['ProductName']
        product['PicURL'] = response.meta.get('img')
        product['TestUrl'] = response.url
        # -----------------------------------------------------------

        # PRICE -----------------------------------------------------
        if js:
            price = js["price"] + u'$'
            if price:
                yield ProductIdItem.from_product(product,
                                                 kind='price',
                                                 value=price
                                                 )
        else:
            price_xpath = '//td[text()="Price:"]/following-sibling::td//text()'
            price = response.xpath(price_xpath).get()
            if price:
                get_first_piece = ['/', 'with']
                for w in get_first_piece:
                    if w in price:
                        price = price.split(w)[0]

                words_to_remove = ['for each color', 'w', ':', 'MSRP']
                for w in words_to_remove:
                    if w in price:
                        price = price.replace(w, '')

                price = price.strip()
                yield ProductIdItem.from_product(product,
                                                 kind='price',
                                                 value=price
                                                 )
        # -----------------------------------------------------------

        yield review
        yield product
