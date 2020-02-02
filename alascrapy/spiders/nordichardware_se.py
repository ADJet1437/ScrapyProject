# -*- coding: utf8 -*-
import json
from urllib import urlencode

from scrapy.http.request import Request
from scrapy.selector import Selector

from alascrapy.spiders.base_spiders import ala_spider as spiders


class NordicHardwareSeSpider(spiders.AlaSpider):
    name = 'nordichardware_se'
    allowed_domains = ['nordichardware.se']

    def get_request(self, page):
        url = 'https://www.nordichardware.se/wp-admin/admin-ajax.php?' \
            'td_theme_name=Newspaper&v=8.0'
        body = {
            'action': 'td_ajax_loop',
            'loopState[sidebarPosition]': '',
            'loopState[moduleId]': '1',
            'loopState[currentPage]': page,  # pagination parameter
            'loopState[max_num_pages]': '137',
            'loopState[atts][category_id]': '6',
            'loopState[atts][offset]': '5',
            'loopState[ajax_pagination_infinite_stop]': '3',
            'loopState[server_reply_html_data]': ''
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        }
        request = Request(
            url=url,
            method='POST',
            body=urlencode(body),
            headers=headers,
            callback=self.parse,
            meta={
                'next-page': page + 1
            }
        )

        return request

    def start_requests(self):
        yield self.get_request(0)

    def parse(self, response):
        body = json.loads(response.text)

        # Fetches until reaches 'max_num_pages' (inclusive)
        last_page = int(body.get('max_num_pages', '0'))
        next_page = response.meta.get('next-page', 0)
        if next_page <= last_page:
            yield self.get_request(next_page)

        html_text = body.get('server_reply_html_data', '')
        selector = Selector(text=html_text)
        reviews_xpath = '//h3/a/@href'
        review_links = selector.xpath(reviews_xpath).extract()
        for link in review_links:
            yield response.follow(url=link, callback=self.parse_review_page)

    def parse_review_page(self, response):
        product = self.parse_product(response)
        # review_or_request contains the complete review or the request for
        # completing the half scraped review.
        review_or_request = self.parse_review(response)
        yield review_or_request
        yield product

    def get_product_name(self, response):
        product_name_xpath = '//meta[@property="og:title"]/@content'
        product_name = self.extract(response.xpath(product_name_xpath))
        product_name = product_name.replace('Test:', '')
        product_name = product_name.split('-')[0]
        return product_name.strip()

    def parse_product(self, response):
        product_xpaths = {
            'PicURL': '//meta[@property="og:image"][1]/@content',

            'source_internal_id': 'substring-after('
            '//link[@rel="shortlink"]/@href, "=")',
        }
        product = self.init_item_by_xpaths(response, 'product', product_xpaths)

        # Extract OriginalCategoryName
        ocn_xpath = '//div[@class="entry-crumbs"]//a/text()'
        ocn = response.xpath(ocn_xpath).extract()
        # removes first item ("Home")
        ocn = ocn[1:]
        ocn = " | ".join(ocn)
        # Removes all spaces and pipes from the boundaries
        ocn = ocn.replace('Test', '').strip('| ')
        product['OriginalCategoryName'] = ocn

        product['TestUrl'] = response.url
        product['source_id'] = self.spider_conf['source_id']
        product['ProductName'] = self.get_product_name(response)

        return product

    def parse_review(self, response):
        review_xpaths = {
            'Author': '//*[@itemprop="author"]/*[@itemprop="name"]/@content',
            'TestSummary': '//meta[@property="og:description"]/@content',
            'TestTitle': '//meta[@property="og:title"]/@content',

            'TestDateText': 'substring-before('
            '//meta[@property="article:published_time"]/@content, "T")',

            'source_internal_id': 'substring-after('
            '//link[@rel="shortlink"]/@href, "=")',
        }

        review = self.init_item_by_xpaths(response, 'review', review_xpaths)

        review['TestUrl'] = response.url
        review['source_id'] = self.spider_conf['source_id']
        review['ProductName'] = self.get_product_name(response)
        review['DBaseCategoryName'] = 'PRO'

        conclusion_page_xpath = '//ul[@id="toc"]' \
            '/li[position() = (last() - 1)]/a/@href'
        url = self.extract(response.xpath(conclusion_page_xpath))
        if url:
            request = response.follow(
                url=url,
                callback=self.parse_conclusion_page,
                meta={'review': review}
            )
            return request
        return review

    def parse_conclusion_page(self, response):
        pros_cons_xpath = '//div[contains(@class, "su-note")]//p//text()'
        pros_cons = response.xpath(pros_cons_xpath).extract()

        pros = []
        cons = []
        for pro_con in pros_cons:
            pro_con = pro_con.strip()
            # Checks the start of the string and remove the fist two
            # characters: "+ " or "- "
            if pro_con.startswith('+'):
                pros.append(pro_con[2:])
            elif pro_con.startswith(u'–'):
                cons.append(pro_con[2:])

        review = response.meta.get('review')
        review['TestPros'] = " | ".join(pros)
        review['TestCons'] = " | ".join(cons)

        yield review
