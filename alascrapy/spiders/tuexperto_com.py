# -*- coding: utf8 -*-
from datetime import datetime
import js2xml

from scrapy.http import Request


from alascrapy.lib.dao import incremental_scraping as incremental_utils
from alascrapy.spiders.base_spiders import ala_spider as spiders


class TuExpertoComSpider(spiders.AlaSpider):
    name = 'tuexperto_com'
    allowed_domains = ['tuexperto.com']
    start_urls = ['https://www.tuexperto.com/']
    blog_feed_nonce = ''

    """
        tuexperto.com has lots of aticles that are not useful for scraping.
        The below list will filter only the actually desided categories.
        The categories that are not here will not be on the CSV file.
        Category "Actualidad" for example has ~95% of aticles (5% review) so
        I'm not including it to reduce the noise in the CSV file.
    """
    included_categories = [
        u'camara',
        u'convertibles',
        u'discos duros',
        u'hardware profesional',
        u'hemos probado',
        u'hifi',
        u'hogar',
        u'home cinema',
        u'impresoras',
        u'juegos',
        u'monitores',
        u'móvil',
        u'ordenadores',
        u'tablets',
        u'televisores',
        u'videojuegos',
        u'wearables',
    ]

    custom_settings = {
        'DOWNLOAD_DELAY': 2,
    }

    def __init__(self, *args, **kwargs):
        super(TuExpertoComSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf['source_id'])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)
        # Joins the string once so we don't do this for every evaluation
        self.included_categories_string = " ".join(self.included_categories)

    def get_request(self, page):
        DATE_FORMAT = 'Y-m-j'  # YYYY-MM-D equivalent of this API
        body = 'action=extra_blog_feed_get_content' \
            '&et_load_builder_modules=1' \
            '&blog_feed_nonce={blog_feed_nonce}' \
            '&to_page={page}' \
            '&posts_per_page=100' \
            '&order=desc' \
            '&orderby=date' \
            '&categories=' \
            '&show_featured_image=1' \
            '&blog_feed_module_type=standard' \
            '&et_column_type=' \
            '&show_author=1' \
            '&show_categories=1' \
            '&show_date=1' \
            '&show_rating=1' \
            '&show_more=1' \
            '&show_comments=1' \
            '&date_format={date_format}' \
            '&content_length=excerpt' \
            '&hover_overlay_icon=' \
            '&use_tax_query=0'.format(
                page=page,
                blog_feed_nonce=self.blog_feed_nonce,
                date_format=DATE_FORMAT)

        request = Request(
            url='https://www.tuexperto.com/wp-admin/admin-ajax.php',
            callback=self.parse_page,
            method='POST',
            body=body,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            meta={
                'next_page': page + 1
            }
        )
        return request

    def get_blog_feed_nonce(self, response):
        # this retieves the hash for the API to work
        id_data_xpath = '//script[@type="text/javascript" and ' \
            'contains(text(), "blog_feed_nonce")]/text()'
        # blog_feed_nonce_xpath
        bfn_xpath = '//property[@name="blog_feed_nonce"]/string/text()'

        js_text = self.extract_xpath(response, id_data_xpath)
        parsed = js2xml.parse(js_text)
        blog_feed_nonce = parsed.xpath(bfn_xpath)

        if blog_feed_nonce and len(blog_feed_nonce) > 0:
            return blog_feed_nonce[0]

        return None

    def parse(self, response):
        # Extracts the API key and yields the first request
        self.blog_feed_nonce = self.get_blog_feed_nonce(response)
        if self.blog_feed_nonce:
            yield self.get_request(1)

    def should_include_review(self, category=''):
        category = category.lower()
        return category in self.included_categories_string

    def parse_page(self, response):
        articles_xpath = '//article'
        article_nodes = response.xpath(articles_xpath)
        if len(article_nodes) > 0:
            yield self.get_request(response.meta['next_page'])
            for article_node in article_nodes:
                review = self.parse_review_node(article_node, response)
                product = self.parse_product_node(article_node, response)
                if self.should_include_review(product['OriginalCategoryName']):
                    yield review
                    yield product

    def parse_product_node(self, article_node, response):
        product_xpaths = {
            'OriginalCategoryName': './/a[@rel="tag"]/text()',
            'PicURL': './/div[@class="header"]/a/img/@src',
            'ProductName': './/div[@class="header"]/a/@title',
            'source_internal_id': 'substring-after(./@id, "post-")',
            'TestUrl': './/div[@class="header"]/a/@href',
        }
        product = self.init_item_by_xpaths(
            response, 'product', product_xpaths, selector=article_node)

        product['source_id'] = self.spider_conf['source_id']

        return product

    def parse_review_node(self, article_node, response):
        review_xpaths = {
            'Author': './/a[@rel="author"]/text()',
            'ProductName': './/div[@class="header"]/a/@title',
            'source_internal_id': 'substring-after(./@id, "post-")',
            'TestDateText': './/span[@class="updated"]/text()',
            'TestSummary': './/div[@class="excerpt entry-summary"]/p/text()',
            'TestTitle': './/div[@class="header"]/a/@title',
            'TestUrl': './/div[@class="header"]/a/@href',
        }

        review = self.init_item_by_xpaths(
            response, 'review', review_xpaths, selector=article_node)

        review['source_id'] = self.spider_conf['source_id']
        review['DBaseCategoryName'] = 'PRO'

        return review
