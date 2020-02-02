# -*- coding: utf8 -*-
import re
from datetime import datetime

from alascrapy.lib.generic import date_format
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider


class ImagingResourceSpider(AlaSpider):
    name = 'imaging_resource'
    allowed_domains = ['imaging-resource.com']
    start_urls = ['http://www.imaging-resource.com/cameras/reviews/',
                  'http://www.imaging-resource.com/lenses/reviews/',
                  'http://www.imaging-resource.com/PRINT.HTM']
    # get around with blocking issue
    custom_settings = {'COOKIES_ENABLED': True}

    def parse(self, response):
        brand_urls_xpath = "//tr[@valign='top'][position()=1]/td/a/@href"
        brand_urls = self.extract_list(response.xpath(brand_urls_xpath))

        if brand_urls:
            for brand_url in brand_urls:
                yield response.follow(brand_url, callback=self.parse_brand_review_headings)
        else:
            review_url_xpath = "//div[@align='right']/a/@href"
            review_urls = self.extract_list(response.xpath(review_url_xpath))

            for review_url in review_urls:
                yield response.follow(review_url, callback=self.parse_review_products)

    def parse_brand_review_headings(self, response):
        review_url_xpath = "//h2[@class ='cameraHeading']/a/@href"
        review_urls = self.extract_list(response.xpath(review_url_xpath))

        for review_url in review_urls:
            yield response.follow(review_url, callback=self.parse_review_products)

    def parse_review_products(self, response):
        product_xpaths = {"PicURL": "//meta[@property='og:image']/@content"
                          }

        review_xpaths = {"Author": "//a[@rel='author']/text()",
                         "TestPros": "//strong[contains(text(),'Pros')]/ancestor::p/text() | " 
                                     "(//span[contains(text(),'Pros')]/following-sibling::p)[1]/text() ",
                         "TestCons": "//strong[contains(text(),'Cons')]/ancestor::p/text() | " 
                                     "(//span[contains(text(),'Cons')]/following-sibling::p)[1]/text() ",
                         "TestVerdict": "//strong/em[contains(text(),'Summary')]"
                                        "/ancestor::strong/following-sibling::em/text() |"
                                        "(//h2[contains(text(),'Summary')]/following-sibling::p)[1]/text()"
                         }

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        ocn_xpath = "//span[@id='breadcrumbs']/a[not(contains(text(),'Reviews'))]/text()|"\
                    "//span[@class='breadcrumbs']/a[not(contains(text(),'Reviews'))]/text()"
        original_category_name = self.extract_all(response.xpath(ocn_xpath), " | ")

        title_xpath = "//meta[@property='og:title']/@content |" \
                      "//title/text()"
        title = self.extract(response.xpath(title_xpath))
        product_name = title
        if product_name:
            product_name = title.replace('Review', '').replace('review', '').strip()
        product["ProductName"] = product_name
        product["OriginalCategoryName"] = original_category_name

        if not product.get("PicURL", ""):
            pic_url_xpath = "//div[@class='lens_image']/img/@src"
            pic_url = self.extract(response.xpath(pic_url_xpath))
            if pic_url:
                product['PicURL'] = pic_url
        yield product

        # TODO need to get both scale for 5 and 10,
        # hard code does not work
        TEST_SCALE = 5 
        source_test_rating_xpath = "(//span[@itemprop='ratingValue'])[1]/text()"
        source_test_rating = self.extract(response.xpath(source_test_rating_xpath))
        # TODO take care of 2/10 case
        if source_test_rating:
            # two rating scale system exist in the source
            if source_test_rating > 5:
                source_rating = float(source_test_rating) / 2
                source_rating = round(source_rating, 1)
                source_test_rating = source_rating
            review["SourceTestRating"] = source_test_rating
            review["SourceTestScale"] = TEST_SCALE

        test_date_xpath1 = self.extract(response.xpath("(//p)[1]/text()"
                                                       "[preceding-sibling::br and following-sibling::br]"))
        test_date_xpath2 = self.extract(response.xpath("//span[@itemprop='datePublished']/text()"))
        if test_date_xpath1:
            test_date = datetime.strptime(test_date_xpath1, '%B %d, %Y')
            test_date = test_date.strftime('%Y/%m/%d')
            review["TestDateText"] = date_format(test_date, "%d %b %Y")
        elif test_date_xpath2:
            review["TestDateText"] = date_format(test_date_xpath2, "%d %b %Y")

        summary_xpath = "//p/strong[contains(text(),'Conclusion')]/ancestor::p/text()|"\
                        "//p/strong[contains(text(),'Conclusion')]/ancestor::p/following-sibling::p/text()|"\
                        "//h3[contains(text(),'Summary')]/following-sibling::p/text()|"\
                        "//h2/following-sibling::p/text()"
        test_summary = self.extract(response.xpath(summary_xpath))
        if len(test_summary) > 100:
            test_summary_text = ' '.join(re.split(r'(?<=[.:;])\s', test_summary)[:2])
            review["TestSummary"] = test_summary_text

        review["DBaseCategoryName"] = "PRO"
        review["ProductName"] = product_name

        if title:
            review["TestTitle"] = title
        yield review
