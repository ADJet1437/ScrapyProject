__author__ = 'jim'

from scrapy.http import Request

from alascrapy.items import ProductItem, ReviewItem, CategoryItem, ProductIdItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import date_format, get_full_url
from alascrapy.lib.selenium_browser import SeleniumBrowser


class BesteproductNlSpider(AlaSpider):
    name = 'besteproduct_nl'
    allowed_domains = ['besteproduct.nl']
    start_urls = ['http://www.besteproduct.nl/']
    custom_settings = {'MAX_SELENIUM_REQUESTS': 3}
    
    def parse(self, response):
        with SeleniumBrowser(self, response) as browser:
            selector = browser.get(response.url)

            category_path = selector.xpath('//ul[contains(@class, "grouplist__group")]')
            for categories in category_path:
                path = self.extract(categories.xpath('./li[@class="grouplist__group__title"]/text()'))
                leaves = categories.xpath('./li[@class="grouplist__group__item"]')
                for leaf in leaves:
                    category = CategoryItem()
                    category['category_leaf'] = self.extract(leaf.xpath('.//text()'))
                    category['category_path'] = 'Home > ' + path + ' > ' + category['category_leaf']
                    category['category_url'] = get_full_url(response.url, self.extract(leaf.xpath('./a/@href')))
                    yield category

                try:
                    for item in self.parse_categories(browser, category['category_url'], category):
                        yield item
                except:
                    pass
            
    def parse_categories(self, browser, url, category):
        selector = browser.get(url)
                  
        if not self.should_skip_category(category):
            products = selector.xpath('//div[contains(@class, "productscore__item")]')
            for product in products:
                pro_review_count = self.extract(product.xpath('.//div[@class="rankingratingline-title"][contains(text(), "experts")]/text()'))
                user_review_count = self.extract(product.xpath('.//div[@class="rankingratingline-title"][contains(text(), "gebruikers")]/text()'))
                if '(0)' in pro_review_count and '(0)' in user_review_count:
                    continue
                product_url = self.extract(product.xpath('.//a[@class="link--title"]/@href'))
                product_url = get_full_url(url, product_url)
                product_name = self.extract(product.xpath('.//a[@class="link--title"]//text()'))
                product_ocn = category['category_path']
                request = Request(url=product_url, callback=self.parse_pro)
                request.meta['item'] = {'name': product_name, 'ocn': product_ocn, 'url': product_url,
                                        'has_review': 0}
                yield request
                    
            product_num = int(self.extract(selector.xpath('//span[@class="js-product-count"]/text()')))
            if product_num > 30:
                pages = product_num / 30
                for page in range(2, pages+1, 1):
                    url = category['category_url']+'#priceMin=&priceMax=&sort=6&page='+str(page)
                    for item in self.parse_categories(browser, url, category):
                        yield item

    def parse_pro(self, response):
        item = response.meta['item']
        pro_review = response.xpath('//div[@id="besteproducttest"]')

        rate_xpath = './/div[@class="block"]/div[contains(@class,"bp-review__intro__score")]//text()'

        if pro_review:
            item['has_review'] = 1
            review = ReviewItem()
            review['DBaseCategoryName'] = "PRO"
            review['ProductName'] = item['name']
            review['TestUrl'] = response.url
            date = self.extract(pro_review.xpath('.//@datetime'))
            review['TestDateText'] = date_format(date, '')
            review['SourceTestRating'] = self.extract(pro_review.xpath(rate_xpath)).replace(",", ".")
            review['Author'] = self.extract(pro_review.xpath('.//div[@class="avatar__title"]/text()'))
            review['TestTitle'] = self.extract(pro_review.xpath('.//h1/text()'))
            review['TestSummary'] = self.extract_all(pro_review.xpath('.//p/text()'))
            yield review
            
        request = Request(url=item['url']+'/gebruikersreviews', callback=self.parse_user)
        request.meta['item'] = item
        yield request
                
    def parse_user(self, response):
        item = response.meta['item']

        reviews_xpath = '//div[contains(@itemtype, "Product")]//div[contains(@class, "row")]' \
                        '/div[contains(@class, "col9")]/parent::div'
        reviews = response.xpath(reviews_xpath)

        rate_xpath = './/div[contains(@class,"badge-rating")]//text()'
        pros_xpath = './/span[contains(text(),"Sterke punten")]/following::text()[1]'
        cons_xpath = './/span[contains(text(),"Zwakke punten")]/following::text()[1]'

        for review in reviews:
            internal_review = review.xpath('.//div[contains(@class, "btn-secondary")][contains(text(), "BesteProduct.nl")]')
            if internal_review:
                item['has_review'] = 1
                user_review = ReviewItem()
                user_review['DBaseCategoryName'] = "USER"
                user_review['ProductName'] = item['name']
                user_review['TestUrl'] = response.url
                date = self.extract(review.xpath('.//span[@class="right"]/text()'))
                user_review['TestDateText'] = date_format(date, "%d-%m-%Y")
                user_review['SourceTestRating'] = self.extract(review.xpath(rate_xpath))
                user_review['Author'] = self.extract(review.xpath('.//div[contains(@class,"left")]//text()'))
                user_review['TestTitle'] = self.extract(review.xpath('.//div[contains(@class,"title--s")]//text()'))
                user_review['TestSummary'] = self.extract_all(review.xpath('.//p[1]/text()'))
                user_review['TestPros'] = self.extract(review.xpath(pros_xpath))
                user_review['TestCons'] = self.extract(review.xpath(cons_xpath))
                yield user_review

        if item['has_review']:
            request = Request(url=item['url']+'/specificaties', callback=self.parse_product)
            request.meta['item'] = item
            yield request
        
    def parse_product(self, response):
        item = response.meta['item']
        
        product = ProductItem()
        product['TestUrl'] = response.url
        product['OriginalCategoryName'] = item['ocn']
        product['ProductName'] = item['name']
        product['PicURL'] = get_full_url(response.url, self.extract(response.xpath('//img[@itemprop="image"]/@src')))
        product["ProductManufacturer"] = self.extract(response.xpath('//span[@itemprop="brand"]/text()'))
        yield product

        mpn_id_xpath = '//div[text()="Partnumber"]/parent::div/div[contains(@class,"value")]/text()'
        ean_id_xpath = '//div[text()="EAN"]/parent::div/div[contains(@class,"value")]/text()'
        mpn_id = self.extract(response.xpath(mpn_id_xpath))
        ean_id = self.extract(response.xpath(ean_id_xpath))

        if mpn_id.strip() > '-':
            mpn = ProductIdItem()
            mpn['ProductName'] = item['name']
            mpn['ID_kind'] = "MPN"
            mpn['ID_value'] = mpn_id
            yield mpn

        if ean_id.strip() > '-':
            ean = ProductIdItem()
            ean['ProductName'] = item['name']
            ean['ID_kind'] = "EAN"
            ean['ID_value'] = ean_id
            yield ean
