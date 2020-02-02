# -*- coding: utf8 -*-
from alascrapy.lib.generic import date_format
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider

TEST_SCALE = 5


class ZeroOnenetSpider(AlaSpider):
    name = '01net_com'
    allowed_domains = ['01net.com']
    start_urls = ['http://www.01net.com/smartphone-mobile/',
                  'http://www.01net.com/tablette-liseuse/',
                  'http://www.01net.com/pc-portables/',
                  'http://www.01net.com/photo/',
                  'http://www.01net.com/tv-video/',
                  'http://www.01net.com/objets-connectes/',
                  'http://www.01net.com/maison-connectee/',
                  'http://www.01net.com/jeux-video/',
                  'http://www.01net.com/voiture-connectee/'
                  ]

    def parse(self, response):
        review_urls_xpath = "//h2[@class='title-normal']/ancestor::a/@href|"\
                            "//a[@title='Voir le test']/@href|//" \
                            "h2[@class='title-big no-margin']/a/@href"
        review_urls = self.extract_list(response.xpath(review_urls_xpath))

        for review_url in review_urls:
            yield response.follow(review_url, callback=self.parse_review)

    def parse_review(self, response):
        product_xpaths = {
                          "PicURL": "//meta[@property='og:image']/@content"}

        review_xpaths = {
                "TestTitle": "//meta[@property='og:title']/@content",
                "TestSummary": "//meta[@name='description']/@content",
                "Author": "//div[@class='author-name']/span/text()",
                "TestPros": "//span[contains(text(),'Les plus')]"
                            "/ancestor::h3/following-sibling::ul/li/text()",
                "TestCons": "//span[contains(text(),'Les moins')]"
                            "/ancestor::h3/following-sibling::ul/li/text()",
                "TestVerdict": "//div[@id='verdict-article']//div/p/text()",
                "TestDateText": "substring-before(//time/@datetime, 'T')"
                        }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        title_xpath = "//meta[@property='og:title']/@content"
        title = self.extract(response.xpath(title_xpath))

        if title:
            product_name = title.replace('Test :', '').replace('Test du', '')\
                            .replace('TEST', '').strip()
            # To get a shorter product name,i use split with either (:) or (,)
            # Below are examples oftitles where why i apply the split function.
            # Test Amazon Fire 7, la tablette sauvée par son bon qualité-prix
            # Xiaomi Redmi 5 Plus: on a testé ce smartphone à 210 eurorôle...
            product_name = product_name.split(',')[0].split(':')[0]
            product["ProductName"] = product_name
            review["ProductName"] = product_name

        ocn_xpath = "//ul[@class='breadcrumb no-padding no-margin']"\
                    "/li/a/text()"
        original_category_name = self.extract_all(
            response.xpath(ocn_xpath), " | ")
        product["OriginalCategoryName"] = original_category_name
        source_int_id = self.extract(
            response.xpath("//meta[@property='og:url']/@content"))
        source_internal_id = source_int_id.split("-")[-1]
        product["source_internal_id"] = source_internal_id.strip(".html")
        source_test_rating_xpath = "//span[@itemprop='ratingValue']/text()"
        source_test_rating = self.extract(
                                    response.xpath(source_test_rating_xpath))

        if source_test_rating:
            review["SourceTestRating"] = source_test_rating
            review["SourceTestScale"] = TEST_SCALE
        review["DBaseCategoryName"] = "PRO"
        review["source_internal_id"] = source_internal_id.strip(".html")
        yield product
        yield review
