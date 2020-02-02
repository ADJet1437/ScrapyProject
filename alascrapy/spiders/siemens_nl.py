# -*- coding: utf-8 -*-
import re
import time
import json
from scrapy.http import Request
import scrapy
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.items import ProductIdItem, ReviewItem


class SiemensNlSpider(AlaSpider):
    name = 'siemens_nl'
    allowed_domains = ['siemens-home.bsh-group.com', 'bazaarvoice.com']
    start_urls = ['https://www.siemens-home.bsh-group.com/nl/producten/vaatwassen',
                  'https://www.siemens-home.bsh-group.com/nl/producten/wassen-drogen']
    template = """https://api.bazaarvoice.com/data/batch.json?passkey=pvc6hum9903eu1vxjw7lnyi2l&apiversion=5.5&displaycode=12356-nl_nl&resource.q0=products&filter.q0=id%3Aeq%3A{}&stats.q0=reviews&filteredstats.q0=reviews&filter_reviews.q0=contentlocale%3Aeq%3Anl_NL&filter_reviewcomments.q0=contentlocale%3Aeq%3Anl_NL&resource.q1=reviews&filter.q1=isratingsonly%3Aeq%3Afalse&filter.q1=productid%3Aeq%3A{}&filter.q1=contentlocale%3Aeq%3Anl_NL&sort.q1=submissiontime%3Adesc&stats.q1=reviews&filteredstats.q1=reviews&include.q1=authors%2Cproducts%2Ccomments&filter_reviews.q1=contentlocale%3Aeq%3Anl_NL&filter_reviewcomments.q1=contentlocale%3Aeq%3Anl_NL&filter_comments.q1=contentlocale%3Aeq%3Anl_NL&limit.q1=8&offset.q1=0&limit_comments.q1=3&resource.q2=reviews&filter.q2=productid%3Aeq%3A{}&filter.q2=contentlocale%3Aeq%3Anl_NL&limit.q2=1&resource.q3=reviews&filter.q3=productid%3Aeq%3A{}&filter.q3=isratingsonly%3Aeq%3Afalse&filter.q3=issyndicated%3Aeq%3Afalse&filter.q3=rating%3Agt%3A3&filter.q3=totalpositivefeedbackcount%3Agte%3A3&filter.q3=contentlocale%3Aeq%3Anl_NL&sort.q3=totalpositivefeedbackcount%3Adesc&include.q3=authors%2Creviews%2Cproducts&filter_reviews.q3=contentlocale%3Aeq%3Anl_NL&limit.q3=1&resource.q4=reviews&filter.q4=productid%3Aeq%3A{}&filter.q4=isratingsonly%3Aeq%3Afalse&filter.q4=issyndicated%3Aeq%3Afalse&filter.q4=rating%3Alte%3A3&filter.q4=totalpositivefeedbackcount%3Agte%3A3&filter.q4=contentlocale%3Aeq%3Anl_NL&sort.q4=totalpositivefeedbackcount%3Adesc&include.q4=authors%2Creviews%2Cproducts&filter_reviews.q4=contentlocale%3Aeq%3Anl_NL&limit.q4=1&callback=BV._internal.dataHandler0"""

    def parse(self, response):
        sub_cat_contents = response.xpath(
            "//ul[@class='teaser-links list-unstyled']")
        for content in sub_cat_contents:
            review_indicator = 'Meer informatie'
            indicator_xpath = ".//text()"
            indicator = self.extract(content.xpath(indicator_xpath))
            if indicator != review_indicator:
                continue
            sub_cat_url_xpath = ".//a/@href"
            sub_cat_url = self.extract(content.xpath(sub_cat_url_xpath))
            yield response.follow(url=sub_cat_url, callback=self.parse_sub_cats)

    def parse_sub_cats(self, response):
        review_url_xpath = '//ul[@class="teaser-links list-unstyled"]//a/@href'
        review_urls = self.extract_list(response.xpath(review_url_xpath))
        for url in review_urls:
            yield response.follow(url=url, callback=self.filter_products_without_rating)

    def filter_products_without_rating(self, response):
        url = response.url
        # this means there are multiple products in this page
        products_with_review_filter = \
            "?f_averageoverallrating_min_s=0.5&f_averageoverallrating_max_s=5.5"
        new_url = url + products_with_review_filter
        yield Request(url=new_url, callback=self.go_to_review_page)

    def go_to_review_page(self, response):
        scrpit_str = self.extract(response.xpath(
            "//script[@data-init-data='ajax-productlist']"))
        links = re.findall(r'"link":"([^,]*)","review"', scrpit_str)
        ratings = re.findall(r'"rating":([\d.]{1,3}),', scrpit_str)
        max_page = re.findall(r'"pageNumber":([\d]{1,2}),', scrpit_str)
        for link, rating in zip(links, ratings):
            yield response.follow(url=link, callback=self.parse_review)
        # process next page
        if max_page:
            max_page = max_page[0]
            if int(max_page) > 1:
                for i in range(2, int(max_page) + 1):
                    next_page_filter = "&pageNumber={}".format(i)
                    new_url = response.url + next_page_filter
                    yield response.follow(url=new_url, callback=self.go_to_review_page)
        if not max_page:
            self.parse_review(response)

    def parse_review(self, response):
        product_xpaths = {
            "PicURL": "//meta[@property='og:image']/@content",
            "OriginalCategoryName": "//h1//span[last()]//text()",
            "ProductManufacturer": "//meta[@name='brand']/@content"
        }

        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        review = ReviewItem()

        sku = self.extract(response.xpath(
            "//span[@itemprop='productID']//text()"))
        brand = product.get('ProductManufacturer', '')
        product_name = ""
        product_name = brand + " " + sku
        product['ProductName'] = product_name
        review['ProductName'] = product_name

        review['DBaseCategoryName'] = 'USER'
        review['SourceTestScale'] = 5

        test_url = str(response.url).split('?')[0] + "#/Tabs=section-reviews/"
        product['TestUrl'] = test_url
        review['TestUrl'] = test_url

        product_id = ProductIdItem()
        product_id['ID_kind'] = 'price'
        price = self.extract(response.xpath("//p[@itemprop='price']//text()"))
        product_id['ID_value'] = price
        product_id['ProductName'] = product_name

        api_url = self.template.format(sku, sku, sku, sku, sku)
        yield scrapy.Request(url=api_url, callback=self.parse_results,
                             meta={'review': review,
                                   'product': product,
                                   'product_id': product_id})

    def parse_results(self, response):
        review = response.meta.get('review', '')
        product = response.meta.get('product', '')
        product_id = response.meta.get('product_id', '')
        data = response.text

        date = re.findall(r'"SubmissionTime":"(.*?)T', data)
        review_text = re.findall(r'"ReviewText":"(.*?)",', data)
        submission_id = re.findall(r'"SubmissionId":"(.*?)",', data)
        title = re.findall(r'"Title":"(.*?)",', data)
        rating = re.findall(r'"Rating":(\d{1}),', data)

        total_len = len(review_text)
        for i, j, k, m, n in zip(date[:total_len], review_text, submission_id, title, rating):
            review['TestDateText'] = i
            review['TestSummary'] = j
            review['source_internal_id'] = k
            review['TestTitle'] = m
            review['SourceTestRating'] = n
            product['source_internal_id'] = k
            product_id['source_internal_id'] = k

        yield review
        yield product
        yield product_id
