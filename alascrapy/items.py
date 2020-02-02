# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CategoryItem(scrapy.Item):
    _name = "category"
    source_id = scrapy.Field()
    category_leaf = scrapy.Field()
    category_path = scrapy.Field()
    category_url = scrapy.Field()
    category_string = scrapy.Field()
    do_not_load = scrapy.Field()


class ProductItem(scrapy.Item):
    _name = "product"
    source_id = scrapy.Field()
    source_internal_id = scrapy.Field()
    ProductName = scrapy.Field()
    OriginalCategoryName = scrapy.Field()
    PicURL = scrapy.Field()
    ProductManufacturer = scrapy.Field()
    TestUrl = scrapy.Field()

    @classmethod
    def from_response(cls, response, category=None, product_name='',
                      source_internal_id='', url='', manufacturer='', pic_url=''):
        if url:
            product_url = url
        else:
            product_url = response.url

        original_category_name = ''
        if isinstance(category, CategoryItem):
            original_category_name = category["category_path"]
        elif isinstance(category, basestring) and category:
            original_category_name = category

        return cls(source_internal_id=source_internal_id, ProductName=product_name,
                   OriginalCategoryName=original_category_name, PicURL=pic_url,
                   ProductManufacturer=manufacturer, TestUrl=product_url)


class ReviewItem(scrapy.Item):
    _name = "review"
    source_id = scrapy.Field()
    source_internal_id = scrapy.Field()
    ProductName = scrapy.Field()
    SourceTestRating = scrapy.Field()
    SourceTestScale = scrapy.Field()
    TestDateText = scrapy.Field()
    TestPros = scrapy.Field()
    TestCons = scrapy.Field()
    TestSummary = scrapy.Field()
    TestVerdict = scrapy.Field()
    Author = scrapy.Field()
    DBaseCategoryName = scrapy.Field()
    TestTitle = scrapy.Field()
    TestUrl = scrapy.Field()
    Pay = scrapy.Field()
    award = scrapy.Field()
    AwardPic = scrapy.Field()
    countries = scrapy.Field()
    alltext = scrapy.Field()

    @classmethod
    def from_product(cls, product, tp='', rating='', scale='', date='', author='',
                     title='', summary='', verdict='', url='', pros='', cons='',
                     award='', award_pic=''):
        if not url:
            url = product.get('TestUrl', None)
        source_internal_id = product.get("source_internal_id", None)
        product_name = product.get("ProductName", None)

        return cls(source_internal_id=source_internal_id, ProductName=product_name,
                   SourceTestRating=rating, SourceTestScale=scale, TestDateText=date,
                   Author=author, DBaseCategoryName=tp, TestTitle=title,
                   TestSummary=summary, TestVerdict=verdict, TestUrl=url,
                   TestPros=pros, TestCons=cons, award=award, AwardPic=award_pic)


class ProductIdItem(scrapy.Item):
    _name = "product_id"
    source_id = scrapy.Field()
    source_internal_id = scrapy.Field()
    ProductName = scrapy.Field()
    ID_kind = scrapy.Field()
    ID_value = scrapy.Field()
    ID_value_orig = scrapy.Field()

    @classmethod
    def from_product(cls, product, kind='', value=''):
        return cls(source_internal_id=product.get('source_internal_id', ''),
                   ProductName=product.get('ProductName', ''), ID_kind=kind, ID_value=value)


class AmazonCollection(scrapy.Item):
    _name = "amazon_collection"
    collection = scrapy.Field()


class AmazonProduct(scrapy.Item):
    _name = "amazon_product"
    product = scrapy.Field()
    asin = scrapy.Field()
    ean = scrapy.Field()
    mpn = scrapy.Field()
    salesrank = scrapy.Field()
    amazon_group = scrapy.Field()
    price = scrapy.Field()

