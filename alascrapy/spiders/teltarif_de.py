# -*- coding: utf8 -*-
import re

from scrapy.http import Request

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format
from alascrapy.items import CategoryItem


class Teltarif_deSpider(AlaSpider):
    name = 'teltarif_de'
    allowed_domains = ['teltarif.de']
    start_urls = ['http://www.teltarif.de/handy/test.html']

    
    def parse(self, response):
                                     
        original_url = response.url
        
        url_xpath = "//a[img[@alt='vor']]/@href"
        single_url = self.extract(response.xpath(url_xpath))
        if single_url:
            matches = None
            if "":
                matches = re.search("", single_url, re.IGNORECASE)
            if matches:
                single_url = matches.group(0)
            single_url = get_full_url(original_url, single_url)
            
            request = Request(single_url, callback=self.parse)
            
            yield request
        urls_xpath = "//li[contains(@class, 'ttboxpad')]//a[contains(@class, 'extra')]/@href"
        urls = self.extract_list(response.xpath(urls_xpath))
        for single_url in urls:
            matches = None
            if "":
                matches = re.search("", single_url, re.IGNORECASE)
            if matches:
                single_url = matches.group(0)
            single_url = get_full_url(original_url, single_url)
            
            request = Request(single_url, callback=self.level_2)
             
            yield request
    
    def level_2(self, response):
                                     
        original_url = response.url
        
        category_leaf_xpath = "//div[@id='breadcrumb']//span[last()]//a//text()"
        category_path_xpath = "//div[@id='breadcrumb']//a//text()"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category

        product_xpaths = { 
                
                
                
                
                "PicURL":"//meta[@property='og:image']/@content",
                
                
                            }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['TestUrl'] = original_url
        try:
            product["OriginalCategoryName"] = category['category_path']
        except:
            pass
        review_xpaths = { 
                
                
                
                
                "TestDateText":"//span[@class='dateNews']/time/text()",
                
                
                
                
                "TestSummary":"//div[@class='abstract']//text()",
                
                
                
                "Author":"//span[@itemprop='author']/a/text()",
                
                
                "TestTitle":"//h1[@itemprop='name']/text()",
                
                
                
                            }
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        review['TestUrl'] = original_url
        try:
            review['ProductName'] = product['ProductName']
            review['source_internal_id'] = product['source_internal_id']
        except:
            pass
        if review and review['TestTitle']:
            title = review["TestTitle"].lower()
            if ":" in title:
                all_title_parts = title.split(":")
                for part in all_title_parts:
                    review["ProductName"] = part.replace("review", "") if 'review' in part else title.replace("review", "")
            else:
                review["ProductName"] = title.replace("review", "")
            
            review["ProductName"] = review["ProductName"].strip("-: ")
            product["ProductName"] = review["ProductName"]

        review["DBaseCategoryName"] = "PRO"
                                    

        if review["TestDateText"]:
            
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(review["TestDateText"], "%d.%m.%Y %H:%M", ["en"])
                                    

        review["SourceTestScale"] = "5"
                                    
        in_another_page_xpath = "//a[img[@alt='letzte']]/@href"
        pros_xpath = "//ul[@class='ttProConUL Pro']/li//text()"
        cons_xpath = "//ul[@class='ttProConUL Contra']/li//text()"
        rating_xpath = ""
        award_xpath = ""
        award_pic_xpath = ""
        
        test_verdict_xpath_1 = '//*[@class="shl"][contains(text(), "Fazit:")]//following-sibling::div[@class="ttsbox"][1]/following::text()[1]'
        
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
