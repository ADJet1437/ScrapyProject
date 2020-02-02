# -*- coding: utf-8 -*-
import scrapy
import json
import re
import pprint
from datetime import datetime
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.items import ProductItem, ReviewItem
from alascrapy.lib.generic import get_full_url


class GoogleCustomSearchApiSpider(AlaSpider):

    def parse(self, response):
        self._logger.info('Parsing Url: {}'.format(response.url))
        # TODO: improve this model for all scenarios data structure
        keyword = self.keyword.replace("+", " ")
        res = json.loads(response.text)
        items = res.get('items', '')
        count = 0
        for item in items:
            # print(item)
            """The standard item will have 11 keys inside the dict:
            kind, title, htmlTitle, link, displayLink, snippet
            htmlSnippet, cacheId, formatterdUrl and pagemap.
            """
            # some can be get directly from item
            link = item.get('link', '')
            source_id = self.get_source_id(link)
            title = item.get('title', '')
            if not source_id:
                # if no existing source in db
                continue
            count += 1
            cache_id = item.get('cacheId', '')  # source internal id
            snippet = item.get('snippet', '')
            snippet = ''.join(x.rstrip('\n') for x in snippet)
            # snippet = snippet.encode('utf-8')  # used for summary

            pagemap = item.get('pagemap')

            product_items = pagemap.get("product")
            image = ""
            if product_items:
                """A perfect product item is like:
                {
                "image": " ",
                "name": " ",
                "sku": "984549994",
                "brand": "Vivitar",
                "gtin13": "0681066261729",
                "description": ""
                }
                """
                product_items = product_items[0]
                image = product_items.get("image")

            product_name = self.handle_product_name(pagemap, item, title)
            manufacturer = pagemap.get('manufacturer', '')
            # For review items
            review_items = pagemap.get('review')
            # print(review_items)
            review_date = ""
            if review_items:
                review_items = review_items[0]
                author = review_items.get('reviewer')
                # author = review_items.get('author')
                rating = review_items.get('ratingstars')
                review_date = review_items.get('reviewdate')
                if not review_date:
                    review_date = review_items.get('datepublished')
            rating_items = pagemap.get('rating')
            bestrating = u''
            if rating_items:
                rating_items = rating_items[0]
                bestrating = rating_items.get('bestrating', '')
                rating = rating_items.get('ratingvalue', '')

            metatags = pagemap.get('metatags')[0]
            if not image:
                image = self.handle_image(pagemap, metatags)
            if not review_date:
                review_date = self.extract_review_date_from_metatags(metatags)
            # sometimes, author will be inside metatags
            if not author:
                author = metatags.get("author")

            dbcn = 'pro'
            create_time = datetime.now()

            self.insert_products_to_db(product_name, image, manufacturer,
                                       title, source_id, cache_id, link,
                                       rating, bestrating, author, snippet,
                                       dbcn, review_date, create_time,
                                       keyword)
        self._logger.info(
            "Successfully insert %s reviews to table temp.gcse_results_alatest",
            count)

    def handle_review(self):
        pass

    def handle_image(self, pagemap, metatags):
        image = ""
        image1 = pagemap.get('image', '')
        image2 = metatags.get("thumbnail", "")
        image3 = metatags.get("og:image", "")
        if image1:
            image = image1
        elif image2:
            image = image2
        elif image3:
            image = image3
        return image

    def handle_product_name(self, pagemap, item, title):
        product_items = pagemap.get('product')
        if product_items:
            product_name = product_items[0].get("name")
            return product_name
        else:
            # Otherwise, get the prodcut name from title
            product_name = re.split('review', title, flags=re.IGNORECASE)[0]
            return product_name
        return ""

    def handle_product_ids(self):
        pass

    def refine_review_date(self, text):
        if 'T' in text:
            review_date = text.split('T')[0]
        else:
            review_date = text
        return review_date

    def extract_review_date_from_metatags(self, metatags):
        review_date = ""
        str1 = metatags.get('pub_date', '')
        str2 = metatags.get("article:published_time", "")
        str3 = metatags.get("date")
        str4 = metatags.get("live_date")
        if str1:
            review_date = self.refine_review_date(str1)
        elif str2:
            review_date = self.refine_review_date(str2)
        elif str3:
            review_date = self.refine_review_date(str3)
        elif str4:
            review_date = self.refine_review_date(str4)
        return review_date

    def transfer_type(self, i):
        try:
            i = str(i)
        except:
            i = i.encode('utf-8')
        return i

    def calculate_scale(self, rating):
        scale = ""
        if float(rating) < 5:
            scale = 5
        elif float(rating) < 10:
            scale = 10
        else:
            scale = 100
        return str(scale)

    def insert_products_to_db(self, product_name, image, manufacturer,
                              title, source_id, cache_id, link, rating, scale,
                              author, summary, dbcn, review_date, create_time,
                              keyword):
        if not scale:
            if rating:
                scale = self.calculate_scale(rating)
        args = {}
        for key, value in zip(locals().keys(), locals().values()):
            value = self.transfer_type(value)
            if value == 'None':
                value = "NULL"
            if value == "":
                value = "NULL"
            if value == "NULL":
                value = "NULL"
            else:
                value = "\"{}\"".format(value)
            args[key] = value
        insert_query = """INSERT IGNORE INTO temp.gcse_results_alatest
                                 (product_name,
                                 pic_url,
                                 manufacturer,
                                 title,
                                 source_id,
                                 source_internal_id,
                                 test_url,
                                 rating,
                                 RatingScale,
                                 Author,
                                 TestSummary,
                                 DBCN,
                                 review_date,
                                 create_time,
                                 search_keyword
                                 )
                                 VALUES (%s,%s,%s,%s,%s,%s,%s, \
                                        %s, %s, %s,%s, %s,%s, \
                                        %s, %s)""" % (args['product_name'],
                                                      args['image'],
                                                      args['manufacturer'],
                                                      args['title'],
                                                      int(source_id),
                                                      args['cache_id'],
                                                      args['link'],
                                                      args['rating'],
                                                      args['scale'],
                                                      args['author'],
                                                      args['summary'],
                                                      args['dbcn'],
                                                      args['review_date'],
                                                      args['create_time'],
                                                      args['keyword']
                                                      )
        # print(insert_query)
        self.mysql_manager.insert_gcse_results(insert_query)

    def get_source_id(self, link):
        source_str = re.findall(r'www.(.*?)/', link)
        if source_str:
            source_str = source_str[0]
            query = """select source_id from 
                    review.sources where source rlike %s"""
            source_id = self.mysql_manager.execute_select(query, source_str)
            if source_id:
                source_id = source_id[0]['source_id']
                return source_id
            return ""
        return ""
