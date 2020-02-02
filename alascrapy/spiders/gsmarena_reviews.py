#!/usr/bin/env python

"""gsmarena Spider: """

__author__ = 'leo'

from scrapy.http import Request
from alascrapy.items import ProductItem, ReviewItem
from alascrapy.spiders.gsmarena_products import GsmArenaProductsSpider
from alascrapy.lib.generic import get_full_url, date_format


class GsmArenaReviewsSpider(GsmArenaProductsSpider):
    name='gsmarena_reviews'

    def parse_product(self, response):

        review_urls_xpath = "//a[contains(@class, 'module-reviews')]/@href"
        for item in super(GsmArenaReviewsSpider, self).parse_product(response):
            yield item

            if isinstance(item, ProductItem):
                product = item

                review_urls = self.extract_list_xpath(response, review_urls_xpath)
                for review_url in review_urls:
                    review_url = get_full_url(response, review_url)
                    request = Request(review_url,
                                      callback=self.parse_reviews,
                                      dont_filter=True)
                    request.meta['product'] = product
                    yield request

    def merge_review(self, original_review, new_review):
        # Adds the new values (from new_review) to the original_review if it
        # was not yet populated
        for attr, value in vars(new_review).items():
            if value and not getattr(original_review, attr, None):
                original_review[attr] = value

    def parse_reviews(self, response):
        product = response.meta['product']

        title_xpath = "//meta[@property='og:title']/@content"
        summary_xpath = '//meta[@property="og:description"]/@content'
        alt_summary_xpath = '//meta[@name="Description"]/@content'
        rating_xpath = "//div[contains(@class, 'final-score')]//div[@class='score-fill']/@data-score"
        alt_rating_xpath = '//span[@class="score"]/text()'
        pros_xpath = "//td[contains(@class, 'content-plus')]//li/text()"
        cons_xpath = "//td[contains(@class, 'content-cons')]//li/text()"
        alt_pros_xpath = "//ul[contains(@class, 'article-blurb-features')]//li/text()"
        alt_cons_xpath = "//ul[contains(@class, 'disadvantages')]//li/text()"
        author_xpath = "//span[@class='reviewer']/text()"
        date_xpath = "//span[@class='dtreviewed']/text()"

        last_review_page_url_xpath = '//ol[contains(@class, "page-options")]' \
            '/li/a[@href=""]/parent::li/preceding-sibling::li[1]/a/@href'

        title = self.extract_xpath(response, title_xpath)
        summary = self.extract_xpath(response, summary_xpath)
        if not summary:
            summary = self.extract_xpath(response, alt_summary_xpath)
        rating = self.extract_xpath(response, rating_xpath)
        if not rating:
            rating = self.extract_xpath(response, alt_rating_xpath)

        scale = ''
        if rating:
            scale = '5'
        pros = self.extract_all_xpath(response, pros_xpath, separator=' ; ')
        if not pros:
            pros = self.extract_all_xpath(response, alt_pros_xpath, separator=' ; ')
        cons = self.extract_all_xpath(response, cons_xpath, separator=' ; ')
        if not cons:
            cons = self.extract_all_xpath(response, alt_cons_xpath, separator=' ; ')
        author = self.extract_xpath(response, author_xpath)
        date = self.extract_xpath(response, date_xpath)
        if date:
            date = date_format(date, "%d %B %Y", languages=['en'])

        current_page_review = ReviewItem.from_product(product=product, tp='PRO', rating=rating, scale=scale,
                                         pros=pros, cons=cons, author=author, title=title,
                                         summary=summary, date=date, url=response.url)

        accumulated_review = response.meta.get('review')
        if accumulated_review:
            self.merge_review(accumulated_review, current_page_review)
        else:
            accumulated_review = current_page_review
                
        last_review_page_url = self.extract_xpath(response, last_review_page_url_xpath)

        if last_review_page_url:
            #If there are other pages on the review, goes to the last one
            last_review_page_url = get_full_url(response, last_review_page_url)
            request = Request(last_review_page_url, callback=self.parse_reviews)
            request.meta['review'] = accumulated_review
            request.meta['product'] = response.meta['product']
            yield request
        else:
            # If it's the last review page, try to get the veredict
            verdict_xpath = "//div[@id='review-body']/p[1]//text()"
            verdict = self.extract_xpath(response, verdict_xpath)
            accumulated_review['TestVerdict'] = verdict
            yield accumulated_review
