# -*- coding: utf8 -*-
from alascrapy.spiders.base_spiders import ala_spider as spiders

MAX_SENTENCES = 2


class EISASpider(spiders.AlaSpider):
    name = 'eisa_eu'
    allowed_domains = ['eisa.eu']
    start_urls = ['https://www.eisa.eu/awards/hi-fi/',
                  'https://www.eisa.eu/awards/home-theatre-audio/',
                  'https://www.eisa.eu/awards/home-theatre-display-video/',
                  'https://www.eisa.eu/awards/in-car-electronics/',
                  'https://www.eisa.eu/awards/mobile-devices/',
                  'https://www.eisa.eu/awards/photography/'
                  ]

    def parse(self, response):
        review_urls_xpath = "//li[@class='awards-box']/a/@href"
        review_urls = self.extract_list(response.xpath(review_urls_xpath))

        for review_url in review_urls:
            yield response.follow(url=review_url,
                                  callback=self.parse_review_products)

    def parse_review_products(self, response):
        product_xpaths = {"PicURL": "//div[@class='featured_img']/img/@src",
                          "ProductName": "//span[@class='award-title-real']"
                          "/text()",
                          "source_internal_id": "substring-after(//"
                          "link[@rel='shortlink']/@href, '=')",
                          "OriginalCategoryName": "substring-after("
                          "//a[@class='back-button']/text(), 'all')"
                          }

        review_xpaths = {"TestTitle": "//span[@class='award-title-real']/text()",
                         "ProductName": "//span[@class='award-title-real']"
                         "/text()",
                         "source_internal_id": "substring-after(//"
                         "link[@rel='shortlink']/@href, '=')",
                         "TestSummary": "//div[@class='content']/p/text()",
                         "award": "//span[@class='subtitle']/text()",
                         "AwardPic": "//div[@class='award-single']/img/@src"
                         }

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product["OriginalCategoryName"] = product["OriginalCategoryName"
                                                  ].replace("awards", '')

        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        review["DBaseCategoryName"] = "PRO"

        review["TestSummary"] = '.'.join(
            review["TestSummary"].split('.')[0:MAX_SENTENCES]) + '.'

        yield review
        yield product
