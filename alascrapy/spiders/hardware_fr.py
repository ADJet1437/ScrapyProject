# -*- coding: utf8 -*-
from datetime import datetime
import re

from alascrapy.lib.generic import get_full_url
from alascrapy.spiders.base_spiders import ala_spider as spiders


class HardwareFrSpider(spiders.AlaSpider):
    name = 'hardware_fr'
    allowed_domains = ['hardware.fr']
    start_urls = ['https://www.hardware.fr/html/articles/']
    current_page = 1

    def get_request_url(self):
        url = 'https://www.hardware.fr/html/articles/index.php?' \
            'page={}&annee=toutes&type=tous'

        return url.format(self.current_page)

    def parse(self, response):
        reviews_xpath = '//span[@class="dossier_titre"]//a/@href'
        review_links = response.xpath(reviews_xpath).extract()
        for link in review_links:
            if '/articles/' in link:
                yield response.follow(
                    url=link,
                    callback=self.parse_review_page
                )

        if len(review_links) > 0:
            self.current_page = self.current_page + 1
            yield response.follow(
                self.get_request_url(),
                callback=self.parse
            )

    def parse_review_page(self, response):
        product = self.parse_product(response)
        review = self.parse_review(response)
        yield product
        yield review

    def parse_product(self, response):
        product_xpaths = {
            'OriginalCategoryName': '//div[@class="tags"]/a/text()',
            'ProductName': 'substring-before(//title/text(), ":")',

            'PicURL': '(//div[@class="content_dossier"]'
            '//img[contains(@src, "media")])[1]/@src',
        }
        product = self.init_item_by_xpaths(response, 'product', product_xpaths)

        product['source_id'] = self.spider_conf['source_id']
        product['source_internal_id'] = self.get_sii(response)
        product['ProductName'] = self.get_product_name(response)
        product['PicURL'] = get_full_url(response, product['PicURL'])

        return product

    def parse_review(self, response):
        review_xpaths = {
            'Author': '//*[@rel="author"]/text()',
            'TestDateText': '//div[@class="date_auteur"]/text()',
            'TestSummary': '//meta[@name="description"]/@content',
            'TestTitle': '//title/text()',
        }

        review = self.init_item_by_xpaths(response, 'review', review_xpaths)

        # Date: "Publié le 10/08/2017 par"
        match = re.search(r'([\d\/]+)', review['TestDateText'])
        if match and match.group(1):
            original_date = match.group(1)  # '10/08/2017'
            formated_date = original_date.split('/')  # ['10','08','2017']
            formated_date = reversed(formated_date)  # ['2017','08','10']
            formated_date = "-".join(formated_date)  # 2017-08-10
            review['TestDateText'] = formated_date

        review['source_id'] = self.spider_conf['source_id']
        review['DBaseCategoryName'] = 'PRO'
        review['source_internal_id'] = self.get_sii(response)
        review['ProductName'] = self.get_product_name(response)

        return review

    def get_sii(self, response):
        chunks = response.url.split('/')
        SII_CHUNK_INDEX = 4
        sii = chunks[SII_CHUNK_INDEX]  # 973-1
        sii = sii.split('-')[0]
        return sii

    def get_product_name(self, response):
        xpath = '//title/text()'
        product_name = self.extract_all(response.xpath(xpath))

        # Removes commom words on the title
        commom_words = ['Dossier', 'HardWare.fr', 'Preview', 'en test']
        for word in commom_words:
            product_name = product_name.replace(word, '')  # Removes the word
            product_name = product_name.strip('-: ')  # Remove trailing marks

        product_name = product_name.split(':')[0]
        product_name = product_name.strip()

        return product_name
