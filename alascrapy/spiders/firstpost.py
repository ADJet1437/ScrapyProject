# -*- coding: utf-8 -*-
import scrapy

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider

from alascrapy.items import ProductIdItem, CategoryItem

TEST_SCALE = 5


class FirstpostSpider(AlaSpider):
    name = 'firstpost'
    allowed_domains = ['firstpost.com']
    start_urls = ['https://www.firstpost.com/tech/reviews']

    def parse(self, response):
        review_link_xpaths = '//div[@class="col-md-8"]/'\
            'div[@class="text-wrapper"]/a/@href'
        review_links = self.extract_list(response.xpath(review_link_xpaths))
        for review in review_links:
            yield response.follow(review, callback=self.parse_review)

        next_page_xpath = '//a[@rel="next"]/@href'
        next_page = self.extract(response.xpath(next_page_xpath))

        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_review(self, response):
        product_xpaths = {
            'PicURL': '//meta[@property="og:image"]/@content',
            'source_internal_id': '//section[@id="article-main"]/@data-article-id',
        }

        review_xpaths = {
            'TestSummary': '//*[@property="og:description"]/@content',
            'Author': '//span[@class="post-by"]/a/text()',

            'TestVerdict': '//strong[contains(.,"Verdict")]'
            '/following-sibling::text() |//*[contains(text(),"Verdict")]'
            '//parent::p//following-sibling::p[1]//text()',

            'TestDateText': 'substring-before(//*'
            '[contains(@property,"published_time")]/@content, " ")',

            'source_internal_id': '//section[@id="article-main"]'
            '/@data-article-id',

            'SourceTestRating': '(//p[@class="big-rating-number"])[1]/text()',
        }

        review = self.init_item_by_xpaths(response, 'review', review_xpaths)
        product = self.init_item_by_xpaths(response, 'product', product_xpaths)

        title_xpath = '//h1[@class]/text()'
        title = self.extract(response.xpath(title_xpath))

        product_name = title.split(":")[0]
        product_name = product_name.replace(' review', '').strip()
        product_name = product_name.replace(' Review', '').strip()

        category = self.get_categories_from_tags(response)
        if category and not self.should_skip_category(category):
            yield category
            product['OriginalCategoryName'] = category['category_path']

        if review.get('SourceTestRating', ''):
            review['SourceTestScale'] = TEST_SCALE

        review['ProductName'] = product_name
        review['DBaseCategoryName'] = 'PRO'
        review['TestTitle'] = title

        PROS_XPATH = '//p[@class="desc-title"][contains(text(),"the good")]'\
            '/following-sibling::p[1]/text()'
        CONS_XPATH = '//p[@class="desc-title"][contains(text(),"the bad")]'\
            '/following-sibling::p[1]/text()'
        pros = self.extract_all(response.xpath(PROS_XPATH), separator=' ; ')
        cons = self.extract_all(response.xpath(CONS_XPATH), separator=' ; ')
        if pros:
            review['TestPros'] = pros
        if cons:
            review['TestCons'] = cons
        yield review

        product['ProductName'] = product_name
        yield product

        product_id = self.parse_price(product, response)
        yield product_id

    def parse_price(self, product, response):
        price_xpath = '//p[@class="cost-text"]/text()'
        price = self.extract(response.xpath(price_xpath))

        if price:
            return ProductIdItem.from_product(
                product,
                kind='price',
                value=price
            )

    def get_categories_from_tags(self, response):
        std_tags = (
            'iphone', 'Nokia', 'smartphone', 'phone', 'windows mobile',
            'zenbook', 'mac', 'macbook pro', 'laptop',
            'netbook', 'ultrabook', 'ltrabook', 'tablet', 'ipad',
            'kindle', 'reader', 'pc', 'monitor',
            'dslr', 'mirrorless camera',  'camera', 'camcorder', 'dv',
                    'earphone', 'headphone ', 'headset', 'speaker',
                    'tv', 'television', 'projector', 'xbox360', 'xbox',
                    'game', 'nintendo ds', 'wii', 'playstation',
                    'bl-ray player', 'seagate media player', 'media player',
                    'printer', 'scanner', 'keyboard', 'drive',
                    'apple watch ', 'smartwatch', 'watch', 'wearable',
                    'sshd', 'ssd', 'gps',
        )

        # due to the exceed amount of tags,
        # only get the last 6 to cover most cases
        tags_xpath = "//div[contains(@class, 'article-tags')]/a[position()>last()-5]/text()"
        src_tags = self.extract_list(response.xpath(tags_xpath))
        # remove duplicated tags and unify cases
        src_tags = list(set(t.lower() for t in src_tags))
        std_tags = (t.lower() for t in std_tags)

        ocn_found = ''
        for std_tag in std_tags:
            for src_tag in src_tags:
                if std_tag in src_tag:
                    ocn_found = std_tag
                    break
            else:
                continue
            break

        if ocn_found:
            category = CategoryItem()
            category['category_path'] = ocn_found
            return category
