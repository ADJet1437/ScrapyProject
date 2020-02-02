	# -*- coding: utf8 -*-
from datetime import datetime
import re

from scrapy.http import Request
from scrapy.utils.sitemap import Sitemap
from scrapy.spiders.sitemap import iterloc

from alascrapy.spiders.base_spiders.ala_sitemap_spider import AlaSitemapSpider
from alascrapy.lib.generic import get_full_url, remove_suffix
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import CategoryItem

import alascrapy.lib.extruct_helper as extruct_helper


class Toptenreviews_comSpider(AlaSitemapSpider):
    name = 'toptenreviews_com'
    allowed_domains = ['toptenreviews.com']

    sitemap_urls = ['http://www.toptenreviews.com/sitemap.xml']

    # For now we only scrape important categories (as we may get blocked)
    sitemap_rules = [('/tv/best-[^/]+/$', 'parse_category'),
                     ('/headphones/best-[^/]+/$', 'parse_category'),
                     ('/home-entertainment/best-[^/]+/$', 'parse_category'),
                     ('/gps/best-[^/]+/$', 'parse_category'),
                     ('/smart-home/best-[^/]+/$', 'parse_category'),
                     ('/photo-video/best-[^/]+/$', 'parse_category'),
                     ('/best-[^/]+drones/$', 'parse_category'),
                     ('/phones/best-[^/]+/$', 'parse_category')]

    # To get around blocking, use cookies and slow the spider down to human speed
    custom_settings = {'COOKIES_ENABLED': True,
                       'DOWNLOAD_DELAY': 8}

    # As the site blocks us, to process urls in sitemap faster, we need to extract category info from them
    # TODO: this function reuses that of its base class and looks ugly, re-write it?
    def _parse_sitemap(self, response):
        body = self._get_sitemap_body(response)
        if body is None:
            self.logger.warning("Ignoring invalid sitemap: %(response)s",
                                {'response': response}, extra={'spider': self})
            return
        s = Sitemap(body)
        if s.type == 'urlset':
            for loc in iterloc(s):
                for r, c in self._cbs:
                    if r.search(loc):
                        category_regex = r'toptenreviews\.com/(.*)/$'
                        match = re.search(category_regex, loc)

                        # the URL pattern must be change if there is no category matching
                        if not match:
                            break

                        category = CategoryItem()
                        category['category_path'] = match.group(1)
                        category['category_url'] = loc
                        if self.should_skip_category(category):
                            break

                        yield category
                        request = Request(loc, callback=c)
                        request.meta['category'] = category
                        yield request
                        break

    def parse_category(self, response):
        urls_xpath = u"//a[contains(./text(), 'See Details')]/@href"
        urls = self.extract_list(response.xpath(urls_xpath))

        for single_url in urls:
            single_url = get_full_url(response, single_url)
            request = Request(single_url, callback=self.parse_review, meta=response.meta)
            yield request

    def parse_review(self, response):
        category = response.meta['category']

        product_xpaths = {
                "source_internal_id": u"//div[@class='article_content']/descendant-or-self::*[./@data-product-id][1]/@data-product-id",
                "ProductName":u"normalize-space(//h1)",
                "PicURL":u"//meta[@property='og:image']/@content",
        }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['ProductName'] = remove_suffix(product['ProductName'], ' Review')
        product['TestUrl'] = response.url
        product['OriginalCategoryName'] = category['category_path']

        if product.get('PicURL', ''):
            product['PicURL'] = get_full_url(response, product['PicURL'])

        review_xpaths = {
                "TestDateText":u"//*[@itemprop='datePublished']/@content",
                "TestPros":u"//p[.//*[contains(text(),'Pros')]]/text()",
                "TestCons":u"//p[.//*[contains(text(),'Cons')]]/text()",
                "TestSummary":u"string(//h2[text()='Summary']/following::p)",
                "TestVerdict":u"//p[.//*[contains(text(),'Verdict')]]/text()",
                "TestTitle":u"normalize-space(//h1)",
                "award":u"(//a[contains(@alt, 'Award')])[1]/@alt",
                "AwardPic":u"(//a[contains(@alt, 'Award')])[1]/@data-bgset"
        }
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        review['TestUrl'] = response.url

        review_json_ld = extruct_helper.extract_json_ld(response.text, 'Review')
        if review_json_ld:
            review = extruct_helper.review_item_from_review_json_ld(review_json_ld, review)

        if review.get('ProductName'):
            product['ProductName'] = review['ProductName']
        else:
            review['ProductName'] = product['ProductName']

        awpic_link = review.get("AwardPic", "")
        if awpic_link:
            review["AwardPic"] = get_full_url(response, awpic_link)

        # Not a detailed review, can only get summary and verdict
        if not (review['TestSummary'] or review['TestVerdict'] or review['TestPros'] or review['TestCons']):
            summary_alt_xpath = "string(//section[@id='Intro']/p[1])"
            verdict_alt_xpath = "string(//section[@id='Intro']/p[last()])"
            review['TestSummary'] = self.extract(response.xpath(summary_alt_xpath))
            review['TestVerdict'] = self.extract(response.xpath(verdict_alt_xpath))

        review["DBaseCategoryName"] = "PRO"
        review["SourceTestScale"] = "10"

        yield product
        yield review
