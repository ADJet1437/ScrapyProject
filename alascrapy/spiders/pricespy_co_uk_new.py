
import re
from scrapy.http import Request

from alascrapy.spiders.base_spiders import ala_spider as spiders
from alascrapy.items import ProductItem, CategoryItem, ProductIdItem
from alascrapy.lib.generic import get_full_url

class Pricespy_co_ukSpider(spiders.AlaSpider):
    
    name = 'pricespy_co_uk'
    allowed_domains = ['pricespy.co.uk']
    start_urls = ['https://pricespy.co.uk/audio-video/speakers-headphones/headphones--c148?filterId=s327294932',
                    'https://pricespy.co.uk/phones-gps/mobile-phones--c103?filterId=s327294930',
                    'https://pricespy.co.uk/camera-photo/digital-compact-cameras--c97?filterId=s327294924',
                    'https://pricespy.co.uk/computers-accessories/tablets--c1594?filterId=s327294920',
                    'https://pricespy.co.uk/phones-gps/wearables/smartwatches--c1808?filterId=s328231870']

    def parse(self, response):

        category = CategoryItem()
        category_path = self.extract_all(response.xpath("//div[@class='Breadcrumbs-sc-11q7umm-0 dsQddb']//text()"), " > ")
        category['category_leaf'] = self.extract(response.xpath('//h1/text()'))
        category['category_path'] = category_path + ' > ' + category['category_leaf']
        category['category_url'] = response.url
        yield category

        for product_urls in response.xpath("//div[@class='Card-sc-882dpj-0 iIDAAR']/a/@href").extract():                   
            product_url = get_full_url(response, product_urls)
            request = Request(url=product_url, callback=self.parse_product)
            yield request

        next_page_url = self.extract(response.xpath("//div[@class='pj-ui-pagination--paging']/a/@href"))
        if next_page_url:
            next_page_url = get_full_url(response, next_page_url)
            request = Request(url=next_page_url, callback=self.parse)
            yield request
        
    def parse_product(self, response):

        product = ProductItem()

        product['TestUrl'] = response.url
        product['OriginalCategoryName'] = self.extract(response.xpath("(//div[@class='Breadcrumbs-sc-11q7umm-0 dsQddb']//text())[last()]"))
        product['ProductName'] = self.extract(response.xpath('//h1/text()'))
        product['PicURL'] = self.extract(response.xpath('//meta[@property="og:image"]/@content'))
        product['ProductManufacturer'] = self.extract(response.xpath("//div[@class='RelatedPage-sc-1i89wok-8 ZlMGA']/a/text()"))
        product['source_internal_id'] = str(self.extract(response.xpath("(//link[@data-route-id='initial']/@href)[1]"))).split("--p")[1]
        yield product

        product_id = ProductIdItem()
        product_id['source_internal_id'] = product['source_internal_id']
        product_id['ProductName'] = product["ProductName"]
        product_id['ID_kind'] = "prisjakt_id"
        product_id['ID_value'] = product["source_internal_id"]
        yield product_id

        hdd_xpath = "//tr[@class='TableRow-sc-41ik9-2 dBYNIg'][4]/td/text()"
        size_internal_hdd = self.extract(response.xpath(hdd_xpath))
        if size_internal_hdd:
            product_id = ProductIdItem()
            product_id['source_internal_id'] = product["source_internal_id"]
            product_id['ProductName'] = product["ProductName"]
            product_id['ID_kind'] = "size_internal_hdd"
            product_id['ID_value'] = size_internal_hdd
            yield product_id

        date_xpath = "//tr[@class='TableRow-sc-41ik9-2 dBYNIg'][5]/td/text()" 
        date = self.extract(response.xpath(date_xpath))
        if date.isdigit():
            product_id = ProductIdItem()
            product_id['source_internal_id'] = product["source_internal_id"]
            product_id['ProductName'] = product["ProductName"]
            product_id['ID_kind'] = "first_publish_date"
            product_id['ID_value'] = date
            yield product_id
        else:
            date_xpath = "//tr[@class='TableRow-sc-41ik9-2 dBYNIg'][6]/td/text()" 
            date = self.extract(response.xpath(date_xpath))
            if date.isdigit():
                product_id = ProductIdItem()
                product_id['source_internal_id'] = product["source_internal_id"]
                product_id['ProductName'] = product["ProductName"]
                product_id['ID_kind'] = "first_publish_date"
                product_id['ID_value'] = date
                yield product_id
