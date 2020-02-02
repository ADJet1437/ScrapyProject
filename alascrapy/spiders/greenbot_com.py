# -*- coding: utf8 -*-
from datetime import datetime
import re

from scrapy.http import Request, HtmlResponse
from scrapy.selector import Selector

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import CategoryItem, ProductItem, ReviewItem, ProductIdItem


class Greenbot_comSpider(AlaSpider):
    name = 'greenbot_com'
    allowed_domains = ['greenbot.com']
    start_urls = ['http://www.greenbot.com/reviews/?start=0']

    def parse(self, response):                    
        original_url = response.url
        urls_xpath = "//div[starts-with(@class,'index-promo') or starts-with(@class,'river-well')]//h3/descendant-or-self::a[1]/@href"
        urls = self.extract_list(response.xpath(urls_xpath))
        if urls and len(urls) > 0:
            for single_url in urls:
                single_url = get_full_url(original_url, single_url)
                yield Request(single_url, callback=self.level_2)
            url_xpath = "//a[starts-with(@id,'load-more')]/@href"
            single_url = self.extract(response.xpath(url_xpath))
            if single_url:
                single_url = get_full_url(original_url, single_url)
                yield Request(single_url, callback=self.parse)
    
    def level_2(self, response):
        original_url = response.url
        category_leaf_xpath = "//nav[starts-with(@class,'breadcrumbs')]/ul/li[last()]//text()"
        category_path_xpath = "//nav[starts-with(@class,'breadcrumbs')]/ul/li//text()"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
            "source_internal_id": "//meta[@property='og:url']/@content",
            "ProductName":"(//article/descendant-or-self::ul[@class='aag-list'][1]/descendant-or-self::*[@class='product-name']/descendant-or-self::*[text()][last()]//text() | //meta[@property='og:title']/@content | //h1//text())[last()]",
            "PicURL":"(//*[(name()='div' and @itemprop='reviewBody') or (name()='figure' and @id='page-lede')]/descendant-or-self::img[1]/@src | //meta[@property='og:image' and normalize-space(./@content)]/@content)[1]",
        }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['TestUrl'] = original_url
        picurl = product.get("PicURL", "")
        if picurl and picurl[:2] == "//":
            product["PicURL"] = "https:" + product["PicURL"]
        if picurl and picurl[:1] == "/":
            product["PicURL"] = get_full_url(original_url, picurl)
        manuf = product.get("ProductManufacturer", "")
        try:
            product["OriginalCategoryName"] = category['category_path']
        except:
            pass
        ocn = product.get("OriginalCategoryName", "")
        review_xpaths = { 
            "source_internal_id": "//meta[@property='og:url']/@content",
            "ProductName":"(//article/descendant-or-self::ul[@class='aag-list'][1]/descendant-or-self::*[@class='product-name']/descendant-or-self::*[text()][last()]//text() | //meta[@property='og:title']/@content | //h1//text())[last()]",
            "SourceTestRating":"translate(string(concat(//article/descendant-or-self::ul[@class='aag-list'][1]/descendant-or-self::div[@class='rating' and not(//*[starts-with(normalize-space(),'Rating:')])][1]/meta/@content, substring-before(concat(substring-before(concat(normalize-space(substring-after(//*[starts-with(normalize-space(),'Rating:')]//text(),'Rating:')),'/'),'/'),' '),' '),string(number(substring-before(substring-after(//p/img[contains(@src,'rating') and not(//div[@class='rating'])]/@src,'rating_'),'-')) div 10),translate(string(count(//article/descendant-or-self::div[@class='rating'][1]/span[contains(@class,'one-star') and not(//meta[@itemprop='ratingValue'])])*1 + count(//article/descendant-or-self::div[@class='rating'][1]/span[contains(@class,'one-half-star') and not(//meta[@itemprop='ratingValue'])])*1.5 + count(//article/descendant-or-self::div[@class='rating'][1]/span[contains(@class,'two-star') and not(//meta[@itemprop='ratingValue'])])*2 + count(//article/descendant-or-self::div[@class='rating'][1]/span[contains(@class,'two-half-star') and not(//meta[@itemprop='ratingValue'])])*2.5 + count(//article/descendant-or-self::div[@class='rating'][1]/span[contains(@class,'three-star') and not(//meta[@itemprop='ratingValue'])])*3 + count(//article/descendant-or-self::div[@class='rating'][1]/span[contains(@class,'three-half-star') and not(//meta[@itemprop='ratingValue'])])*3.5 + count(//article/descendant-or-self::div[@class='rating'][1]/span[contains(@class,'four-star') and not(//meta[@itemprop='ratingValue'])])*4 + count(//article/descendant-or-self::div[@class='rating'][1]/span[contains(@class,'four-half-star') and not(//meta[@itemprop='ratingValue'])])*4.5 + count(//article/descendant-or-self::div[@class='rating'][1]/span[contains(@class,'five-star') and not(//meta[@itemprop='ratingValue'])])*5),'0',''))),'NaN','')",
            "TestDateText":"//meta[@name='date']/@content",
            "TestPros":"//div[contains(@class,'pros')]/ul/li//text()",
            "TestCons":"//div[contains(@class,'cons')]/ul/li//text()",
            "TestSummary":"//meta[@name='description']/@content",
            "TestVerdict":"//div[@itemprop='reviewBody']/descendant-or-self::*[(name()='h2' or name()='h3' or name()='h4') and ./following-sibling::p[string-length(normalize-space())>1]][last()]/following-sibling::p[string-length(normalize-space())>1 and not(//ul[@class='aag-list']//div[@class='expanded-content']/p)][1]//text() | //ul[@class='aag-list']//div[@class='expanded-content']/p//text()",
            "Author":"//div/descendant-or-self::*[(name()='a' and @rel='author') or ((name()='p' or name()='span') and @itemprop='author')][1]/span//text()",
            "TestTitle":"//meta[@property='og:title']/@content",
        }
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        review['TestUrl'] = original_url
        try:
            review['ProductName'] = product['ProductName']
            review['source_internal_id'] = product['source_internal_id']
        except:
            pass
        awpic_link = review.get("AwardPic", "")
        if awpic_link and awpic_link[:2] == "//":
            review["AwardPic"] = "https:" + review["AwardPic"]
        if awpic_link and awpic_link[:1] == "/":
            review["AwardPic"] = get_full_url(original_url, awpic_link)

        review["DBaseCategoryName"] = "PRO"
        review["SourceTestScale"] = "5"
                                    
        matches = None
        field_value = product.get("source_internal_id", "")
        if field_value:
            matches = re.search("((?<=\/article\/)\d*(?=\/))", field_value, re.IGNORECASE)
        if matches:
            product["source_internal_id"] = matches.group(1)

        matches = None
        field_value = review.get("source_internal_id", "")
        if field_value:
            matches = re.search("((?<=\/article\/)\d*(?=\/))", field_value, re.IGNORECASE)
        if matches:
            review["source_internal_id"] = matches.group(1)
                                    
        in_another_page_xpath = "//section[@class='pagination']/span[@class='page-numbers']/a[last()]/@href"
        pros_xpath = "//div[contains(@class,'pros')]/ul/li//text()"
        cons_xpath = "//div[contains(@class,'cons')]/ul/li//text()"
        rating_xpath = ""
        award_xpath = ""
        award_pic_xpath = ""
        
        test_verdict_xpath_1 = '//div[@itemprop="reviewBody"]/descendant-or-self::*[(name()="h2" or name()="h3" or name()="h4") and ./following-sibling::p[string-length(normalize-space())>1]][last()]/following-sibling::p[string-length(normalize-space(./text()))>1 and not(//ul[@class="aag-list"]//div[@class="expanded-content"]/p)][1]//text() | //ul[@class="aag-list"]//div[@class="expanded-content"]/p//text()'
        
        review["TestVerdict"] = None
        in_another_page_url = None
        if in_another_page_xpath:
            in_another_page_url = self.extract(response.xpath(in_another_page_xpath))
        if in_another_page_url:
            in_another_page_url = get_full_url(response, in_another_page_url)
            request = Request(in_another_page_url, callback=self.parse_fields_page)
            request.meta['review'] = review
            
            request.meta['test_verdict_xpath_1'] = test_verdict_xpath_1
            
            request.meta['pros_xpath'] = pros_xpath
            request.meta['cons_xpath'] = cons_xpath
            request.meta['rating_xpath'] = rating_xpath
            request.meta['award_xpath'] = award_xpath
            request.meta['award_pic_xpath'] = award_pic_xpath
            yield request
        else:
            
            if not review["TestVerdict"]:
                review["TestVerdict"] = self.extract(response.xpath(test_verdict_xpath_1))
            
            yield review

        yield product

    
    def parse_fields_page(self, response):
        review = response.meta['review']
        
        test_verdict_xpath_1 = response.meta['test_verdict_xpath_1']
        
        
        if not review["TestVerdict"]:
            review["TestVerdict"] = self.extract(response.xpath(test_verdict_xpath_1))
        
        pros_xpath = response.meta['pros_xpath']
        cons_xpath = response.meta['cons_xpath']
        rating_xpath = response.meta['rating_xpath']
        award_xpath = response.meta['award_xpath']
        award_pic_xpath = response.meta['award_pic_xpath']
        if pros_xpath:
            review["TestPros"] = self.extract_all(response.xpath(pros_xpath), ' ; ')
        if cons_xpath:
            review["TestCons"] = self.extract_all(response.xpath(cons_xpath), ' ; ')
        if rating_xpath:
            review['SourceTestRating'] = self.extract(response.xpath(rating_xpath), '%')
        if award_xpath:
            review['award'] = self.extract(response.xpath(award_xpath))
        if award_pic_xpath:
            review['AwardPic'] = self.extract(response.xpath(award_pic_xpath))
        yield review
