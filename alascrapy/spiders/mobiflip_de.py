# -*- coding: utf-8 -*-

from datetime import datetime


from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils


class Mobiflip_deSpider(AlaSpider):
    name = 'mobiflip_de'
    allowed_domains = ['mobiflip.de']
    start_urls = ['https://www.mobiflip.de/thema/testberichte']

    def __init__(self, *args, **kwargs):
        super(Mobiflip_deSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

        if not self.stored_last_date:
            self.stored_last_date = datetime(1970, 1, 1)


    
    def parse(self, response):
        review_divs_xpath = '//li[@class="infinite-post"]'
        review_divs = response.xpath(review_divs_xpath)

        for review_div in review_divs:
            review_urls_xpath = './/div/a/@href'

            review_url = review_div.xpath(review_urls_xpath).get()

            yield response.follow(url=review_url,
                            callback=self.parse_page)
        

        # next page
        next_page_xpath = '//div[@class="nav-links-home"]/a/@href'
        next_page = self.extract(response.xpath(next_page_xpath))

        if next_page:

            last_review_date_xpath = 'substring-before(//li[@class="infinite-post"]'\
                                     '[last()]/div/span/text(), " | ")'
            last_date = response.xpath(last_review_date_xpath).get()
            last_date = last_date.replace('.', '/')
            last_date = datetime.strptime(last_date, "%d/%m/%y")

            if last_date > self.stored_last_date:
                yield response.follow(next_page, callback=self.parse)
    
    def parse_page(self, response):
       
        product_xpaths = { 
                # 'ProductName': '//header/h1/text()',
                'OriginalCategoryName': '//div[@class="breadcrumbbox"]//span[@itemprop="title"]//text()',
                
                
                'PicURL': '//meta[@property="og:image"]/@content',
                'TestUrl': '//meta[@property="og:url"]/@content'
                
                
                            }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
       
        review_xpaths = { 
                'TestDateText': 'substring-before(//meta[@property="article:published_time"]/@content, "T")',
                
                'TestSummary': '//meta[@property="og:description"]/@content',
                "TestVerdict":"//h2[contains(.//text(),'Fazit')]/following::p[string-length(.//text())>2][1]//text()",
                'Author': '//span[contains(@class,"author-name")]//text()',
                'TestTitle': '//meta[@property="og:title"]/@content',
                'TestUrl': '//meta[@property="og:url"]/@content',
                            }
        review = self.init_item_by_xpaths(response, "review", review_xpaths)

        pname_xpath = '//header/h1/text()'
        pname = self.extract(response.xpath(pname_xpath))

        if ':' in pname:
            review['ProductName'] = pname.split(':')[0]
            product['ProductName'] = pname.split(':')[0]
        
        else:
            review['ProductName'] = pname
            product['ProductName'] = pname

        pname = review['ProductName']

        if 'im Test' in pname:
            review['ProductName'] = pname.split(' im')[0]
            product['ProductName'] = pname.split(' im')[0]
        
        else:
            review['ProductName'] = pname
            product['ProductName'] = pname

        src_int_id_xpath = 'substring-after(//link[@rel="shortlink"]/@href, "=")'
        src_int_id = self.extract(response.xpath(src_int_id_xpath))
        review['source_internal_id'] = src_int_id
        product['source_internal_id'] = src_int_id


        yield product
        review['DBaseCategoryName'] = 'PRO'
                                     
        yield review
        
