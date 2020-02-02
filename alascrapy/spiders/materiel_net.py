__author__ = 'jim'

from scrapy.http import Request

from alascrapy.items import ProductItem, CategoryItem, ReviewItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url, date_format


class MaterielNetSpider(AlaSpider):
    name = 'materiel_net'
    allowed_domains = ['materiel.net']
    start_urls = ['http://www.materiel.net/plan-du-site.html']

    def parse(self, response):
        category_urls = self.extract_list(response.xpath('//div[@id="categories"]/div/ul/li/a/@href'))

        for category_url in category_urls:
            category_url = get_full_url(response, category_url)
            yield Request(url=category_url, callback=self.parse_category)

    def parse_category(self, response):
        sub_category_urls = self.extract_list(response.xpath(
            '//ul[not(descendant::a[@class="CatListSubItemHL"])]/li[@class="subSousMenu"]/a/@href'))
        for sub_category_url in sub_category_urls:
            yield Request(url=get_full_url(response, sub_category_url), callback=self.parse_category)

        if sub_category_urls:
            return

        category = CategoryItem()
        category['category_path'] = self.extract_all(response.xpath('//div[@class="cheminCat"]//text()'))
        category['category_leaf'] = self.extract(response.xpath('//div[@class="cheminCat"]/text()[last()]'))
        category['category_url'] = response.url
        yield category

        if not self.should_skip_category(category):
            category_id = self.extract(response.xpath('//input[@id="category"]/@value'))
            sorted_url = 'http://www.materiel.net/request/ProdList.php?ref=%s&n=-1' % category_id
            request = Request(url=sorted_url, callback=self.parse_products)
            request.meta['category'] = category
            yield request

    def parse_products(self, response):
        product_urls = self.extract_list(response.xpath('//div[@itemprop="review"]/preceding-sibling::a/@href'))

        for product_url in product_urls:
            request = Request(url=get_full_url(response, product_url), callback=self.parse_product)
            request.meta['category'] = response.meta['category']
            yield request

    def parse_product(self, response):
        product = ProductItem()

        product['TestUrl'] = response.url
        product['OriginalCategoryName'] = response.meta['category']['category_path']
        product['ProductName'] = self.extract_all(response.xpath('//h1//span[not(contains(@*,"category"))]/text()'))
        pic_url = self.extract(response.xpath('//div[@itemprop="image"]/img/@src'))
        if not pic_url:
            pic_url = self.extract(response.xpath('//div[@class="conteneurImage"]/img/@src'))
        product['PicURL'] = get_full_url(response, pic_url)
        product['ProductManufacturer'] = self.extract(response.xpath('//h1//span[(contains(@*,"brand"))]/text()'))
        yield product

        reviews = response.xpath('//table[contains(@class,"ProdCom")]')
       
        for review in reviews:
            user_review = ReviewItem()
            user_review['DBaseCategoryName'] = "USER"
            user_review['ProductName'] = product['ProductName']
            user_review['TestUrl'] = product['TestUrl']
            date = self.extract(review.xpath('.//div[@style]/text()'))
            date_list = date.split(',')
            user_review['TestDateText'] = date_format(date_list[1].strip('le '), '%d/%m/%Y')
            rate = self.extract(review.xpath('.//img[contains(@src,"NoteSmall")]/@src'))
            user_review['SourceTestRating'] = rate.split('NoteSmall')[1].split('.')[0]
            user_review['Author'] = date_list[0]
            user_review['TestTitle'] = self.extract(review.xpath('.//div[@class="ProdComTitle"]/text()'))
            user_review['TestSummary'] = self.extract_all(review.xpath('.//tr[2]/td//text()'))
            yield user_review
