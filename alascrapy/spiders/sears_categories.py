#!/usr/bin/env python

"""sears category Spider: """

__author__ = 'graeme'

import re

from scrapy import Request

from alascrapy.items import CategoryItem
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider


class SearsCategorySpider(AlaSpider):
    name = 'sears_categories'
    allowed_domains = ['sears.com']
    start_urls = ['http://www.sears.com/shc/s/smv_10153_12605']
    #start_urls = ['http://www.sears.com/shc/s/smv_10153_12605?vName=Beauty']

    def __init__(self, *args, **kwargs):
        super(SearsCategorySpider, self).__init__(self, *args, **kwargs)

    def parse(self, response):

        if "shopping-tourism" in response.url:
            # No thanks Sears, we want to go to your categories page
            cat_page_req_url = "http://www.sears.com/shc/s/smv_10153_12605"
            cat_page_req = Request(cat_page_req_url)
            yield cat_page_req

        elif "smv_10153_12605" in response.url:
            url_list = self.extract_list(response.xpath('//div[@class="siteMapSubCell"]/ul/li/a/@href'))
            #count = 0
            for url in url_list:
                #if count == 0:
                    url = "http://www.sears.com/shc/s/" + url
                    subcat_page_req = Request(url, callback=self.parse_subcat_page)
                    yield subcat_page_req

                #count += 1

    def parse_subcat_page(self, response):

        # Column 1
        column_position = 1
        header_position = 1

        basic_category = self.extract(response.xpath('//h1/a/text()'))

        while column_position < 5:
            current_category_list = [basic_category]
            current_category_level = -1

            header = self.extract(response.xpath('//div[@class="siteMapSubCat" and position()=%d]/h4[position()=%d]/a/text()' % (column_position, header_position)))
            sub_categories_list = self.extract_list(response.xpath('//div[@class="siteMapSubCat" and position()=%d]/h4[position()=%d]/following::ul[position()=1]/li/a/text()' % (column_position, header_position)))
            indent_list = self.extract_list(response.xpath('//div[@class="siteMapSubCat" and position()=%d]/h4[position()=%d]/following::ul[position()=1]/li/@style' % (column_position, header_position)))
            link_list = self.extract_list(response.xpath('//div[@class="siteMapSubCat" and position()=%d]/h4[position()=%d]/following::ul[position()=1]/li/a/@href' % (column_position, header_position)))

            # This is a bit annoying and complicated. If there's no more headers in the current column, we want to check
            # the next column for subcategories. On top of that, the entire next column might be subcategories so we
            # have to handle that differently. Joy.
            next_header = self.extract(response.xpath('//div[@class="siteMapSubCat" and position()=%d]/h4[position()=%d]/a/text()' % (column_position, header_position + 1)))
            if not next_header:
                # Grab subcategories which trail over into next column
                start_column_position = column_position
                next_column_position = column_position + 1
                while column_position < 5:
                    next_column_first_header = self.extract(response.xpath('//div[@class="siteMapSubCat" and position()=%d]/h4[position()=%d]/a/text()' % (next_column_position, 1)))

                    # If the column has no headers then everything in the column belongs to our current header
                    if not next_column_first_header:
                        trailing_subcat_list = self.extract_list(response.xpath('//div[@class="siteMapSubCat" and position()=%d]/ul[position()=1]/li/a/text()' % next_column_position))
                        trailing_indent_list = self.extract_list(response.xpath('//div[@class="siteMapSubCat" and position()=%d]/ul[position()=1]/li/@style' % next_column_position))
                        trailing_link_list = self.extract_list(response.xpath('//div[@class="siteMapSubCat" and position()=%d]/ul[position()=1]/li/a/@href' % next_column_position))

                        sub_categories_list.extend(trailing_subcat_list)
                        indent_list.extend(trailing_indent_list)
                        link_list.extend(trailing_link_list)

                        # Entire column of subcategories so we'll boost the overall column position too.
                        column_position += 1
                    else:
                        trailing_subcat_list = self.extract_list(response.xpath('//div[@class="siteMapSubCat" and position()=%d]/h4[position()=1]/preceding::ul[position()=1]/li/a/text()' % next_column_position))
                        trailing_indent_list = self.extract_list(response.xpath('//div[@class="siteMapSubCat" and position()=%d]/h4[position()=1]/preceding::ul[position()=1]/li/@style' % next_column_position))
                        trailing_link_list = self.extract_list(response.xpath('//div[@class="siteMapSubCat" and position()=%d]/h4[position()=1]/preceding::ul[position()=1]/li/a/@href' % next_column_position))

                        sub_categories_list.extend(trailing_subcat_list)
                        indent_list.extend(trailing_indent_list)
                        link_list.extend(trailing_link_list)

                        # Reset the header position and increment the column position
                        column_position += 1
                        header_position = 1
                        break

                    # Check the next column
                    next_column_position = column_position + 1

            current_category_list.append(header)

            for sub_cat, indent, link in zip(sub_categories_list, indent_list, link_list):
                matches = re.search(r'(\d+)px', indent)
                if matches:
                    indent_value = int(matches.group(1))

                if current_category_level < indent_value:
                    # Increment a level
                    current_category_list.append(sub_cat)
                    current_category_level = indent_value
                elif current_category_level == indent_value:
                    # Ditch the last one, switch it for this one
                    current_category_list.pop()
                    current_category_list.append(sub_cat)
                elif current_category_level > indent_value:
                    # The annoying scenario. Decrease the level 6 at a time, popping as we go
                    while current_category_level >= indent_value:
                        current_category_list.pop()
                        current_category_level -= 6  # the indent between subcategories is 6px, hence this magic number
                    # Once we reach the lowest level, append and set the new level
                    current_category_list.append(sub_cat)
                    current_category_level = indent_value

                category = CategoryItem()
                category['category_leaf'] = sub_cat
                category['category_path'] = " > ".join(current_category_list)
                category['category_url'] = "http://www.sears.com" + link

                yield category

            if next_header:
                header_position += 1

            if not next_header and start_column_position == 4:
                break
