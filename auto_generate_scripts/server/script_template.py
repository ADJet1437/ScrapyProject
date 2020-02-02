# -*- coding: utf8 -*-

import_template = '''# -*- coding: utf8 -*-
from datetime import datetime
import re

from scrapy.http import Request, HtmlResponse
from scrapy.selector import Selector

from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.spiders.base_spiders.bazaarvoice_spider import BVNoSeleniumSpider
from alascrapy.lib.generic import get_full_url, date_format
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import CategoryItem, ProductItem, ReviewItem, ProductIdItem
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from alascrapy.lib.selenium_browser import SeleniumBrowser



'''

init_func_template = '''class {{spider_name}}({{spider_type}}):
    name = '{{name}}'
    allowed_domains = [{{allowed_domains}}]
    start_urls = [{{start_urls}}]


'''

level_template = '''    {% if level_index == '1' %}
    def parse(self, response):
                                    {% else %}
    def level_{{level_index}}(self, response):
                                    {% endif %} 
        original_url = response.url
        product = response.meta.get("product", {})
        review = response.meta.get("review", {})
        {% if need_parse_javascript == "yes" %}
        with SeleniumBrowser(self, response) as browser:
            browser.get(response.url)
            original_request = response.request
            response = Selector(text=browser.browser.page_source).response
            response = HtmlResponse(original_url).replace(body=response.body)
            response.request = original_request
        {% endif %}

'''

request_single_url_template = '''        url_xpath = u"{{url_xpath}}"
        single_url = self.extract(response.xpath(url_xpath))
        if single_url:
            matches = None
            if "{{url_regex}}":
                matches = re.search("{{url_regex}}", single_url, re.IGNORECASE)
                if matches:
                    single_url = matches.group(0)
                else:
                    return
            single_url = get_full_url(original_url, single_url)
            {% if level_index == '1' %}
            request = Request(single_url, callback=self.parse)
            {% else %}
            request = Request(single_url, callback=self.level_{{level_index}})
            {% endif -%}
            try:
                request.meta["product"] = product
            except:
                pass
            try:
                request.meta["review"] = review
            except:
                pass
            yield request

'''

request_urls_template = '''        urls_xpath = u"{{urls_xpath}}"
        params_regex = {{params_regex}}
        urls = self.extract_list(response.xpath(urls_xpath))
        {% if include_original_url == "yes" %}
        urls.append(original_url)
        {% endif %}
        for single_url in urls:
            matches = None
            if "{{url_regex}}":
                matches = re.search("{{url_regex}}", single_url, re.IGNORECASE)
                if matches:
                    single_url = matches.group(0)
                else:
                    continue
            single_url = get_full_url(original_url, single_url)
            {% if level_index == '1' %}
            request = Request(single_url, callback=self.parse)
            {% else %}
            request = Request(single_url, callback=self.level_{{level_index}})
            {% endif %}
            {% for key, value in params_xpath.iteritems() %}
            matches = None
            text_{{loop.index}} = ""
            extract_text = self.extract(response.xpath(u'{{value}}'))
            if extract_text:
                if "{{key}}" in params_regex:
                    matches = re.search(params_regex.get("{{key}}", ""), extract_text, re.IGNORECASE)
                    if matches:
                        text_{{loop.index}} = matches.group(1)
                else:
                    text_{{loop.index}} = extract_text
            request.meta["{{key}}"] = text_{{loop.index}}
            {% endfor %} 
            try:
                request.meta["product"] = product
            except:
                pass
            try:
                request.meta["review"] = review
            except:
                pass
            yield request

'''

request_containers_urls_template = '''        containers_xpath = u"{{containers_xpath}}"
        url_xpath = u"{{url_xpath}}"
        params_regex = {{params_regex}}
        containers = response.xpath(containers_xpath)
        for container in containers:
            single_url = self.extract(container.xpath(url_xpath))
            single_url = get_full_url(response, single_url)
            {%- if level_index == '1' %}
            request = Request(single_url, callback=self.parse)
            {% else %}
            request = Request(single_url, callback=self.level_{{level_index}})
            {% endif -%} 
            {% for key, value in params_xpath.iteritems() %}
            matches = None
            text_{{loop.index}} = ""
            extract_text = self.extract(container.xpath(u'{{value}}'))
            if extract_text:
                if "{{key}}" in params_regex:
                    matches = re.search(params_regex.get("{{key}}", ""), extract_text, re.IGNORECASE)
                    if matches:
                        text_{{loop.index}} = matches.group(1)
                else:
                    text_{{loop.index}} = extract_text
            request.meta["{{key}}"] = text_{{loop.index}}
            {% endfor %}
            try:
                request.meta["product"] = product
            except:
                pass
            try:
                request.meta["review"] = review
            except:
                pass
            yield request

'''

product_template = '''        product_xpaths = { 
                {% if sii_xpath %}
                "source_internal_id": u"{{sii_xpath}}",
                {% endif %}
                {% if pname_xpath %}
                "ProductName":u"{{pname_xpath}}",
                {% endif %}
                {% if ocn_xpath %}
                "OriginalCategoryName":u"{{ocn_xpath}}",
                {% endif %}
                {% if pic_xpath %}
                "PicURL":u"{{pic_xpath}}",
                {% endif %}
                {% if manuf_xpath %}
                "ProductManufacturer":u"{{manuf_xpath}}"
                {% endif %}
                            }
        product = self.init_item_by_xpaths(response, "product", product_xpaths)
        product['TestUrl'] = original_url
        picurl = product.get("PicURL", "")
        if picurl and picurl[:2] == "//":
            product["PicURL"] = "https:" + product["PicURL"]
        if picurl and picurl[:1] == "/":
            product["PicURL"] = get_full_url(original_url, picurl)
        manuf = product.get("ProductManufacturer", "")
        if manuf == "" and u"{{manuf_xpath}}"[:2] != "//":
            product["ProductManufacturer"] = u"{{manuf_xpath}}"
        try:
            product["OriginalCategoryName"] = category['category_path']
        except:
            pass
        ocn = product.get("OriginalCategoryName", "")
        if ocn == "" and u"{{ocn_xpath}}"[:2] != "//":
            product["OriginalCategoryName"] = u"{{ocn_xpath}}"

'''

review_template = '''        review_xpaths = { 
                {% if sii_xpath %}
                "source_internal_id": u"{{sii_xpath}}",
                {% endif %}
                {% if pname_xpath %}
                "ProductName":u"{{pname_xpath}}",
                {% endif %}
                {% if rating_xpath %}
                "SourceTestRating":u"{{rating_xpath}}",
                {% endif %}
                {% if date_xpath %}
                "TestDateText":u"{{date_xpath}}",
                {% endif %}
                {% if pros_xpath %}
                "TestPros":u"{{pros_xpath}}",
                {% endif %}
                {% if cons_xpath %}
                "TestCons":u"{{cons_xpath}}",
                {% endif %}
                {% if summary_xpath %}
                "TestSummary":u"{{summary_xpath}}",
                {% endif %}
                {% if verdict_xpath %}
                "TestVerdict":u"{{verdict_xpath}}",
                {% endif %}
                {% if author_xpath %}
                "Author":u"{{author_xpath}}",
                {% endif %}
                {% if title_xpath %}
                "TestTitle":u"{{title_xpath}}",
                {% endif %}
                {% if award_xpath %}
                "award":u"{{award_xpath}}",
                {% endif %}
                {% if awpic_xpath %}
                "AwardPic":u"{{awpic_xpath}}"
                {% endif %}
                            }
        review = self.init_item_by_xpaths(response, "review", review_xpaths)
        review['TestUrl'] = original_url
        try:
            review['ProductName'] = product['ProductName']
            review['source_internal_id'] = product['source_internal_id']
        except:
            pass
        awpic_link = review.get("AwardPic", "")
        if awpic_link and awpic_link[:2] == "//":
            review["AwardPic"] = "https:" + review["AwardPic"]
        if awpic_link and awpic_link[:1] == "/":
            review["AwardPic"] = get_full_url(original_url, awpic_link)

'''

containers_review_template = '''{% if button_next_javascript == "no" %}
        {% if first_js_on_page == "true" %}
        button_next_url = ""
        if u"{{button_next_xpath}}":
            button_next_url = self.extract(response.xpath(u"{{button_next_xpath}}"))
        if button_next_url:
            button_next_url = get_full_url(original_url, button_next_url)
            request = Request(button_next_url, callback=self.level_{{highest_level}})
            {% for meta_item in response_meta %}
            request.meta["{{meta_item}}"] = response.meta["{{meta_item}}"]
            {% endfor %}
            yield request

        containers_xpath = u"{{containers_xpath}}"
        containers = response.xpath(containers_xpath)
        for review_container in containers:
            review = ReviewItem()
            {% if sii_xpath %}
            review['source_internal_id'] = self.extract(response.xpath(u"{{sii_xpath}}"))
            {% endif %}
            {% if pname_xpath %}
            review['ProductName'] = self.extract(review_container.xpath(u"{{pname_xpath}}"))
            {% endif %}
            {% if rating_xpath %}
            review['SourceTestRating'] = self.extract(review_container.xpath(u"{{rating_xpath}}"))
            {% endif %}
            {% if date_xpath %}
            review['TestDateText'] = self.extract(review_container.xpath(u"{{date_xpath}}"))
            {% endif %}
            {% if pros_xpath %}
            review['TestPros'] = self.extract(review_container.xpath(u"{{pros_xpath}}"))
            {% endif %}
            {% if cons_xpath %}
            review['TestCons'] = self.extract(review_container.xpath(u"{{cons_xpath}}"))
            {% endif %}
            {% if summary_xpath %}
            review['TestSummary'] = self.extract(review_container.xpath(u"{{summary_xpath}}"))
            {% endif %}
            {% if verdict_xpath %}
            review['TestVerdict'] = self.extract(review_container.xpath(u"{{verdict_xpath}}"))
            {% endif %}
            {% if author_xpath %}
            review['Author'] = self.extract(review_container.xpath(u"{{author_xpath}}"))
            {% endif %}
            {% if title_xpath %}
            review['TestTitle'] = self.extract(review_container.xpath(u"{{title_xpath}}"))
            {% endif %}
            {% if award_xpath %}
            review['award'] = self.extract(review_container.xpath(u"{{award_xpath}}"))
            {% endif %}
            {% if awpic_xpath %}
            review['AwardPic'] = self.extract(review_container.xpath(u"{{awpic_xpath}}"))
            {% endif %}
            review['TestUrl'] = original_url
            try:
                review['ProductName'] = product['ProductName']
                review['source_internal_id'] = product['source_internal_id']
            except:
                pass
            awpic_link = review.get("AwardPic", "")
            if awpic_link and awpic_link[:2] == "//":
                review["AwardPic"] = "https:" + review["AwardPic"]
            if awpic_link and awpic_link[:1] == "/":
                review["AwardPic"] = get_full_url(original_url, awpic_link)
        {% else %}
            button_next_url = ""
            if u"{{button_next_xpath}}":
                button_next_url = self.extract(response.xpath(u"{{button_next_xpath}}"))
            if button_next_url:
                button_next_url = get_full_url(original_url, button_next_url)
                request = Request(button_next_url, callback=self.level_{{highest_level}})
                {% for meta_item in response_meta %}
                request.meta["{{meta_item}}"] = response.meta["{{meta_item}}"]
                {% endfor %}
                yield request

            containers_xpath = u"{{containers_xpath}}"
            containers = response.xpath(containers_xpath)
            for review_container in containers:
                review = ReviewItem()
                {% if sii_xpath %}
                review['source_internal_id'] = self.extract(response.xpath(u"{{sii_xpath}}"))
                {% endif %}
                {% if pname_xpath %}
                review['ProductName'] = self.extract(review_container.xpath(u"{{pname_xpath}}"))
                {% endif %}
                {% if rating_xpath %}
                review['SourceTestRating'] = self.extract(review_container.xpath(u"{{rating_xpath}}"))
                {% endif %}
                {% if date_xpath %}
                review['TestDateText'] = self.extract(review_container.xpath(u"{{date_xpath}}"))
                {% endif %}
                {% if pros_xpath %}
                review['TestPros'] = self.extract(review_container.xpath(u"{{pros_xpath}}"))
                {% endif %}
                {% if cons_xpath %}
                review['TestCons'] = self.extract(review_container.xpath(u"{{cons_xpath}}"))
                {% endif %}
                {% if summary_xpath %}
                review['TestSummary'] = self.extract(review_container.xpath(u"{{summary_xpath}}"))
                {% endif %}
                {% if verdict_xpath %}
                review['TestVerdict'] = self.extract(review_container.xpath(u"{{verdict_xpath}}"))
                {% endif %}
                {% if author_xpath %}
                review['Author'] = self.extract(review_container.xpath(u"{{author_xpath}}"))
                {% endif %}
                {% if title_xpath %}
                review['TestTitle'] = self.extract(review_container.xpath(u"{{title_xpath}}"))
                {% endif %}
                {% if award_xpath %}
                review['award'] = self.extract(review_container.xpath(u"{{award_xpath}}"))
                {% endif %}
                {% if awpic_xpath %}
                review['AwardPic'] = self.extract(review_container.xpath(u"{{awpic_xpath}}"))
                {% endif %}
                review['TestUrl'] = original_url
                try:
                    review['ProductName'] = product['ProductName']
                    review['source_internal_id'] = product['source_internal_id']
                except:
                    pass
                awpic_link = review.get("AwardPic", "")
                if awpic_link and awpic_link[:2] == "//":
                    review["AwardPic"] = "https:" + review["AwardPic"]
                if awpic_link and awpic_link[:1] == "/":
                    review["AwardPic"] = get_full_url(original_url, awpic_link)
        {% endif %}

    {% else %}

        {% if first_js_on_page == "true" %}
        with SeleniumBrowser(self, response) as browser:
            browser.get(response.url)
        {% endif %}
            first_time = True
            while True:
                if not first_time:
                    try:
                        selector = browser.click_link(u"{{button_next_xpath}}", None)
                        response = selector.response
                    except:
                        break

                first_time = False
                containers_xpath = u"{{containers_xpath}}"
                containers = response.xpath(containers_xpath)
                for review_container in containers:
                    review = ReviewItem()
                    {% if sii_xpath %}
                    review['source_internal_id'] = self.extract(response.xpath(u"{{sii_xpath}}"))
                    {% endif %}
                    {% if pname_xpath %}
                    review['ProductName'] = self.extract(review_container.xpath(u"{{pname_xpath}}"))
                    {% endif %}
                    {% if rating_xpath %}
                    review['SourceTestRating'] = self.extract(review_container.xpath(u"{{rating_xpath}}"))
                    {% endif %}
                    {% if date_xpath %}
                    review['TestDateText'] = self.extract(review_container.xpath(u"{{date_xpath}}"))
                    {% endif %}
                    {% if pros_xpath %}
                    review['TestPros'] = self.extract(review_container.xpath(u"{{pros_xpath}}"))
                    {% endif %}
                    {% if cons_xpath %}
                    review['TestCons'] = self.extract(review_container.xpath(u"{{cons_xpath}}"))
                    {% endif %}
                    {% if summary_xpath %}
                    review['TestSummary'] = self.extract(review_container.xpath(u"{{summary_xpath}}"))
                    {% endif %}
                    {% if verdict_xpath %}
                    review['TestVerdict'] = self.extract(review_container.xpath(u"{{verdict_xpath}}"))
                    {% endif %}
                    {% if author_xpath %}
                    review['Author'] = self.extract(review_container.xpath(u"{{author_xpath}}"))
                    {% endif %}
                    {% if title_xpath %}
                    review['TestTitle'] = self.extract(review_container.xpath(u"{{title_xpath}}"))
                    {% endif %}
                    {% if award_xpath %}
                    review['award'] = self.extract(review_container.xpath(u"{{award_xpath}}"))
                    {% endif %}
                    {% if awpic_xpath %}
                    review['AwardPic'] = self.extract(review_container.xpath(u"{{awpic_xpath}}"))
                    {% endif %}
                    review['TestUrl'] = original_url
                    try:
                        review['ProductName'] = product['ProductName']
                        review['source_internal_id'] = product['source_internal_id']
                    except:
                        pass
                    awpic_link = review.get("AwardPic", "")
                    if awpic_link and awpic_link[:2] == "//":
                        review["AwardPic"] = "https:" + review["AwardPic"]
                    if awpic_link and awpic_link[:1] == "/":
                        review["AwardPic"] = get_full_url(original_url, awpic_link)
    {% endif %}       

'''

get_pname_from_title_template = '''        if review and review['TestTitle']:
            title = review["TestTitle"].lower()
            if ":" in title:
                all_title_parts = title.split(":")
                for part in all_title_parts:
                    review["ProductName"] = part.replace("review", "") if 'review' in part else title.replace("review", "")
            else:
                review["ProductName"] = title.replace("review", "")
            {% for replace_word in replace_words %}
            review["ProductName"] = review["ProductName"].replace("{{replace_word}}".lower(), "")
            {% endfor %}
            review["ProductName"] = review["ProductName"].strip("-: ")
            product["ProductName"] = review["ProductName"]

'''

get_dbasecategoryname_template = '''{% if review_type == "PRO" %}
        review["DBaseCategoryName"] = "{{dbcn}}"
                                    {% elif click_next_page == False %}
            {% if first_js_on_page == "true" %}
            review["DBaseCategoryName"] = "{{dbcn}}"
            {% else %}
                review["DBaseCategoryName"] = "{{dbcn}}"
            {% endif %}
                                    {% else %}
                {% if first_js_on_page == "true" %}
                review["DBaseCategoryName"] = "{{dbcn}}"
                {% else %}
                    review["DBaseCategoryName"] = "{{dbcn}}"
                {% endif %} 
                                    {% endif %}

'''

get_sourcetestscale_template = '''{% if review_type == "PRO" %}
        review["SourceTestScale"] = "{{scale}}"
                                    {% elif click_next_page == False %}
            {% if first_js_on_page == "true" %}
            review["SourceTestScale"] = "{{scale}}"
            {% else %}
                review["SourceTestScale"] = "{{scale}}"
            {% endif %} 
                                    {% else %}
                {% if first_js_on_page == "true" %}
                review["SourceTestScale"] = "{{scale}}"
                {% else %}
                    review["SourceTestScale"] = "{{scale}}"
                {% endif %}
                                    {% endif %}

'''

get_testdatetext_template = '''{% if review_type == "PRO" %}
        if review["TestDateText"]:
            {% for replace_word in replace_words %}
            review["TestDateText"] = review["TestDateText"].lower().replace('{{replace_word}}'.lower(), "")
            {% endfor %}
            review["TestDateText"] = review["TestDateText"].strip()
            review["TestDateText"] = date_format(review["TestDateText"], "{{format_string}}", ["{{languages}}"])
                                    {% elif click_next_page == False %}
            {% if first_js_on_page == "true" %}
            if review["TestDateText"]:
                {% for replace_word in replace_words %}
                review["TestDateText"] = review["TestDateText"].lower().replace('{{replace_word}}'.lower(), "")
                {% endfor %}
                review["TestDateText"] = date_format(review["TestDateText"], "{{format_string}}", ["{{languages}}"])
            {% else %}
                if review["TestDateText"]:
                    {% for replace_word in replace_words %}
                    review["TestDateText"] = review["TestDateText"].lower().replace('{{replace_word}}'.lower(), "")
                    {% endfor %}
                    review["TestDateText"] = date_format(review["TestDateText"], "{{format_string}}", ["{{languages}}"])
            {% endif %}
                                    {% else %}
                {% if first_js_on_page == "true" %}
                if review["TestDateText"]:
                    {% for replace_word in replace_words %}
                    review["TestDateText"] = review["TestDateText"].lower().replace('{{replace_word}}'.lower(), "")
                    {% endfor %}
                    review["TestDateText"] = date_format(review["TestDateText"], "{{format_string}}", ["{{languages}}"])
                {% else %}
                    if review["TestDateText"]:
                        {% for replace_word in replace_words %}
                        review["TestDateText"] = review["TestDateText"].lower().replace('{{replace_word}}'.lower(), "")
                        {% endfor %}
                        review["TestDateText"] = date_format(review["TestDateText"], "{{format_string}}", ["{{languages}}"])
                {% endif %}
                                    {% endif %}

'''

clean_field_template = '''{% if review_type == "PRO" or type == "product" %}
        matches = None
        field_value = {{type}}.get("{{field}}", "")
        if field_value:
            matches = re.search("{{regex}}", field_value, re.IGNORECASE)
        if matches:
            {{type}}["{{field}}"] = matches.group(1)
                                    {% elif click_next_page == False %}
            {% if first_js_on_page == "true" %}
            matches = None
            field_value = {{type}}.get("{{field}}", "")
            if field_value:
                matches = re.search("{{regex}}", field_value, re.IGNORECASE)
            if matches:
                {{type}}["{{field}}"] = matches.group(1)
            {% else %}
                matches = None
                field_value = {{type}}.get("{{field}}", "")
                if field_value:
                    matches = re.search("{{regex}}", field_value, re.IGNORECASE)
                if matches:
                    {{type}}["{{field}}"] = matches.group(1)
            {% endif %}
                                    {% else %}
                {% if first_js_on_page == "true" %}
                matches = None
                field_value = {{type}}.get("{{field}}", "")
                if field_value:
                    matches = re.search("{{regex}}", field_value, re.IGNORECASE)
                if matches:
                    {{type}}["{{field}}"] = matches.group(1)
                {% else %}
                    matches = None
                    field_value = {{type}}.get("{{field}}", "")
                    if field_value:
                        matches = re.search("{{regex}}", field_value, re.IGNORECASE)
                    if matches:
                        {{type}}["{{field}}"] = matches.group(1)
                {% endif %}
                                    {% endif %}

'''

get_supplement_xpaths_template = '''{% if review_type == "PRO" or type == "product" %}
        {% for s_xpath in supplement_xpaths %}
        if not {{type}}.get("{{field}}", ""):
            {{type}}["{{field}}"] = self.extract_all(response.xpath(u'{{s_xpath}}'))
        {% endfor %}
                                    {% elif click_next_page == False %}
            {% if first_js_on_page == "true" %}
            {% for s_xpath in supplement_xpaths %}
            if not {{type}}.get("{{field}}", ""):
                {{type}}["{{field}}"] = self.extract_all(response.xpath(u'{{s_xpath}}'))
            {% endfor %}
            {% else %}
                {% for s_xpath in supplement_xpaths %}
                if not {{type}}.get("{{field}}", ""):
                    {{type}}["{{field}}"] = self.extract_all(response.xpath(u'{{s_xpath}}'))
                {% endfor %}
            {% endif %}
                                    {% else %}
                {% if first_js_on_page == "true" %}
                {% for s_xpath in supplement_xpaths %}
                if not {{type}}.get("{{field}}", ""):
                    {{type}}["{{field}}"] = self.extract_all(response.xpath(u'{{s_xpath}}'))
                {% endfor %}
                {% else %}
                    {% for s_xpath in supplement_xpaths %}
                    if not {{type}}.get("{{field}}", ""):
                        {{type}}["{{field}}"] = self.extract_all(response.xpath(u'{{s_xpath}}'))
                    {% endfor %}
                {% endif %}
                                    {% endif %}

'''


get_fields_supplement_template = '''        in_another_page_xpath = u"{{in_another_page_xpath}}"
        pros_xpath = u"{{pros_xpath}}"
        cons_xpath = u"{{cons_xpath}}"
        rating_xpath = u"{{rating_xpath}}"
        award_xpath = u"{{award_xpath}}"
        award_pic_xpath = u"{{award_pic_xpath}}"
        {% for v_xpath in test_verdict_xpaths %}
        test_verdict_xpath_{{loop.index}} = u'{{v_xpath}}'
        {% endfor %}
        review["TestVerdict"] = None
        in_another_page_url = None
        if in_another_page_xpath:
            in_another_page_url = self.extract(response.xpath(in_another_page_xpath))
        if in_another_page_url:
            in_another_page_url = get_full_url(response, in_another_page_url)
            request = Request(in_another_page_url, callback=self.parse_fields_page)
            request.meta['review'] = review
            {% for v_xpath in test_verdict_xpaths %}
            request.meta['test_verdict_xpath_{{loop.index}}'] = test_verdict_xpath_{{loop.index}}
            {% endfor %}
            request.meta['pros_xpath'] = pros_xpath
            request.meta['cons_xpath'] = cons_xpath
            request.meta['rating_xpath'] = rating_xpath
            request.meta['award_xpath'] = award_xpath
            request.meta['award_pic_xpath'] = award_pic_xpath
            yield request
        else:
            {% for v_xpath in test_verdict_xpaths %}
            if not review["TestVerdict"]:
                review["TestVerdict"] = self.extract_all(response.xpath(test_verdict_xpath_{{loop.index}}))
            {% endfor %}
            yield review

'''

parse_fields_template = '''    
    def parse_fields_page(self, response):
        review = response.meta['review']
        {% for num in verdict_xpath_num %}
        test_verdict_xpath_{{loop.index}} = response.meta['test_verdict_xpath_{{loop.index}}']
        {% endfor %}
        {% for num in verdict_xpath_num %}
        if not review["TestVerdict"]:
            review["TestVerdict"] = self.extract_all(response.xpath(test_verdict_xpath_{{loop.index}}))
        {% endfor %}
        pros_xpath = response.meta['pros_xpath']
        cons_xpath = response.meta['cons_xpath']
        rating_xpath = response.meta['rating_xpath']
        award_xpath = response.meta['award_xpath']
        award_pic_xpath = response.meta['award_pic_xpath']
        if pros_xpath:
            review["TestPros"] = self.extract_all(response.xpath(pros_xpath), ' ; ')
        if cons_xpath:
            review["TestCons"] = self.extract_all(response.xpath(cons_xpath), ' ; ')
        if rating_xpath:
            review['SourceTestRating'] = self.extract(response.xpath(rating_xpath), '%')
        if award_xpath:
            review['award'] = self.extract(response.xpath(award_xpath))
        if award_pic_xpath:
            review['AwardPic'] = self.extract(response.xpath(award_pic_xpath))
        yield review

'''

click_template = '''{% if first_js_on_page == "true" %}
        with SeleniumBrowser(self, response) as browser:
        {% endif %}
            wait_for = None
            wait_type, wait_for_xpath = "{{wait_type}}", u"{{wait_for_xpath}}"
            if wait_for_xpath :
                wait_for = EC.{{wait_type}}((By.XPATH, wait_for_xpath))
            browser.get(response.url)
            if response.xpath(u"{{target_xpath}}"):
                selector = browser.click_link(u"{{target_xpath}}", wait_for)
                response = selector.response

'''

click_continuous_template = '''{% if first_js_on_page == "true" %}
        with SeleniumBrowser(self, response) as browser:
        {% endif %}
            wait_for = None
            wait_type, wait_for_xpath = "{{wait_type}}", u"{{wait_for_xpath}}"
            if wait_for_xpath :
                wait_for = EC.{{wait_type}}((By.XPATH, wait_for_xpath))
            browser.get(response.url)
            while True:
                try:
                    selector = browser.click_link(u"{{target_xpath}}", wait_for)
                    response = selector.response
                except:
                    break

'''

scroll_template = '''{% if first_js_on_page == "true" %}
        with SeleniumBrowser(self, response) as browser:
        {% endif %}
            wait_for = None
            wait_type, wait_for_xpath = "{{wait_type}}", u"{{wait_for_xpath}}"
            if wait_for_xpath :
                wait_for = EC.{{wait_type}}((By.XPATH, wait_for_xpath))
            browser.get(response.url)
            selector = browser.scroll_until_the_end(2000, wait_for)
            response = selector.response

'''

product_id_template = '''
        product_id = self.product_id(product)
        {%- if id_value_xpath %}
        id_value = self.extract(response.xpath(u"{{id_value_xpath}}"))
        if id_value:
            product_id['ID_kind'] = "{{id_kind}}"
            product_id['ID_value'] = id_value
            yield product_id
        {% else %}
        product_id['ID_kind'] = "{{id_kind}}"
        product_id['ID_value'] = product["source_internal_id"]
        yield product_id
        {% endif %}

'''

category_template = '''        category_leaf_xpath = u"{{category_leaf_xpath}}"
        category_path_xpath = u"{{category_path_xpath}}"
        category = CategoryItem()
        category['category_url'] = original_url
        category['category_leaf'] = self.extract(response.xpath(category_leaf_xpath))
        category['category_path'] = self.extract_all(response.xpath(category_path_xpath), ' | ')
        if self.should_skip_category(category):
            return
        yield category


'''

save_product_template = '''{% for meta in response_meta %}
        if "{{meta}}" in ProductItem.fields:
            product["{{meta}}"] = response.meta["{{meta}}"]
        {% endfor %}
        yield product


'''


save_review_template = '''
        {% if review_type == "PRO" %}
                            {% for meta in response_meta %}
        if "{{meta}}" in ReviewItem.fields:
            review["{{meta}}"] = response.meta["{{meta}}"]
                            {% endfor %}
        yield review
        {% elif click_next_page == False %}
            {% if first_js_on_page == "true" %}
                            {% for meta in response_meta %}
            if "{{meta}}" in ReviewItem.fields:
                review["{{meta}}"] = response.meta["{{meta}}"]
                            {% endfor %}
            yield review
            {% else %}
                            {% for meta in response_meta %}
                if "{{meta}}" in ReviewItem.fields:
                    review["{{meta}}"] = response.meta["{{meta}}"]
                            {% endfor %}
                yield review
            {% endif %}
        {% else %}
                {% if first_js_on_page == "true" %}
                            {% for meta in response_meta %}
                if "{{meta}}" in ReviewItem.fields:
                    review["{{meta}}"] = response.meta["{{meta}}"]
                            {% endfor %}
                yield review
                {% else %}
                            {% for meta in response_meta %}
                    if "{{meta}}" in ReviewItem.fields:
                        review["{{meta}}"] = response.meta["{{meta}}"]
                            {% endfor %}
                    yield review
                {% endif %}
        {% endif %}

'''
