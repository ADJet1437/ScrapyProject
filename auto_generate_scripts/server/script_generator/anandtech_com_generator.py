# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Anandtech_comSpider", spider_type = "AlaSpider", allowed_domains = "'anandtech.com'", start_urls = "'http://www.anandtech.com/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//a[@rel='next']/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//section/div[starts-with(@class,'cont_box1') or @class='featured_banner']/div[1]/a[1]/@href", level_index = "2", url_regex = "(.*[^p](?=review))", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//nav[@class='breadcrumb']//li[last()]/a/text()", category_path_xpath = "//nav[@class='breadcrumb']//li/a/text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "//link[@rel='shortlink']/@href", pname_xpath = "translate(substring-after(substring-after(//meta[@property='og:url']/@content,'/show/'),'/'),'-',' ')", ocn_xpath = "", pic_xpath = "//meta[@property='og:image']/@content", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "//link[@rel='shortlink']/@href", pname_xpath = "translate(substring-after(substring-after(//meta[@property='og:url']/@content,'/show/'),'/'),'-',' ')", rating_xpath = "", date_xpath = "//div[starts-with(@class,'blog_top')]/span/em", pros_xpath = "", cons_xpath = "", summary_xpath = "//div[contains(@class,'Content')]/p[string-length(normalize-space())>1][not(strong)][1]//text()", verdict_xpath = "", author_xpath = "//meta[@name='author']/@content", title_xpath = "//meta[@property='og:title']/@content", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "source_internal_id", regex = "((?<=\/show\/)\d.*\d)", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "source_internal_id", regex = "((?<=\/show\/)\d.*\d)", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "TestDateText", regex = "((?<=on\s).*(?=\s\d))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "ProductName", regex = "(\w.*(?=\sreview))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "ProductName", regex = "(\w.*(?=\sreview))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "ProductName", regex = "((?<=the\s).*)", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "ProductName", regex = "((?<=the\s).*)", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%B %d, %Y", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.get_fields_supplement(in_another_page_xpath = "//select[@name='ContentPagesListTop']/option[last()]/@value", test_verdict_xpaths = ['//h2[(contains(.,"Final") and contains(.,"Words")) or contains(.,"Conclusion") or contains(.,"Conclud")]/following::p[string-length(normalize-space())>1 and not(./preceding::h3/preceding::h2) and not(./preceding::div[contains(@class,"ShoppingWidget")]) and not(@align)][starts-with(.,"Overall") or starts-with(.,"Last") or contains(.,"summary") or position()=last()][1]//text()'], pros_xpath = "", cons_xpath = "", rating_xpath = "", award_xpath = "", award_pic_xpath = "")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/anandtech_com.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

