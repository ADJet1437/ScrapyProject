# -*- coding: utf8 -*-

from datetime import datetime
import dateparser
import re

from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.lib import extruct_helper
from alascrapy.items import CategoryItem


class WiredComSpider(AlaSpider):
    name = 'wired_com'
    allowed_domains = ['wired.com']
    start_urls = ['https://www.wired.com/category/gear/']

    def __init__(self, *args, **kwargs):
        super(WiredComSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):
        all_categories_xpath = "//a[contains(@class, 'product-reviews-component__item')]/@href"
        all_categories_urls = self.extract_list(
                                response.xpath(all_categories_xpath)
                                )
        for category_url in all_categories_urls:
            yield response.follow(url=category_url,
                                  callback=self.parse_first_page
                                  )

    def parse_first_page(self, response):
        """
            make request to parse review for the first page of a category,
            find the 'load more' link to get a complete review lists,
            which contains the latest update date for each review listed.
        """
        # make request to parse review in the first page of a category
        review_url_xpath = "//li[contains(@class, 'card-component__description')]/a[1]/@ href"
        review_urls = self.extract_list(response.xpath(review_url_xpath))
        for review_url in review_urls:
            yield response.follow(url=review_url, callback=self.parse_review)

        # link to the load more click.
        more_results_xpath = "//a[@class='more-results__link']/@href"
        next_page_url = self.extract(response.xpath(more_results_xpath))
        if next_page_url:
            yield response.follow(url=next_page_url,
                                  callback=self.parse_category
                                  )

    def parse_category(self, response):
        latest_review_date_xpath = "//div[@class = 'archive-listing-component']//li//time/text()"
        next_page_xpath = "//li[contains(@class, 'caret--right')]/a/@href"
        review_url_xpath = "//li[@class='archive-item-component']/a/@href"

        review_urls = self.extract_list(response.xpath(review_url_xpath))
        for review_url in review_urls:
            # urls that are under path /story/ are either not a review,
            # or need authorization to unlock the review
            if 'story' not in review_url:
                yield response.follow(url=review_url, callback=self.parse_review)

        # incremental scraping, avoid scrapy the reviews already exist
        if self.is_earlier_than_last_stored_review(response,
                                                   latest_review_date_xpath,
                                                   self.stored_last_date):
            return

        next_page = self.extract(response.xpath(next_page_xpath))
        if next_page:
            yield response.follow(url=next_page,
                                  callback=self.parse_category
                                  )

    def parse_review(self, response):
        # TODO verdict not found and source_id not found

        product_xpath = {"PicURL": "//*[@property='og:image']/@content"}
        review_xpaths = {
                "TestSummary": "//*[@property='og:description']/@content",
                "TestPros": "//div[@id='wired-tired']//p[1]/text()",
                "TestCons": "//div[@id='wired-tired']//p[2]/text()",
                "TestDateText": "(//meta[@itemprop='datePublished'])[1]/@content",
                }

        product = self.init_item_by_xpaths(response, "product", product_xpath)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        # utilize structured data
        # --------------------------------------------------
        # get review from structured data 'Review'
        review_json_ld = extruct_helper.extract_json_ld(
                            response.text, 'Review'
                            )
        if review_json_ld:
            review = extruct_helper.review_item_from_review_json_ld(
                    review_json_ld, review
                    )

        # get title from structure data 'NewsArticle', or Product
        # -------------------------------------------------------
        # wired.com use the format
        #'Review: [product name] | wired'as title
        # most of the time
        title = ''
        news_article_json_ld = extruct_helper.extract_json_ld(
                response.text, 'NewsArticle'
                )
        product_json_ld = extruct_helper.extract_json_ld(
                response.text, 'Product'
                )

        if news_article_json_ld:
            title = news_article_json_ld.get('headline').strip()
            review['TestTitle'] = title
        elif product_json_ld:
            title = product_json_ld.get('name').strip()
            review['TestTitle'] = title

        # double check product name
        # --------------------------------------------------
        product_name = review.get('ProductName')
        if not product_name:
            if title.startswith('Review:'):
                PRODUCT_INDEX = 1
                product_name = title.split(':')[PRODUCT_INDEX].strip()
            else:
                product_name = title.split('Review')[0].strip()

            # get rid of the the last part of 'product_name | wired'
            if '|' in product_name:
                product_name = product_name.split('|')[0].strip()

            review['ProductName'] = product_name

        product['ProductName'] = product_name

        # double check date
        # --------------------------------------------------
        date = review['TestDateText']
        if not date:
            date_xpath = "//meta[@name='parsely-pub-date']/@content"
            date = self.extract(response.xpath(date_xpath))
        review['TestDateText'] = date_format(date, '')

        # double check author
        # --------------------------------------------------
        author = review.get('Author', '')
        if not author:
            author_xpath = "//span[@itemprop='author']/a/text()"
            author = self.extract(response.xpath(author_xpath))
            if author:
                review['Author'] = author

        # parse category using tags
        category = self.get_categories_from_tags(response)
        if category:
            yield category
            if self.should_skip_category(category):
                return
            product['OriginalCategoryName'] = category['category_path']

        # double check PicURL for product
        # --------------------------------------------------
        pic_url = product.get('PicURL')
        if not pic_url:
            pic_url_xpath = "(//div[contains(@class, 'gallery-pic')]//img)[1]/@src"
            pic_url = self.extract_xpath(response, pic_url_xpath)
            if pic_url:
                product['PicURL'] = pic_url

        yield product

        # double check review rating
        # --------------------------------------------------
        rating_value = review.get('SourceTestRating')
        if not rating_value:
            rating_text_xpath = "//h3[contains(text(), 'RATING')]/following-sibling::p//text()"
            rating_text = self.extract_xpath(response, rating_text_xpath)
            rating_re = r'([0-9]+)'
            if rating_text:
                rating_match = re.search(rating_re, rating_text)
                if rating_match:
                    rating = rating_match.group(0)
                    review['SourceTestRating'] = rating
                    REVIEW_SCALE = unicode('10')
                    review['SourceTestScale'] = REVIEW_SCALE

        review["DBaseCategoryName"] = "PRO"
        yield review

# --------------------------------------------------------------------
# helper functions
# --------------------------------------------------------------------
    def get_categories_from_tags(self, response):
        # the order of the list item matters,
        # from detailed category to generatic one
        category_tags = (
                        'automotive', 'cars',
                        'running shoes', 'shoes', 'hero6', 'gopro',
                        'tripods', 'dslrs', 'fujifilm', 'instax', 'polaroid',
                        'instant photography', 'camcorders', 'cameras',
                        'photography', 'xbox one x', 'xbox one',
                        'super mario', 'nintendo switch','nintendo',
                        'playstation 4', 'pc gaming', 'console games',
                        'console gaming', 'wacom', 'games',
                        'kindle', 'e-readers', 'tablets', 'ultrabooks',
                        'e-books', 'chromebook', 'chromebooks', 'laptops',
                        'pcs', 'computers', 'timbuk2', 'backpack',
                        'fitness trackers', 'android wear', 'wearables',
                        'printers', 'health', 'coffee makers', 'coffee',
                        'moto x', 'oneplus', 'iphone', 'iphone x',
                        'motorola', 'samsung galaxy phones', 'smartphones',
                        'phones', 'apple watch', 'smartwatch', 'smartwatches',
                        'motorcycles', 'mechanical keyboards', 'keyboards',
                        'portable audio', 'earbuds', 'headphones',
                        'snowboards', 'snowboarding', 'radio', 'tvs',
                        'google home', 'smart home', 'cooking', 'home',
                        'amazon echo', 'wireless speakers', 'robot',
                        'car reviews' 'usb', 'sd cards', 'portable storage',
                        'augmented reality', 'cloud computing',
                        'smart speakers', 'speakers', 'pens', 'chromecast',
                        'wireless earbuds', 'grills', 'bags',
                        'microwaves', 'kitchen')

        tag_xpath = "//meta[@property='article:tag']/@content"\
                    "|//meta[@property='article:section']/@content"\
                    "|//meta[@name='keywords']/@content"

        page_tags = self.extract_list(response.xpath(tag_xpath))
        # remove duplicated tags and unify cases
        page_tags = list(set(t.lower() for t in page_tags))
        # some tags are included as one single str,
        # i.e. 'car reviews,mercedes-benz, sports cars'
        # i.e. ['a, b, c', d] -> [['a', 'b', 'c'], ['d']]
        page_tags = [tag.split(',') for tag in page_tags]
        # flatten list, i.e. -> ['a', 'b', 'c', 'd']
        page_tags = [tag for sublist in page_tags for tag in sublist]

        category_name = ''
        for category_tag in category_tags:
            if category_tag.lower() in page_tags:
                category_name = category_tag
                break

        if category_name:
            category = CategoryItem()
            category['category_path'] = category_name
            return category

    def is_earlier_than_last_stored_review(self,
                                           response,
                                           latest_review_date_xpath,
                                           stored_last_date):

        """ a helper function for utilizing incremental scraping.

        This function will check if the latest review in the response is
        earlier than our stored last date. The caller function will skip the
        review if that is out of date according to the boolean value returned
        by this function.

        :param response: HTTP reponse from HTTP request we sent
        :param latest_review_date_xpath: the xpath for latest review date
        :param stored_last_date: self stored last date
        :type response: scrapy Response object
        :type latest_review_date_xpath: string
        :type stored_last_date: datetime object
        :returns: weather the review is too old or not
        :rtype: Boolean

        .. todo:: date_formats might be better to pass as an arg.

        """

        latest_review_date_text = self.extract_xpath(
            response, latest_review_date_xpath
        )
        latest_review_date = dateparser.parse(
            latest_review_date_text,
            date_formats=['%Y-%m-%d']
        )
        return latest_review_date and latest_review_date < stored_last_date
