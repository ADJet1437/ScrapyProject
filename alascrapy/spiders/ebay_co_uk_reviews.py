# -*- coding: utf8 -*-
from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format
from alascrapy.items import CategoryItem, ReviewItem, ProductIdItem


class Ebay_co_uk_ReviewsSpider(AlaSpider):
    name = 'ebay_co_uk_reviews'
    allowed_domains = ['ebay.co.uk']

    # The script support two types of inputs, product_id and item_id,
    # and product_id takes priority
    product_url_prefix = 'https://www.ebay.co.uk/p/'
    item_url_prefix = 'https://www.ebay.co.uk/itm/'

    def __init__(self, product_id=None, item_id=None, *args, **kwargs):
        super(Ebay_co_uk_ReviewsSpider, self).__init__(self, *args, **kwargs)
        self.product_id = product_id
        self.item_id = item_id

    def start_requests(self):
        # product_id takes priority
        if self.product_id:
            product_url = self.product_url_prefix + self.product_id
            yield Request(url=product_url, callback=self.parse_product)
        elif self.item_id:
            item_url = self.item_url_prefix + self.item_id
            yield Request(url=item_url, callback=self.parse_product)
        else:
            print 'Please start the spider with one of the following arguments: product_id or item_id'

    def parse_product(self, response):
        category_leaf_xpath = "(//*[contains(@itemtype, 'BreadcrumbList')])[1]//li[@itemprop='itemListElement']" \
                              "[last()]//text()"
        category_path_xpath = "(//*[contains(@itemtype, 'BreadcrumbList')])[1]//li[@itemprop='itemListElement']//text()"
        category = CategoryItem()
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')

        if self.should_skip_category(category):
            return

        yield category

        product_xpaths = {
                "ProductName":"//h1[@itemprop='name']/text()",
                "PicURL":"//img[@itemprop='image']/@src",
        }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product["OriginalCategoryName"] = category['category_path']

        if self.product_id:
            product['source_internal_id'] = self.product_id

            id_value = self.extract(
                response.xpath("//div[@class='s-name' and contains(text(), 'MPN')]/"
                               "following-sibling::div[1]/text()"))
            if id_value:
                product_id = ProductIdItem.from_product(product)
                product_id['ID_kind'] = "mpn"
                product_id['ID_value'] = id_value
                yield product_id

            id_value = self.extract(response.xpath("//div[@class='s-name' and contains(text(), 'UPC')]/"
                                                   "following-sibling::div[1]/text()"))
            if id_value:
                product_id = ProductIdItem.from_product(product)
                product_id['ID_kind'] = "upc"
                product_id['ID_value'] = id_value
                yield product_id

            url_xpath = "//div[@class='see--all--reviews']/a/@href"
        elif self.item_id:
            product['source_internal_id'] = self.item_id

            id_value = self.extract(response.xpath("//td[contains(text(), 'MPN')]/following-sibling::td[1]/span/text()"))
            if id_value:
                product_id = ProductIdItem.from_product(product)
                product_id['ID_kind'] = "mpn"
                product_id['ID_value'] = id_value
                yield product_id

            id_value = self.extract(response.xpath("//td[contains(text(), 'EAN')]/following-sibling::td[1]/span/text()"))
            if id_value:
                product_id = ProductIdItem.from_product(product)
                product_id['ID_kind'] = "ean"
                product_id['ID_value'] = id_value
                yield product_id

            url_xpath = "//div[@class='reviews-right']//a[@class='sar-btn right']/@href"

        yield product

        single_url = self.extract(response.xpath(url_xpath))
        if single_url:
            single_url = get_full_url(response, single_url)
            request = Request(single_url, callback=self.parse_review)
            request.meta['product'] = product
            request.meta['review_url'] = response.url
            yield request
    
    def parse_review(self, response):
        product = response.meta['product']
        review_url = response.meta['review_url']

        containers_xpath = "//div[@itemprop='review']"
        containers = response.xpath(containers_xpath)
        for review_container in containers:
            review = ReviewItem()
            review['SourceTestRating'] = self.extract(review_container.xpath(".//*[@itemprop='ratingValue']/@content"))
            review['TestDateText'] = self.extract(review_container.xpath(".//span[@itemprop='datePublished']/text()"))
            review['TestSummary'] = self.extract_all(review_container.xpath(".//p[@itemprop='reviewBody']//text()"
                                                                            "[not(ancestor::a)]"))
            review['Author'] = self.extract(review_container.xpath(".//a[@itemprop='author']/text()"))
            review['TestTitle'] = self.extract(review_container.xpath(".//*[@itemprop='name']/text()"))
            review['TestUrl'] = review_url
            review["SourceTestScale"] = "5"

            review['ProductName'] = product['ProductName']
            review['source_internal_id'] = product['source_internal_id']
            
            review["DBaseCategoryName"] = "USER"
            if review["TestDateText"]:
                review["TestDateText"] = date_format(review["TestDateText"], '')

            yield review

        button_next_url = self.extract(response.xpath("//*[@rel='next']/@href"))
        if button_next_url:
            button_next_url = get_full_url(response.url, button_next_url)
            request = Request(button_next_url, callback=self.parse_review, meta=response.meta)
            yield request
