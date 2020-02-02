# -*- coding: utf8 -*-

from datetime import datetime
from scrapy import Request

from alascrapy.items import ProductItem, ReviewItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils


class Notebooksbilliger_de_blog(AlaSpider):
    name = 'notebooksbilliger_de_blog'
    allowed_domains = ['blog.notebooksbilliger.de']

    start_urls = ['https://blog.notebooksbilliger.de/category/notebook/',
                  'https://blog.notebooksbilliger.de/category/desktop-pc/',
                  'https://blog.notebooksbilliger.de/category/display/',
                  'https://blog.notebooksbilliger.de/category/smartphone/'
                  ]

    def __init__(self, *args, **kwargs):
        super(Notebooksbilliger_de_blog, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager,
            self.spider_conf["source_id"])

        # testing diff stored_last_date
        # self.stored_last_date = datetime(2017, 1, 1)

    def parse(self, response):
        review_articles_xpath = '//article[not(ancestor::div[@class="main-top'\
                                '-post"]) and not(ancestor::div[@class="aside'\
                                '-top-post"] )]'

        review_articles = response.xpath(review_articles_xpath)

        for article in review_articles:
            # Check whether this article is a proper review
            if self.is_article_a_review(article):
                # Check whether this review is new.
                if self.is_article_new(article):
                    review_url_xpath = './/a/@href'
                    review_url = article.xpath(review_url_xpath).get()

                    # For some reason the individual review pages don't have
                    #  an ID, but they have IDS for articles in thsi page.
                    # Let's save and pass it to parse_product_review()
                    post_id = article.xpath('.//@id').get().split('post-')[1]

                    # The individual review pages don't have the dates in a
                    #  clear way or they are in german. To make it easier, we
                    #  get the date in this page and send it as a meta variable
                    date_xpath = './/li[@class="entry-date"]//a/text()'
                    date = article.xpath(date_xpath).get()
                    date = datetime.strptime(date, '%d.%m.%Y')
                    date = date.strftime("%Y-%m-%d")

                    # The individual review pages sometimes don't have the
                    #   author. It's safer and easier to pass them from this
                    #   page.
                    author_xpath = '//aside[@class="entry-details"]//'\
                                   'li[@class="entry-author"]//a//text()'
                    author = article.xpath(author_xpath).get()

                    # Passing the category from here it's much easier and safer
                    category = response.url.split('category/')[1].split('/')[0]

                    yield Request(url=review_url,
                                  callback=self.parse_product_review,
                                  meta={'review_id': post_id,
                                        'review_date': date,
                                        'author': author,
                                        'category': category})

        # Check whether we should scrape the next page
        if self.is_article_new(review_articles[-1]):
            next_page_url_xpath = '//a[@class="nextpostslink"]/@href'
            next_page_url = response.xpath(next_page_url_xpath).get()

            if next_page_url:
                yield Request(url=next_page_url,
                              callback=self.parse)

    def is_article_a_review(self, article):
        ''' This website puts NEWS, review of maultiple products,
             discounts, and other things in the same style as sole reviews.
            This function is in charge of identifying whether an article
             is a review or not. '''

        categories_xpath = './/span[@class="entry-category"]//a//text()'
        categories = article.xpath(categories_xpath).getall()
        if ('Test' in categories) and \
           ('Vergleichstest' not in categories) and \
           ('Aktion/Gewinnspiel' not in categories):
            return True

        return False

    def is_article_new(self, article):
        ''' In this website, the reviews are wrapped in <article> tags.
            This function returns true in case the article is new. '''

        date_xpath = './/li[@class="entry-date"]//a/text()'
        date = article.xpath(date_xpath).get()
        date = datetime.strptime(date, '%d.%m.%Y')

        if date > self.stored_last_date:
            return True

        return False

    def get_product_name(self, response):
        ''' This is a very tricky site when it comes to get the product name.
            They don't put the product name in a simple easy way. They always
            embedded it inside some text, button, or something else which can
            always change their pattern. This function is the best attempt you
            can find to get the product name. Feel free to improve it. '''

        review_title_xpath = '//h1[@class="entry-title"]//text()'
        review_title = response.xpath(review_title_xpath).get()

        product_name = review_title

        # There are many and many exceptions. For example:
        # PN : some description here
        # Test: PN - some description here
        # PN - some description
        # PN im Test: some description (e.g https://goo.gl/in3rk2)
        # Was kriegt man für xxx Euro? PN im Test (e.g https://goo.gl/b54Tk8)
        # Business First: PN im Test (e.g https://goo.gl/Ga17da)
        # Review: PN – some description (e.g https://goo.gl/c9VCzR)
        # Test: Toshiba Portégé X20W-D-14G im Campus-Programm für 999 €

        words_to_remove_from_beginning = \
            ['Review:',
             'Test:',
             'Business First:',
             'Im Test:',
             'Silvesterknaller:',
             'Genug Power für alle Spiele:',
             'Kleines Kraftpaket:',
             'Klein, kühl, vielseitig:',
             'Klein und schnell:',
             'Ergonomisch, günstig, alltagstauglich:']

        for w in words_to_remove_from_beginning:
            if product_name.startswith(w.decode('utf-8')):
                product_name = product_name.split(w.decode('utf-8'))[1]

        # If "PN : some description here" get "PN "
        product_name = product_name.split(":")[0]

        # If "PN – some description" get "PN ". This is a diff hifen!
        product_name = product_name.split("–".decode('utf-8'))[0]

        # Test: Toshiba Portégé X20W-D-14G im Campus-Programm für 999 €
        product_name = product_name.split('im Campus-Programm')[0]

        # If "Was kriegt man für xxx Euro? PN im Test" get
        #   " PN im Test"
        if "Euro?" in product_name:
            product_name = product_name.split("?")[1]

        if "?" in product_name:
            product_name = product_name.split("?")[0]

        words_to_remove = ['im Test',
                           'Gaming-Notebook',
                           'Test',
                           '[Gewinnspiel]',
                           'Review'
                           ]

        for w in words_to_remove:
            product_name = product_name.replace(w, '')

        # Removing double space
        product_name = product_name.replace('  ', ' ')

        # Removing space at the start and end of string
        product_name = product_name.strip()

        return product_name

    def parse_product_review(self, response):

        # REVIEW -----------------------------------------------------------
        review_xpaths = {
            'TestTitle': '//meta[@property="og:title"][1]//@content',
            'TestSummary': '//meta[@property="og:description"]//@content',
        }

        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        review['ProductName'] = self.get_product_name(response)

        review['source_internal_id'] = response.meta.get('review_id')
        review['TestDateText'] = response.meta.get('review_date')
        review['DBaseCategoryName'] = 'PRO'
        review['Author'] = response.meta.get('author')
        review['TestUrl'] = response.url

        # Some reviews have a rating, such as 88%, others don't have it.
        # If there's a rating, we scrape it, otherwise we set
        # it to none.
        rating_xpath = '//div[@class="rating-widget-percent"]//text()'
        rating = response.xpath(rating_xpath).get()

        if rating:
            rating = rating.split('%')[0]
            review['SourceTestRating'] = rating
            review['SourceTestScale'] = 100
        else:
            review['SourceTestRating'] = None
            review['SourceTestScale'] = None
        # ------------------------------------------------------------------

        # PRODUCT ----------------------------------------------------------
        product = ProductItem()
        product['source_internal_id'] = response.meta.get('review_id')
        product['OriginalCategoryName'] = response.meta.get('category')
        product['ProductName'] = review['ProductName']
        product['PicURL'] = response.xpath('//meta[@property="og:image"][1]'
                                           '//@content').get()
        # product['ProductManufacturer']  # not found
        product['TestUrl'] = response.url
        # ------------------------------------------------------------------

        yield review
        yield product
