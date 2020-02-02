# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Unbox_phSpider", spider_type = "AlaSpider", allowed_domains = "'unbox.ph'", start_urls = "'http://www.unbox.ph/category/editorials/reviews/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//div[@class='pagination']//*[contains(@*,'next')]/a/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//article//h2/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//div[@id='crumbs']/descendant-or-self::a[last()]//text()", category_path_xpath = "//div[@id='crumbs']//a//text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "substring-after(//link[@rel='shortlink']/@href,'p=')", pname_xpath = "//h1//text()", ocn_xpath = "//div[@id='crumbs']//a//text()", pic_xpath = "//meta[@property='og:image']/@content", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//link[@rel='amphtml']/@href", level_index = "3", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "3", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "//h1[contains(@class,'title')]//text()", rating_xpath = "", date_xpath = "normalize-space(//*[contains(@*,'meta-date')])", pros_xpath = "", cons_xpath = "", summary_xpath = "//div[contains(@class,'the_content')]/p[string-length(normalize-space())>1][1]//text() | //div[contains(@class,'the_content')]/div[not(./preceding-sibling::p[string-length(normalize-space())>1])][string-length(normalize-space())>1][1]//text()", verdict_xpath = "normalize-space(//div[contains(@class,'the_content')]/*[contains(.,'erdict')][last()]/following-sibling::p[string-length(normalize-space())>1][1])", author_xpath = "//span[contains(@class,'author')]//text()", title_xpath = "//h1[contains(@class,'title')]//text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "TestDateText", regex = "(\w+\s\d+,\s\d{4})", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%B %d, %Y", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/unbox_ph.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

