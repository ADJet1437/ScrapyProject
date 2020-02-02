# -*- coding: utf8 -*-
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider


class CnetDeSpider(AlaSpider):
    name = 'cnet_de'
    allowed_domains = ['cnet.de']
    start_urls = [
        'http://www.cnet.de/kategorie/tests/']

    def parse(self, response):
        title_xpath = response.xpath('//h2/a/text()')
        names_xpath = response.xpath('//span[@class="byline"]/text()')
        links_xpath = response.xpath('//h2/a/@href')
        titles = self.extract_list(title_xpath)
        names = self.extract_list(names_xpath)
        links = self.extract_list(links_xpath)

        for review_title, name, link in zip(titles, names, links):
            title = review_title
            product_name = title.replace('Test', '').strip()
            # the constant signifies the striping of the unwanted characters
            # in the names
            JUSTFULLNAME = 8
            author = name[JUSTFULLNAME:]
            yield response.follow(link, callback=self.parse_page,
                                  meta={'Author': author, 'Title': title,
                                        'Product_name': product_name})
        # next page
        next_page = self.extract(response.xpath('//li[@class="next"]/a/@href'))
        if next_page:
            yield response.follow(next_page)

    def parse_page(self, response):
        product_xpaths = {'PicURL': '//meta[@property="og:image"]/@content'}

        review_xpaths = {'TestSummary':
                         '//meta[@property ="og:description"]/@content',
                         'SourceTestRating': '//div[@class="score"]/text()',
                         'TestDateText': 'substring-before'
                         '(//meta[@property="article:published_time"]/'
                         '@content, "T")',
                         'SourceTestRating': '//div[@class="score"]/text()',
                         'TestPros': '//ul[@class="prolist"]/li/text() | '
                         '//h2[contains(text(),"PRO")]/ancestor::thead/'
                         'following-sibling::tbody/tr/td[1]/text()',
                         'TestCons': '//ul[@class="conlist"]/li/text() | '
                         '//h2[contains(text(),"CON")]/ancestor::thead/'
                         'following-sibling::tbody/tr/td[2]/text()',
                         'TestVerdict': '//h2[contains(.,"Fazit")]/'
                         'following-sibling::p[1]/text() |'
                         '//div[@class="fazit"]/p/text()'
                         }

        product = self.init_item_by_xpaths(response, 'product', product_xpaths)
        review = self.init_item_by_xpaths(response, 'review', review_xpaths)

        title = response.meta.get('Title')
        product_name = response.meta.get('Product_name')
        s_id = self.extract(response.xpath('//article/@id'))
        # removes the first five characters
        FIFTHCHAR = 5
        source_internal_id = s_id[FIFTHCHAR:]
        ocn_xpath = '//meta[@property="article:tag"]/@content'
        ocn = self.extract_all(response.xpath(ocn_xpath), ' | ')
        original_category_name = ocn.replace('Tests', '').strip()
        # populating the product item
        product['source_internal_id'] = source_internal_id
        product['ProductName'] = product_name
        product['OriginalCategoryName'] = original_category_name

        yield product

        test_scale = 10
        author = response.meta.get('Author')

        review['DBaseCategoryName'] = 'PRO'
        review['SourceTestScale'] = test_scale
        review['ProductName'] = product_name
        review["source_internal_id"] = source_internal_id
        review['Author'] = author
        review['TestTitle'] = title

        yield review
