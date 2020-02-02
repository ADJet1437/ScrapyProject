# -*- coding: utf8 -*-

import re
from bs4 import BeautifulSoup

from alascrapy.spiders.base_spiders.rm_spider import RMSpider
from alascrapy.lib.generic import date_format
from alascrapy.items import ProductItem, ReviewItem
from alascrapy.lib.selenium_browser import SeleniumBrowser, uses_selenium


class FnacRMSpider(RMSpider):
    name = 'fnac_com_rm'
    allowed_domains = ['fnac_com_rm']

    rating_re = re.compile("star S(\d)")
    date_re = re.compile(u"Posté le (.+)", re.UNICODE)

    @uses_selenium
    def parse(self, response):
        all_review_button_xpath = "//a[contains(@class,'seeAllReviews')]"
        soup = BeautifulSoup(response.body, "lxml")
        #inspect_response(response, self)
        item_id = response.url.split('/')[-2].strip()
        product = ProductItem()
        product['source_internal_id'] = item_id
        product['ProductName'] = soup.find('span', {'itemprop':'name'}).text.strip()
        product['ProductManufacturer'] = soup.find('span', {'itemprop':'manufacturer'}).text.strip()
        ocn = []	
        ocn_paths = soup.find('ul', {'class':'Breadcrumb-list'}).find_all('span', {'itemprop':'title'})
        for item in ocn_paths:
            ocn.append(item.text.strip())
        product['OriginalCategoryName'] = ' > '.join(ocn)
        product['PicURL'] = soup.find('img', {'class':'js-ProductVisuals-imagePreview'})['src'].strip()
        product['TestUrl'] = response.url
        yield product
        yield self.get_rm_kidval(product, response)

        with SeleniumBrowser(self, response) as browser:
            selector = browser.get(response.url)
            all_review_button = response.xpath(all_review_button_xpath)
            if all_review_button:
                selector = browser.click("//a[contains(@class,'seeAllReviews')]")
            for review in self._parse_reviews(selector, product, browser):
                yield review

    def _parse_reviews(self, selector, product, browser):
        review_container_xpath = "//div[@class='customerlistcomment']"

        author_xpath = ".//div[@class='customer-name']/a/text()"
        title_xpath = ".//div[@class='customer-text']/strong/text()"
        summary_xpath = ".//div[@class='customer-text']/p/text()"
        rating_xpath = ".//span[contains(@class, 'star S')]/@class"
        test_date_xpath = ".//div[@class='customer-detail']/p/text()"
        next_page_xpath = "//a[@title='Page suivante']"
        review_containers = selector.xpath(review_container_xpath)

        for review_container in review_containers:
            review = ReviewItem()
            review['DBaseCategoryName'] = "USER"
            review['ProductName'] = product['ProductName']
            review['source_internal_id'] = product['source_internal_id']
            review['TestUrl'] = product['TestUrl']
            review['Author'] = self.extract(review_container.xpath(author_xpath))
            review["TestTitle"] = self.extract(review_container.xpath(title_xpath))
            review["TestSummary"] = self.extract(review_container.xpath(summary_xpath))

            date_text = self.extract_all(review_container.xpath(test_date_xpath))
            date_match = re.search(self.date_re, date_text)
            if date_match:
                date_text = date_match.group(1)
                review["TestDateText"] = date_format(date_text, "%d %b %Y")

            rating_text = self.extract(review_container.xpath(rating_xpath))
            match = re.match(self.rating_re, rating_text)
            if match:
                review['SourceTestRating'] = match.group(1)
            yield review

        next_page = selector.xpath(next_page_xpath)
        if next_page:
            next_page_selector = browser.click(next_page_xpath)
            for review in self._parse_reviews(next_page_selector, product, browser):
                yield review
