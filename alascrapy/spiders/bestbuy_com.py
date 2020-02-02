import re

from scrapy.http import Request

from alascrapy.items import ProductItem, ReviewItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.lib.generic import get_full_url


class BestbuyComSpider(AlaSpider):
    name = 'bestbuy_com'
    allowed_domains = ['bestbuy.com', 'bestbuy.ugc.bazaarvoice.com']
    start_urls = ['http://www.bestbuy.com/site/home-appliances/refrigerators/abcat0901000.c?id=abcat0901000']

    def parse(self, response):

        category_urls = self.extract_list(response.xpath(
            "//div[@class='sub-cat-links']//div[@class='column-wrap']//ul/li/a/@href"))
        for category_url in category_urls:
            yield Request(url=category_url, callback=self.parse_category)

    def parse_category(self, response):

        category_xpath = "//div[@class='hierarchy']/ul/li/a[contains(@data-track, 'All')]/@href"
        category_url = self.extract(response.xpath(category_xpath))
        if category_url:
            category_url = get_full_url(response,category_url)
            yield Request(url=get_full_url(response,category_url), callback=self.parse_category)
        else:
            product_list_xpath = "//div[@class='list-page']//div[@class='list-items']/div[@class='list-item']/@data-url"

            next_page_xpath = "//li[@class='pager-next']/a/@href"
            product_urls = self.extract_list(response.xpath(product_list_xpath))

            for product_url in product_urls:
                product_url = get_full_url(response, product_url)
                yield Request(url=product_url, callback=self.parse_product)

            next_page = self.extract(response.xpath(next_page_xpath))
            if(next_page):
                request = Request(url=get_full_url(response, next_page), callback=self.parse_category)
                #yield request


    def parse_product(self, response):
        product = ProductItem()
        print response.url
        product['TestUrl'] = response.url
        product['OriginalCategoryName'] = self.extract_all(response.xpath('//ol[@id="breadcrumb-list"]/li/a/text()'), "->")
        product['ProductName'] = self.extract(response.xpath('//div[@class="type-subhead-alt-regular"]//text()'))
        product['PicURL'] = self.extract(response.xpath('//div[@data-slide-number="0"]/div[@class="zoomable hammer-wrapper"]/img/@data-img-path'))
        product['ProductManufacturer'] = self.extract(response.xpath('//meta[@id="schemaorg-brand-name"]/@content'))
        product['source_internal_id'] = self.extract(response.xpath('//span[@id="sku-value" and @itemprop="productID"]/text()'))
        yield product
      
        request = Request(url="http://bestbuy.ugc.bazaarvoice.com/3545w/" + product['source_internal_id'] + "/reviews.djs?format=embeddedhtml", callback=self.parse_review)
        request.meta['product'] = product
        yield request

    def parse_review(self, response):

        product = response.meta['product']

        doc = response.body.replace("\\", "")

        reviewList_pattern = 'BVRRReviewRatingsContainer(.*)(?=BVRRAdditionalFieldsContainer)'

        m = re.search(reviewList_pattern, doc)
        if(m):
            reviewListContent = m.group(0)
        else:
            return

        reviewSplit_pattern = 'BVRRAdditionalFieldsContainer'

        reviewList = re.split(reviewSplit_pattern, reviewListContent)

        testTitle_pattern = '(?<=BVRRReviewTitle">).*?(?=(</span><span class="BVRRLabel BVRRReviewTitleSuffix"))'
        testSummary_pattern = '(?<=class="BVRRReviewText">).*?(?=<)'
        testRating_pattern = '(?<="BVImgOrSprite" alt=").*?(?= out of 5" title)'
        testAuthor_pattern = '(?<=class="BVRRNickname">).*?(?=( </span))'
        testDate_pattern = '(?<=dtreviewed" content=").*?(?=" class="BVRRValue BVRRReviewDate")'

        for reviewString in reviewList:
            review = ReviewItem()
            review['DBaseCategoryName'] = "USER"
            review['ProductName'] = product['ProductName']
            review['TestUrl'] = product['TestUrl']
            review['source_internal_id'] = product['source_internal_id']
            rating = re.search(testRating_pattern, reviewString)
            if rating is not None:
                review['SourceTestRating'] = rating.group(0)
            author = re.search(testAuthor_pattern, reviewString)
            if author is not None:
                review['Author'] = author.group(0)
            title = re.search(testTitle_pattern, reviewString)
            if title is not None:
                review['TestTitle'] = title.group(0)
            summary = re.search(testSummary_pattern, reviewString)
            if summary is not None:
                review['TestSummary'] = summary.group(0)
            date = re.search(testDate_pattern, reviewString)
            if date is not None:
                review['TestDateText'] = date.group(0)
            yield review

        nextpage_pattern = '(?<=("BVRRPageLink BVRRNextPage"><a data-bvjsref=")).*(?=(" data-bvcfg="__CONFIGKEY__"))'
        next_page = re.search(nextpage_pattern, doc)

        if next_page is not None:
            nextpageUrl = next_page.group(0).replace('amp;', '')
            print nextpageUrl
            request = Request(url=nextpageUrl, callback=self.parse_review)
            request.meta['product'] = product
            yield request



