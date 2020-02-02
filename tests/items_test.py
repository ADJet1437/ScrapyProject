__author__ = 'graeme'

import unittest
from alascrapy.items import CategoryItem, ProductItem, ProductIdItem, ReviewItem


class ItemTest(unittest.TestCase):

    def test_category(self):
        category = CategoryItem()
        category['category_leaf'] = "Cat Leaf"
        category['category_path'] = "Path One > Path Two ,.-'` Cat Leaf `'-.,"
        category['category_url'] = "http://trolololol.com/PathOne/PathTwo/catleaf.shtml"
        category['source_id'] = 1234567

        assert category._name == "category", "CategoryItem _name field incorrect"
        assert category['category_leaf'] == "Cat Leaf", "CategoryItem category_leaf incorrectly set"
        assert category['category_path'] == "Path One > Path Two ,.-'` Cat Leaf `'-.,", "CategoryItem category_path incorrectly set"
        assert category['category_url'] == "http://trolololol.com/PathOne/PathTwo/catleaf.shtml",\
            "CategoryItem category_url incorrectly set"
        assert category['source_id'] == 1234567, "CategoryItem source_id incorrectly set"

    def test_product(self):
        product = ProductItem()
        product['source_id'] = 7654321
        product['source_internal_id'] = "Squibobble12387"
        product['ProductName'] = "Awesome fake product #1"
        product['OriginalCategoryName'] = "Fake products"
        product['PicURL'] = "http://totes.fake.website.com/fake_products/pics/fake_product_of_awesome.jpg"
        product['ProductManufacturer'] = "ACME"
        product['TestUrl'] = "http://totes.fake.website.com/fake_products/fake_product_of_awesome.html"

        assert product._name == "product", "ProductItem _name field incorrect"
        assert product['source_id'] == 7654321, "ProductItem source_id incorrectly set"
        assert product['source_internal_id'] == "Squibobble12387", "ProductItem source_internal_id incorrectly set"
        assert product['ProductName'] == "Awesome fake product #1", "ProductItem ProductName incorrectly set"
        assert product['OriginalCategoryName'] == "Fake products", "ProductItem OriginalCategoryName incorrectly set"
        assert product['PicURL'] == "http://totes.fake.website.com/fake_products/pics/fake_product_of_awesome.jpg", \
            "ProductItem PicURL incorrectly set"
        assert product['ProductManufacturer'] == "ACME", "ProductItem ProductManufacturer incorrectly set"
        assert product['TestUrl'] == "http://totes.fake.website.com/fake_products/fake_product_of_awesome.html", \
            "ProductItem TestUrl incorrectly set"

    def test_product_id(self):
        product_id = ProductIdItem()
        product_id['source_id'] = 1987238972
        product_id['source_internal_id'] = "123Jupiter987"
        product_id['ProductName'] = "I'M A PRODUCT!"
        product_id['ID_kind'] = "ean"
        product_id['ID_value'] = "not_an_ean_value_at_all"

        assert product_id._name == "product_id", "ProductIdItem _name incorrect"
        assert product_id['source_id'] == 1987238972, "ProductIdItem source_id incorrectly set"
        assert product_id['source_internal_id'] == "123Jupiter987", "ProductIdItem source_internal_id incorrectly set"
        assert product_id['ProductName'] == "I'M A PRODUCT!", "ProductIdItem ProductName incorrectly set"
        assert product_id['ID_kind'] == "ean", "ProductIdItem ID_kind incorrectly set"
        assert product_id['ID_value'] == "not_an_ean_value_at_all", "ProductIdItem ID_value incorrectly set"

    def test_review(self):
        review = ReviewItem()

        review['source_id'] = 19827398
        review['source_internal_id'] = "FakeID"
        review['ProductName'] = "Fake Product Name"
        review['SourceTestRating'] = "9 million"
        review['SourceTestScale'] = "10"
        review['TestDateText'] = "29/02/2000"
        review['TestPros'] = "Shiny"
        review['TestCons'] = "Doesn't work"
        review['TestSummary'] = "BUY THEM ALL"
        review['TestVerdict'] = "BUY"
        review['Author'] = "Steve"
        review['DbaseCategoryName'] = "Fake Items"
        review['TestTitle'] = "An amazingly shiny thing I bought"
        review['TestUrl'] = "http://awesomejunk.com/shinythings/fake_shiny_thing.html"
        review['Pay'] = "Maybe"
        review['award'] = "AWESOME"
        review['AwardPic'] = "http://somewhere.else.com/pic.png"
        review['countries'] = "ALL OF THEM"

        assert review._name == "review", "ReviewItem _name incorrect"
        assert review['source_id'] == 19827398, "ReviewItem source_id incorrectly set"
        assert review['source_internal_id'] == "FakeID", "ReviewItem source_internal_id incorrectly set"
        assert review['ProductName'] == "Fake Product Name", "ReviewItem ProductName incorrectly set"
        assert review['SourceTestRating'] == "9 million", "ReviewItem SourceTestRating incorrectly set"
        assert review['SourceTestScale'] == "10", "ReviewItem SourceTestScale incorrectly set"
        assert review['TestDateText'] == "29/02/2000", "ReviewItem TestDateText incorrectly set"
        assert review['TestPros'] == "Shiny", "ReviewItem TestPros incorrectly set"
        assert review['TestCons'] == "Doesn't work", "ReviewItem TestCons incorrectly set"
        assert review['TestSummary'] == "BUY THEM ALL", "ReviewItem TestSummary incorrectly set"
        assert review['TestVerdict'] == "BUY", "ReviewItem TestVerdict incorrectly set"
        assert review['Author'] == "Steve", "ReviewItem Author incorrectly set"
        assert review['DbaseCategoryName'] == "Fake Items", "ReviewItem DbaseCategoryName incorrectly set"
        assert review['TestTitle'] == "An amazingly shiny thing I bought", "ReviewItem TestTitle incorrectly set"
        assert review['TestUrl'] == "http://awesomejunk.com/shinythings/fake_shiny_thing.html", \
            "ReviewItem TestUrl incorrectly set"
        assert review['Pay'] == "Maybe", "ReviewItem Pay incorrectly set"
        assert review['award'] == "AWESOME", "ReviewItem award incorrectly set"
        assert review['AwardPic'] == "http://somewhere.else.com/pic.png", "ReviewItem AwardPic incorrectly set"
        assert review['countries'] == "ALL OF THEM", "ReviewItem countries incorrectly set"

    @classmethod
    def suite(cls):

        tests = ['test_category', 'test_product',
                 'test_product_id', 'test_review']

        return unittest.TestSuite(map(ItemTest, tests))

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(ItemTest.suite())