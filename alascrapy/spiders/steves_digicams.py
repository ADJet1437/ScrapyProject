import re
from alascrapy.lib.generic import date_format
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider


class StevesDigicamsSpider(AlaSpider):
    name = 'steves_digicams'
    allowed_domains = ['steves-digicams.com']
    start_urls = ['http://www.steves-digicams.com/camera-reviews/']

    def parse(self, response):
        next_page_xpath = "//a[@class='right']/@href"
        review_urls_xpath = "//div[@data-title= 'Name']/span/a/@href"
        review_urls = self.extract_list(response.xpath(review_urls_xpath))

        for review_url in review_urls:
            yield response.follow(review_url, callback=self.parse_review)

        next_page = self.extract(response.xpath(next_page_xpath))
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_review(self, response):
            product_xpaths = {"PicURL": "(//span/a/img/@src)[1]"
                              }

            review_xpaths = {"TestTitle": "//div[@class='text-entry']/h2/text()",
                             "Author": "//a[@rel='author']/text()",
                             "TestPros": "(//strong[contains(text(),'Pros')]/ancestor::"
                                         "tr/following-sibling::tr/td/ul)[1]/li/text()",
                             "TestCons": "(//strong[contains(text(),'Pros')]/ancestor::"
                                         "tr/following-sibling::tr/td/ul)[2]/li/text()"
                             }
            product = self.init_item_by_xpaths(response, "product", product_xpaths)
            review = self.init_item_by_xpaths(response, "review", review_xpaths)

            try:
                title = self.extract(response.xpath("//div[@class='text-entry']/h1/text()"))
                if title:
                    product_name = title.replace('Review', '').replace('review', '').strip()
                product["ProductName"] = product_name

                original_category_name_xpath = "//td/ul[@class='breadcrumbs']/li/a/text()"
                original_category_name = self.extract_all(response.xpath(original_category_name_xpath), " | ")
                if original_category_name:
                    product["OriginalCategoryName"] = original_category_name

                yield product
                
                test_date_xpath = self.extract(response.xpath("//div[@class='entry-body']"))
                if test_date_xpath:
                    test_date_regex = re.findall(r'(\d{2})[/.-](\d{2})[/.-](\d{4})',test_date_xpath)
                    test_date = ''.join(str(e) for e in test_date_regex)
                    test_date_ = re.sub("[()'u]", '', test_date)
                    test_date_text = test_date_.replace(" ","").replace(",","-")
                    review["TestDateText"] = date_format(test_date_text, "%d %b %Y")

                test_summary = self.extract(response.xpath("//div[@class='entry-body']/div[2]/text()"))
                if test_summary:
                    review["TestSummary"] = test_summary
                review["DBaseCategoryName"] = "PRO"
                review["ProductName"] = product_name

                test_verdict_xpath = "//div/strong[contains(text(),'Bottom Line')]/ancestor::" \
                                     "tr/following-sibling::tr/td/text()"
                test_verdict = self.extract(response.xpath(test_verdict_xpath)).strip('Read more in our .')
                if test_verdict:
                    review["TestVerdict"] = test_verdict
                yield review
            except:
                pass

