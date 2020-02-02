from alascrapy.lib.generic import get_full_url
from alascrapy.spiders.base_spiders import ala_spider as spiders


class TipaSpider(spiders.AlaSpider):
    name = 'tipa_com'
    allowed_domains = ['tipa.com']
    start_urls = ['http://www.tipa.com/english/XXIV_tipa_awards_2014.html',
                  'http://www.tipa.com/english/XXV_tipa_awards_2015.html',
                  'http://www.tipa.com/english/XXVI_tipa_awards_2016.html',
                  'http://www.tipa.com/english/XXVII_tipa_awards_2017.html'

                  ]

    def parse(self, response):
        review_urls_xpath = "//p[@class='awardsListName']/strong/a/@href"
        review_urls = self.extract_list(response.xpath(review_urls_xpath))

        for review_url in review_urls:
            yield response.follow(url=review_url,
                                  callback=self.parse_review_products)

    def parse_review_products(self, response):
        product_xpaths = {"PicURL": "//div[@id = 'img-box']/img/@src",
                          "ProductName": "//title/text()"
                          }

        review_xpaths = {"TestTitle": "//title/text()",
                         "ProductName": "//title/text()",
                         "TestSummary": "//meta[@name='description']/@content",
                         "Author": "//div[@class='author-name']/span/text()",
                         "TestVerdict": "// article["
                         "@id = 'toptext-box']/div/text()|// article[@id ="
                         "'toptext-box']/div/span/text()",
                         "award": "//article[@id='toptext-box']/h1/text()",
                         }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['PicURL'] = get_full_url(response, product['PicURL'])

        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        review["DBaseCategoryName"] = "PRO"

        yield review
        yield product
