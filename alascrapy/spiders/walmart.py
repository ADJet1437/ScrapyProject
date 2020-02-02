#!/usr/bin/env python

"""Walmart Spider: """

__author__ = 'carter'

from datetime import datetime
from bs4 import BeautifulSoup
from urlparse import urljoin

from scrapy.http import Request

from alascrapy.items import ProductItem, ProductIdItem, ReviewItem, CategoryItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.dao.incremental_scraping import get_latest_user_review_date_by_sii

reviews_link_pattern = 'https://www.walmart.com/reviews/product/%s?limit=20&page=%s&sort=submission-desc'

class WalmartSpider(AlaSpider):
    name = 'walmart'
    allowed_domains = ['walmart.com']
    start_urls = ['http://www.walmart.com/cp/3944']
    download_delay=2

    def parse(self, response):
        soup = BeautifulSoup(response.body, "lxml")
        all_categories = soup.find('div', {'class':'category-leftnav'}).find('div', {'data-zone':'zone3'}).find('div', {'class':'expander-content'}).find_all('li')
        for item in all_categories:
            link = item.find('a')['href']
            rlink = urljoin(response.url, link)
            request = Request(rlink, callback=self.parse_sub_categories)
            yield request

    def parse_sub_categories(self, response):
        soup = BeautifulSoup(response.body, "lxml")
        try:
            all_categories = soup.find('div', {'class':'category-leftnav'}).find('div', {'data-zone':'zone3'}).find('div', {'class':'expander-content'}).find_all('li')
            for item in all_categories:
                link = item.find('a')['href']
                rlink = urljoin(response.url, link)
                request = Request(rlink, callback=self.parse_product_list)
                yield request
        except:
            request = Request(response.url, callback=self.parse_product_list)
            yield request

    def parse_product_list(self, response):
        soup = BeautifulSoup(response.body, "lxml")

        category = response.meta.get('category', None)
        if not category:
            ocn = []
            ocn_paths = soup.find('ol', {'class':'breadcrumb-list'}).find_all('span', {'itemprop':'title'})
            for item in ocn_paths:
                ocn.append(item.text.strip())
            ocn_string = ' > '.join(ocn)
            category = CategoryItem()
            category['category_path'] = ocn_string
            category['category_leaf'] = ocn_string
            category['category_url'] = response.url
            yield category

        if self.should_skip_category(category):
            return

        units = soup.find('ul', {'class':'tile-list-grid'}).find_all('div', {'class':'tile-grid-unit'})
        for item in units:
            reviews_count = item.find('span', {'class':'stars-reviews'})
            if reviews_count:
                review_link = item.find('a', {'class':'js-product-image'})['href']
                rlink = urljoin(response.url, review_link)
                product_request = Request(rlink, callback=self.parse_product)
                product_request.meta['category'] = category
                #yield product_request

        next_page_btn =  soup.find('a', {'class':'paginator-btn-next'})
        if next_page_btn:
            nlink = urljoin(response.url, next_page_btn['href'])
            next_page_request = Request(nlink, callback=self.parse_product_list)
            next_page_request.meta['category'] = category
            #yield next_page_request

    def parse_product(self, response):
        category = response.meta['category']
        soup = BeautifulSoup(response.body, "lxml")
        item_id = response.url.split('/')[-1].strip()
        product = ProductItem()  
        product['source_internal_id'] = item_id
        product['ProductName'] = soup.find('h1', {'itemprop':'name'}).text.strip()
        product['ProductManufacturer'] = soup.find('a', {'id':'WMItemBrandLnk'}).text.strip() if soup.find('a', {'id':'WMItemBrandLnk'}) else ''

        product['OriginalCategoryName'] = category['category_path']
        product['PicURL'] = soup.find('img', {'class':'product-image'})['src'].strip()
        product['TestUrl'] = response.url
        yield product

        price = soup.find('div', {'itemprop':'price'})
        product_id = ProductIdItem()
        product_id['source_id'] = product['source_id']
        product_id['ProductName'] = product['ProductName']
        product_id['source_internal_id'] = product['source_internal_id']
        if price:
            try:
                product_id['ID_kind'] = 'price'
                product_id['ID_value'] = format(round(float(''.join(price.text.replace('$', ''))), 2), ".2f").replace('.', ',')
            except:
                pass
        yield product_id

        latest_review_date = get_latest_user_review_date_by_sii(self.mysql_manager,
                                                                self.spider_conf['source_id'],
                                                                item_id)

        review_page = 1
        reviews_link = reviews_link_pattern % (item_id, str(review_page))
        request = Request(reviews_link, callback=self.parse_review)
        request.meta['ProductName'] = product['ProductName']
        request.meta['item_id'] = item_id
        request.meta['review_page'] = review_page
        request.meta['latest_review_date'] = latest_review_date
        anchors = soup.find_all('a', {'class':'js-product-anchor'})
        for anchor in anchors:
            if 'reviews' in anchor.text:
                request.meta['max_idx'] = int(anchor.text.replace('reviews', '').strip())
                break
        yield request
    
    def parse_review(self, response):
        soup = BeautifulSoup(response.body, "lxml")
        pname = response.meta['ProductName']
        item_id = response.meta['item_id']
        review_page = response.meta['review_page']
        latest_review_date = response.meta['latest_review_date']
        review_body = soup.find('div', {'class':'customer-review-body'})
        if review_body == None:
            return

        reviews_blocks = soup.find_all('div', {'class':'customer-review-body'})
        for item in reviews_blocks:
            review = ReviewItem()
            review['ProductName'] = pname
            review['source_internal_id'] = item_id
            review['SourceTestRating'] = item.find('span', {'class':'visuallyhidden'}).text.replace('stars', '').strip()
            review['SourceTestScale'] = '5'
            timestamp = item.find('span', {'class':'customer-review-date'}).text.strip()
            review_date = datetime.strptime(timestamp, "%m/%d/%Y")
            review['TestDateText'] = review_date.strftime('%Y-%m-%d')
            review['TestSummary'] = item.find('p', {'class':'js-customer-review-text'}).text.strip()
            review['Author'] = item.find('span', {'class':'customer-name-heavy'}).text.strip()
            review['DBaseCategoryName'] = 'USER'
            review['TestTitle'] = item.find('div', {'class':'customer-review-title'}).text.strip()
            review['TestUrl'] = response.url
            yield review

        if latest_review_date > review_date:
            review_page += 1
            next_page_link = reviews_link_pattern % (item_id, str(review_page))
            request = Request(next_page_link, callback=self.parse_review)
            request.meta['ProductName'] = pname
            request.meta['item_id'] = item_id
            request.meta['review_page'] = review_page
            request.meta['latest_review_date'] = latest_review_date
            yield request
