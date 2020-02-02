# -*- coding: utf8 -*-
from datetime import datetime
import dateparser
import alascrapy.lib.extruct_helper as extruct_helper

from scrapy.http import Request, HtmlResponse

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import CategoryItem, ReviewItem


class Pcadvisor_co_ukSpider(AlaSpider):
    name = 'techadvisor_co_uk'
    allowed_domains = ['techadvisor.co.uk']
    start_urls = ['http://www.techadvisor.co.uk/review']

    #custom_settings = {'COOKIES_ENABLED': True,
    #                   'DOWNLOAD_DELAY': 8}

    def __init__(self, *args, **kwargs):
        super(Pcadvisor_co_ukSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])
        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)

    def parse(self, response):
        review_url_xpath = "//ul/li[@class='media']/a/@href"
        latest_date_xpath = "(//ul/li[@class='media']//*[@class='startDate'])[1]/text()"

        next_page_xpath = "(//*[@rel='next'])[1]/@href"

        # get the date of latest review of the page
        latest_date_text = self.extract(response.xpath(latest_date_xpath))
        latest_date = dateparser.parse(latest_date_text)

        if latest_date and latest_date < self.stored_last_date:
            return

        # extract all review urls and send a request for each of them
        review_urls = self.extract_list(response.xpath(review_url_xpath))
        for review_url in review_urls:
            yield response.follow(url=review_url, callback=self.parse_product)

        # go to next page
        next_page_url = self.extract(response.xpath(next_page_xpath))
        if next_page_url:
            yield response.follow(url=next_page_url, callback=self.parse)

    def parse_product(self, response):
        original_url = response.url
        
        category_leaf_xpath = "//ul[contains(@class,'crumb')]/li[last()-1]/a//text()"
        category_path_xpath = "//ul[contains(@class,'crumb')]/li[position()<last()]/a//text()"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        # initialize a product
        product_xpaths = {
                "source_internal_id": "//meta[@property='bt:id']/@content",
                "ProductName": "//*[@itemprop='itemReviewed']/meta[@itemprop='name']/@content",
                "PicURL": "//meta[@property='og:image']/@content"
        }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['OriginalCategoryName'] = category['category_path']

        product_name = self.extract(response.xpath("//header[@class='content-area__header']/h1/text()"))
        if 'review' in product_name:
            productname = product_name.replace("review", "").replace("Review", "")
        else:
            productname = product_name

        product['ProductName'] = productname

        review = ReviewItem()
        review['ProductName'] = productname
        review['source_internal_id'] = product['source_internal_id']
        review['Author'] = self.extract(response.xpath("//p[@class='metaArticleData']/span[@class='author']//text()"))
        date = self.extract(response.xpath("//p[@class='metaArticleData']//time[@class='dateCreated']/@datetime"))
        review['TestDateText'] = str(date).split("T")[0]
        sourcetestrating = self.extract(response.xpath("(//meta[@itemprop='ratingValue']/@content)[1]"))
        if sourcetestrating:
            review['SourceTestRating'] = sourcetestrating
            review['SourceTestScale'] = '5'        
        review['TestUrl'] = response.url
        review['DBaseCategoryName'] = 'PRO'
        summary_xpath = "//meta[@property='og:description']/@content"
        award_xpath = "//meta[@itemprop='award']/@content"
        award_image_xpath = "//meta[@itemprop='award']/following-sibling::img/@src"

        review['TestSummary'] = self.extract(response.xpath(summary_xpath))
        award_name = self.extract(response.xpath(award_xpath))
        if award_name:
            review['award'] = 'TechAdvisor ' + award_name
        awardpic = self.extract(response.xpath(award_image_xpath))
        if awardpic:
            review['AwardPic'] = awardpic
        
        yield product
        yield review