from alascrapy.lib.generic import date_format
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider


class MacWorldUKSpider(AlaSpider):
    name = 'macworld_co_uk'
    allowed_domains = ['macworld.co.uk']
    start_urls = ['https://www.macworld.co.uk/review/']
    custom_settings = {'COOKIES_ENABLED': True}

    def parse(self, response):
        next_page_xpath = "//li[@class='readOnText']/a/@href"
        review_urls_xpath = "//div[@class ='bd']/h2/a/@href"
        review_urls = self.extract_list(response.xpath(review_urls_xpath))

        for review_url in review_urls:
            yield response.follow(review_url, callback=self.parse_review)

        next_page = self.extract(response.xpath(next_page_xpath))
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_review(self, response):
            product_xpaths = {"PicURL": "//meta[@property='og:image']/@content",
                              "source_internal_id": "//meta[@property='bt:id']/@content",
                              "OriginalCategoryName": "//ul[@class='breadcrumbs']/li[position() < last()]/a/span/text()"
                              }

            review_xpaths = {"TestTitle": "//meta[@property='og:title']/@content",
                             "TestSummary": "//meta[@property='og:description']/@content",
                             "Author": "//span/a[@rel='author']/text()",
                             "source_internal_id": "//meta[@property='bt:id']/@content",
                             "TestVerdict": "//h2[contains(text(),'OUR VERDICT')]/following-sibling::p/text()"
                             }
            product = self.init_item_by_xpaths(response, "product", product_xpaths)
            review = self.init_item_by_xpaths(response, "review", review_xpaths)

            title_xpath = "//ul[@class='breadcrumbs']/li[last()]/a/span/text()"
            title = self.extract(response.xpath(title_xpath))
            if ":" in title_xpath:
                title = title.split(':')[0]
            product_name = title.replace('review', '').strip()
            product["ProductName"] = product_name

            # get rid of the prefix 'Home Reviews' for ocn from source page
            ocn = product.get('OriginalCategoryName', '')
            if ocn:
                ocn = ocn.replace('Home Reviews', '').strip()
                product['OriginalCategoryName'] = ocn
            yield product

            TEST_SCALE = 5
            rating_xpath = "//div[@class = 'ratings']/img/@src"
            source_rating = self.extract_list(response.xpath(rating_xpath))
            if source_rating:
                source_test_rating = sum('bluestarfilled' in s for s in source_rating)
                review["SourceTestRating"] = source_test_rating
                review["SourceTestScale"] = TEST_SCALE
            test_date_xpath = self.extract(response.xpath("//span[@class='publicationDate']/time/@datetime"))
            review["TestDateText"] = date_format(test_date_xpath, "%d %b %Y")
            review["DBaseCategoryName"] = "PRO"
            review["ProductName"] = product_name
            yield review
