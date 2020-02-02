# -*- coding: utf8 -*-

from datetime import datetime
import re

from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format
import alascrapy.lib.dao.incremental_scraping as incremental_utils


class EphotozineSpider(AlaSpider):
    name = 'ephotozine'
    allowed_domains = ['ephotozine.com']

    start_urls = ['https://www.ephotozine.com/reviews/digital-cameras-29',
                  'https://www.ephotozine.com/reviews/camera-phones-30']

    def __init__(self, *args, **kwargs):
        super(EphotozineSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

        # In order to test another stored_last_date
        # self.stored_last_date = datetime(2018, 2, 8)

    def parse(self, response):
        # print "...PARSE: " + response.url

        review_divs_xpath = '//div[@class="article-item-featured-image"]'

        review_divs = response.xpath(review_divs_xpath)

        # Sice the categories are not present in the individuals' review page
        #  we have to send it to parse_review() from here. Check the 'meta'
        #  value in the Request() function.
        category = response.xpath('//h1[@class="main-title"]//text()').get()
        if category == "Digital Cameras":
            category = "Cameras"
        elif category == "Camera Phones":
            category = "Phones"

        # Checking the date of the review before scraping it.
        for review_div in review_divs:
            date_xpath = './/time[@class="date"]/@datetime'

            review_date = review_div.xpath(date_xpath).get()
            review_date = datetime.strptime(review_date, "%m/%d/%Y")

            # If the review is new, let's scrape it
            if review_date > self.stored_last_date:
                review_urls_xpath = './/h2/a/@href'

                review_url = review_div.xpath(review_urls_xpath).get()

                yield Request(url=review_url,
                              callback=self.parse_review,
                              meta={'category': category})

        # Checking next page
        if self.continue_to_next_page(response):
            next_page_xpath = '//ul[@class="pagination"]//li/a/@href'
            next_page_url = response.xpath(next_page_xpath).getall()[-2]

            # print "    ... SCRAPE NEXT_PAGE_URL: " + next_page_url
            yield Request(url=next_page_url,
                          callback=self.parse)

    def continue_to_next_page(self, response):
        # In case it's the first time the spider ir running,
        #  we should definetely scrape the next page
        if not self.stored_last_date:
            return True

        review_dates_xpath = '//div[@class="article-item-featured-image"]'\
                             '//time[@class="date"]/@datetime'

        # get the date of the last review
        last_review_date = response.xpath(review_dates_xpath).getall()[-1]
        last_review_date = datetime.strptime(last_review_date, "%m/%d/%Y")
        # print " ...last_review_date: " + str(last_review_date)

        if last_review_date > self.stored_last_date:
            return True

        return False

    def add_verdict(self, response, review):
        # print "...ADD_VERDICT: " + response.url

        verdict_xpath = "(//h2[contains(text(),'Verdict')]//following-sibling"\
                        "::p)[1]//text()"
        award_pic_xpath = "//*[contains(@class,'col-md-4')]//img[contains("\
                          "@src,'AWARD')]/@src"

        test_pros_xpath = "(//div[@class='row']//h3[contains(text(),'Pros')]"\
                          "//following-sibling::p)[1]//text()"
        test_cons_xpath = "(//div[@class='row']//h3[contains(text(),'Cons')]"\
                          "//following-sibling::p)[1]//text()"

        test_pros_alt_xpath = "//div[@class='row']//*[@class='article_pros']/"\
                              "following-sibling::text()[1]"
        test_cons_alt_xpath = "//div[@class='row']//*[@class='article_cons']/"\
                              "following-sibling::text()[1]"

        full_star_css = "#head_specifications .rating .icon-star"
        half_star_css = "#head_specifications .rating .icon-star-half-full"

        review["TestVerdict"] = self.extract_all(response.xpath(verdict_xpath))
        review["AwardPic"] = self.extract(response.xpath(award_pic_xpath))

        review["TestPros"] = self.extract_all(response.xpath(test_pros_xpath),
                                              " ; ")
        if not review["TestPros"] or review["TestPros"] == 'View Full Product'\
                                                           ' Details':
            review["TestPros"] = self.extract_all(response.xpath(
                                                  test_pros_alt_xpath), " ; ")

        review["TestCons"] = self.extract_all(response.xpath(
                                              test_cons_xpath), " ; ")

        if not review["TestCons"] or review["TestCons"] == 'View Full '\
                                                           'Product Details':
            review["TestCons"] = self.extract_all(response.xpath(
                                                  test_cons_alt_xpath), " ; ")

        # There is no rating in the reviews
        '''
        full_rating_stars = response.css(full_star_css)
        half_rating_stars = response.css(half_star_css)

        review["SourceTestRating"] = len(full_rating_stars) +
                                     len(half_rating_stars)*0.5
        if review["SourceTestRating"] == 0:
            review["SourceTestRating"] = ''
        '''

        if review["AwardPic"]:
            if 'highlyrec' in review["AwardPic"]:
                review["award"] = "Highly Recommended"
            elif 'recommended' in review["AwardPic"]:
                review["award"] = "Recommended"
            elif 'edchoice' in review["AwardPic"]:
                review["award"] = "Editor's Choice"
            elif 'bestbuy' in review["AwardPic"]:
                review["award"] = "Best Buy"
            elif 'groupwinner' in review["AwardPic"]:
                review["award"] = "Group Winner"

        review["SourceTestRating"] = None
        review["SourceTestScale"] = None

    def parse_review(self, response):
        # print "...PARSE_REVIEW: " + response.url

        product_xpaths = {"PicURL": "(//*[@property='og:image'])[1]/@content",
                          "ProductManufacturer": "(//*[@class='specs_table']//"
                                                 "td[text()='Manufacturer']/"
                                                 "following-sibling::td)[1]//"
                                                 "text()"
                          }

        review_xpaths = {"TestTitle": "//*[@property='og:title']/@content",
                         "TestSummary": "//*[@property='og:description']/"
                                        "@content",
                         "Author": '//span[@itemprop="author"]/span[@itemprop'
                                   '="name"]/text()',
                         "TestDateText": '//time[@class="date"]/@datetime'
                         }

        date_alt_xpath = "//time[@itemprop='datePublished']/@datetime"
        author_alt_xpath = "//*[@itemprop='author']/text()"
        pname_alt_xpath = "//*[@itemprop='itemReviewed']/text()"

        verdict_page_xpath = "(//ul[@class='review-navigation']/li[" \
                             "@class='section_verdict'])[1]/a/@href"

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        # For internal ID we are using the end of the URL
        internal_source_id = response.url.split('-')[-1]

        product['source_internal_id'] = internal_source_id
        review['source_internal_id'] = internal_source_id

        # The category of the product review is sent by 'meta' from parse()
        product['OriginalCategoryName'] = response.meta.get('category')

        # Getting the product name ----------------------------------------
        product_name_xpath = '//meta[@property="og:title"]/@content'
        product_name = response.xpath(product_name_xpath).get()

        remove_from_product_name = ['Review',
                                    'Preview',
                                    'Hands-On With The New',
                                    'Hands-On'
                                    ]

        for r in remove_from_product_name:
            if r in product_name:
                product_name = product_name.replace(r, '')

        # remove space at the beginning of the string
        product_name = product_name.lstrip()

        # remove space at the end of the string
        product_name = product_name.rstrip()

        # remove double spaces
        product_name = product_name.replace('  ', '')
        # -----------------------------------------------------------------

        product["ProductName"] = product_name
        review["ProductName"] = product_name

        review["SourceTestRating"] = None
        review["SourceTestScale"] = None

        review["DBaseCategoryName"] = "PRO"
        if review["Author"]:
            review["Author"] = re.sub("\s*by\s+", "", review["Author"])
        else:
            review["Author"] = self.extract(response.xpath(author_alt_xpath))

        if not review["TestDateText"]:
            review["TestDateText"] = self.extract(response.xpath(
                                                  date_alt_xpath))

        review["TestDateText"] = date_format(review["TestDateText"],
                                             "%m/%d/%Y")

        verdict_page = response.xpath(verdict_page_xpath)
        if verdict_page:
            verdict_page_url = self.extract(verdict_page)
            verdict_page_url = get_full_url(response.url, verdict_page_url)
            request = Request(verdict_page_url, callback=self.parse_verdict)
            request.meta['review'] = review
            request.meta['product'] = product
            yield request
        else:
            self.add_verdict(response, review)
            yield product
            yield review

    def parse_verdict(self, response):
        # print "...PARSE_VERDICT: " + response.url

        review = response.meta['review']
        product = response.meta['product']
        self.add_verdict(response, review)
        yield product
        yield review
