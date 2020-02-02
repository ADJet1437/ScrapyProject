# -*- coding: utf8 -*-
from datetime import datetime
import dateparser

from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import CategoryItem


class TheVergeSpider(AlaSpider):
    name = 'theverge'
    allowed_domains = ['theverge.com']

    start_urls = ['https://www.theverge.com/phone-review',
                  'https://www.theverge.com/tablet-review',
                  'https://www.theverge.com/laptop-review',
                  'https://www.theverge.com/smartwatch-review',
                  'https://www.theverge.com/headphone-review',
                  'https://www.theverge.com/speaker-review']

    def __init__(self, *args, **kwargs):
        super(TheVergeSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager,
            self.spider_conf["source_id"])

    def parse(self, response):
        # Handling Top Box Reviews --------------------------------------------
        topbox_review_divs_xpath = '//div[@class="c-entry-box--compact'\
            'c-entry-box--compact--review c-entry-box--compact--hero"]'

        topbox_review_divs = response.xpath(topbox_review_divs_xpath)

        for trd in topbox_review_divs:
            review_url_xpath = './/h2/a/@href'
            review_url = trd.xpath(review_url_xpath).get()

            # Since the Topbox reviews don't have an explicit date, we need to
            #   check the date when we go into its page. That's why we call the
            #   'self.parse_review_checkdate' function.
            yield Request(review_url,
                          callback=self.parse_review_checkdate)
        # --------------------------------------------------------------------

        # Handling non 'featured' reviews -------------------------------------
        review_divs_xpath = '//div[@class="c-compact-river__entry "]'
        review_divs = response.xpath(review_divs_xpath)  # list of selectors

        for rd in review_divs:
            date = rd.xpath('.//time/@datetime').get()

            # If date is None, it's very likely that it's what they call
            #   "featured review". We handle those cases in the next for loop
            if date:
                date = self.str_to_datetime(date)

                # If the review is older than the last stored date, skipt it,
                #   we already scraped it.
                if date > self.stored_last_date:
                    review_url = rd.xpath('.//h2[@class="c-entry-box--'
                                          'compact__title"]/a/@href').get()

                    yield Request(review_url,
                                  callback=self.parse_review)

            # In case date is None, let's go to its review page to check
            #   whether it's a new review or not
            else:
                review_url = rd.xpath('.//h2[@class="c-entry-box--'
                                      'compact__title"]/a/@href').get()

                yield Request(review_url,
                              callback=self.parse_review_checkdate)
        # ---------------------------------------------------------------------

        # Handling 'featured' reviews -----------------------------------------
        featuerd_review_divs_xpath = '//div[@class="c-compact-river__entry'\
                                     'c-compact-river__entry--featured"]'
        # list of selectors
        featured_review_divs = response.xpath(review_divs_xpath)

        for frd in featured_review_divs:
            date = frd.xpath('.//time/@datetime').get()

            # There are some reviews calls which do not have a photo nor a
            #   date. It looks like an add. For example, the "Samsung Galaxy
            #   Watch review by stefan etienne" at this page:
            #   https://www.theverge.com/smartwatch-review
            if date:
                date = self.str_to_datetime(date)

                # If the review is older than the last stored date, skipt it,
                #   we already scraped it.
                if date > self.stored_last_date:
                    review_url = frd.xpath('.//h2[@class="c-entry-box--'
                                           'compact__title"]/a/@href').get()

                    yield Request(review_url,
                                  callback=self.parse_review)

            # In case date is None, let's go to its review page to check
            #   whether it's a new review or not
            else:
                review_url = rd.xpath('.//h2[@class="c-entry-box--'
                                      'compact__title"]/a/@href').get()

                yield Request(review_url,
                              callback=self.parse_review_checkdate)
        # -------------------------------------------------------------------------

        # Checking whether we should go to the next page.
        # There are two possibilities for that:
        #  1- The page has a "more stories" button - '.../phone-review' pages
        #  2- The page has a "next" button - '.../phone-review/archive' pages
        more_stories_button_xpath = '//a[@class="c-pagination__more'\
                                    ' c-pagination__link p-button"]/@href'

        next_button_xpath = '//div[@class="c-pagination__wrap"]/a[@class="c-'\
                            'pagination__next c-pagination__link p-button"]/'\
                            '@href'

        more_stories_url = response.xpath(more_stories_button_xpath).get()

        next_page_url = response.xpath(next_button_xpath).get()

        if more_stories_url and self.continue_to_next_page(response):
            yield Request(more_stories_url, callback=self.parse)

        elif next_page_url and self.continue_to_next_page(response):
            yield Request(next_page_url, callback=self.parse)
        # -------------------------------------------------------------------------

    def continue_to_next_page(self, response):
        # In case it's the first time the spider is running
        if not self.stored_last_date:
            return True

        # Get the date of the last review in the list. That should be the
        #   oldest one.
        last_review_date = response.xpath("//time/@datetime")[-1].get()

        # Convert to datetime format so we can compare with the
        #   stored_last_date last_review_date = datetime.strptime
        #   last_review_date, '%Y-%m-%dT%H:%M:%S+00:00')
        last_review_date = self.str_to_datetime(last_review_date)

        if last_review_date < self.stored_last_date:
            return False

        return True

    def str_to_datetime(self, s):
        # Some of the date in the website are not in the same format.
        # In this function we convert the possible date formats we have
        # identified in the website so far.
        try:
            return datetime.strptime(s, '%Y-%m-%dT%H:%M:%S')
        except:
            try:
                return datetime.strptime(s, '%Y-%m-%d %H:%M:%S-%f')
            except:
                return None

    def _parse_product(self, response):
        category_xpath = "//ul[@class='p-entry-header__labels']/li[1]//text()"
        category_url_xpath = "//ul[@class='p-entry-header__labels']"\
            "/li[1]/a/@href"
        category = CategoryItem()

        # backup for category
        category_group = "//div[contains(@class, 'c-entry-group-labels')]"\
                         "//li/a"
        cat_xpath = category_group + "/span/text()"
        cat_url_xpath_backup = category_group + "/span/text()"

        cat_leaf_text = self.extract(response.xpath(category_xpath))
        if not cat_leaf_text:
            cats_text = self.extract_list(response.xpath(cat_xpath))
            cats_text = ' | '.join(set(cats_text))
            cat_leaf_text = cats_text.replace('Reviews', '').strip()

        category["category_leaf"] = cat_leaf_text
        category["category_path"] = category["category_leaf"]

        cat_url = get_full_url(response, self.extract(
            response.xpath(category_url_xpath)))
        if not cat_url:
            cat_url = get_full_url(response, self.extract(
                response.xpath(cat_url_xpath_backup)))
        category["category_url"] = cat_url
        yield category

        manufacturer_xpath = "//ul[@class='p-entry-header__labels']"\
            "/li[last()]//text()"
        product = response.meta['product']
        product["OriginalCategoryName"] = category['category_path']
        product['ProductManufacturer'] = self.extract(
            response.xpath(manufacturer_xpath))
        yield product

    def get_product_name(self, url):
        # a typical example of a review url
        # https://www.theverge.com/2017/7/18/15988172/oneplus-travel-backpack-bag-review'
        product_name = url.split('/')[-1]
        product_name = ' '.join(product_name.split('-')[:-1])
        return product_name

    # Some reviews don't have an explicit date beforehand. This function
    #  is called by those reviews. In case the review is new, then we call
    #  the regular 'parse_review()' function.
    def parse_review_checkdate(self, response):
        date_xpath = '//time/@datetime'
        date = response.xpath(date_xpath).get()

        if date:
            date = self.str_to_datetime(date)

            # If the review is older than the last stored date, skipt it, we
            #   already scraped it.
            if date > self.stored_last_date:
                self.parse_review(response)
        # else:
        #    print "---------- PROBLEM SCRAPING THIS REVIEW! "
        #    print response

    def parse_review(self, response):
        product_xpaths = {"PicURL": "//*[@property='og:image']/@content",
                          "ProductName": "//*[@class='c-scorecard__title']"
                          "/a/text()"
                          }

        review_xpaths = {"TestTitle": "//*[@property='og:title']/@content",
                         "TestSummary": "//*[@property='og:description']/"
                         "@content",

                         "Author": "//meta[@property='author']/@content",
                         "TestVerdict": "string(//p[@class='c-end-para'])",

                         "SourceTestRating": "//span[@itemprop='ratingValue']"
                         "/text() | //*[@class='c-scorecard__score-number']"
                         "/text()",

                         "TestDateText": "//*[contains(@name,'sailthru.date')]"
                         "/@content",

                         "TestPros": "(//*[contains(@class, 'c-scorecard__"
                         "additional-info')]/ul)[1]/li/text() |"
                         "//h6[contains(text(), 'Good')]/following-sibling::ul"
                         "/li/text()",

                         "TestCons": "(//*[contains(@class, 'c-scorecard__"
                         "additional-info')]/ul)[2]/li/text() |"
                         "//h6[contains(text(), 'Bad')]/following-sibling::ul"
                         "/li/text()",
                         }

        splitted = response.url.rstrip('/').split('/')
        source_internal_id = splitted[-2]

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['source_internal_id'] = source_internal_id

        if not product.get('ProductName', ''):
            product['ProductName'] = self.get_product_name(response.url)

        product_url_xpath = "//div[@class='meta']/h3/a/@href"
        product_page_url = self.extract(response.xpath(product_url_xpath))
        if product_page_url:
            product_page_url = get_full_url(response, product_page_url)
            request = Request(product_page_url,
                              callback=self._parse_product)
            request.meta['product'] = product
            yield request
        else:
            category_xpath = "//meta[@name='outbrainsection']/@content"
            category = CategoryItem()
            category["category_leaf"] = self.extract(
                response.xpath(category_xpath))
            category["category_path"] = category["category_leaf"]
            category["category_url"] = get_full_url("https://www.theverge.com",
                                                    category["category_leaf"])
            yield category

            product["OriginalCategoryName"] = category['category_path']
            yield product

        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        review["ProductName"] = product["ProductName"]
        review["DBaseCategoryName"] = "PRO"

        # rating
        # --------------------
        rating = review.get('SourceTestRating', '')
        # the most digit for rating will be 3, i.e. 8.5
        # the goal is to filter out review for multiple product compare
        # in one page
        if not rating:
            return
        elif len(rating) > 3:   # multiple products in one page
            return
        else:
            review['SourceTestScale'] = '10'

        review['source_internal_id'] = source_internal_id

        if not review['TestVerdict']:
            alt_verdict_xpath = "//*[contains(@class, 'c-entry-summary')]"\
                "//text()"
            review_verdict = self.extract(response.xpath(alt_verdict_xpath))
            if review_verdict.lower() != review['TestSummary'].lower():
                review['TestVerdict'] = review_verdict

        yield review
