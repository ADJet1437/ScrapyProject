# -*- coding: utf8 -*-
from datetime import datetime

from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_sitemap_spider import AlaSitemapSpider
from alascrapy.lib.generic import get_full_url, date_format
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import CategoryItem, ProductItem, ReviewItem, ProductIdItem

class Pcworld_enSpider(AlaSitemapSpider):
    name = 'pcworld_en'
    allowed_domains = ['pcworld.com']
    sitemap_urls = ['https://www.pcworld.com/seo/sitemap/https/articles/index.xml']
    sitemap_rules = [('.+\\.html', 'extract_reviews')]
    sitemap_follow = []

    def __init__(self, *args, **kwargs):
        super(Pcworld_enSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        if self.stored_last_date:
            self.stored_last_date = datetime(self.stored_last_date.year,
                                             self.stored_last_date.month,
                                             1)
        else:
            self.stored_last_date = datetime(1970,1,1)

        current_date = datetime.today()
        for year in range(self.stored_last_date.year, current_date.year+1):
            months_span = range(12)
            if year==self.stored_last_date.year:
                months_span = months_span[self.stored_last_date.month-1:]
            if year==current_date.year and current_date.month != 12:
                months_span = months_span[:current_date.month-12]
            for month in months_span:
                if month+1 < 10:
                    self.sitemap_follow.append('urlset.{0}.0{1}.xml'.format(year, month+1))
                else:
                    self.sitemap_follow.append('urlset.{0}.{1}.xml'.format(year, month+1))
        # Reinit the spider in order to reload the dynamically generated sitemap_follow
        super(Pcworld_enSpider, self).__init__(self, *args, **kwargs)

    def extract_reviews(self, response):
        is_review = self.extract(response.xpath("//div[@class='category']//text()"))
        if is_review.lower() != "review" and is_review.lower() != "update":
            return
        category_leaf_xpath = "//li[last()]//span[@itemprop='title']/text()"
        category_path_xpath = "//span[@itemprop='title']/text()"
        category = CategoryItem()
        category['category_url'] = response.url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_name_xpath = "(//*[@itemprop='itemReviewed'])[1]//*[@itemprop='name']/text()"
        product_name_xpath_alt = "//h1[@itemprop='headline']/text()"

        product_xpaths = {
            "ProductName": product_name_xpath,
            "PicURL":"//meta[@property='og:image']/@content",
        }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        if not product.get('ProductName', ''):
            product['ProductName'] = self.extract(response.xpath(product_name_xpath_alt))

        product['TestUrl'] = response.url
        product["PicURL"] = get_full_url(response.url, product["PicURL"])
        product["OriginalCategoryName"] = category['category_path']
        product['source_internal_id'] = self.trimId(response.xpath("//body/@id").extract_first())
        review_xpaths = {
            "TestDateText":"//span[@itemprop='datePublished']/text()",
            "TestPros":"//div[@class='product-pros']//li/text()",
            "TestCons":"//div[@class='product-cons']//li/text()",
            "TestSummary":"//meta[@property='og:description']/@content[last()]",
            "TestVerdict":"//h2[last()]/following-sibling::p[1]/text()",
            "Author":"//a[@rel='author']/span[@itemprop='name']/text()",
            "TestTitle":"//h1[@itemprop='headline']/text()",
        }
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        review['ProductName'] = product['ProductName']
        review['TestUrl'] = response.url
        review['SourceTestRating'] = response.xpath("//meta[@itemprop='ratingValue']/@content").extract_first()
        review["DBaseCategoryName"] = "PRO"
        review["SourceTestScale"] = "5"
        try:
            review['source_internal_id'] = product['source_internal_id']
        except:
            pass
        if review["TestDateText"]:
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(review["TestDateText"], "%b %d, %Y %I:%M %p", ["en"])
        yield product
        yield review

    def trimId(self, article):
        try:
            return int(article[7::])
        except:
            pass