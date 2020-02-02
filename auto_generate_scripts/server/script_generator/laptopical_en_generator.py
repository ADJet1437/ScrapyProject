# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Laptopical_enSpider", spider_type = "AlaSpider", allowed_domains = "'laptopical.com'", start_urls = "'http://www.laptopical.com/category/laptops'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//section[@id='content']//h2[contains(@class,'post-title')]/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//div[contains(@class,'pagination')]/a[contains(@class,'next')]/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//*[contains(@class,'post-title')]/text()", ocn_xpath = "", pic_xpath = "//meta[@property='og:image']/@content", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "//*[contains(@class,'post-title')]/text()", rating_xpath = "", date_xpath = "//meta[@property='article:published_time']/@content", pros_xpath = "//*[contains(.,'Pros')]/following-sibling::ul[1]/li/text()", cons_xpath = "//*[contains(.,'Cons')]/following-sibling::ul[1]/li/text()", summary_xpath = "//section[@id='content']//div[contains(@class,'entry')]//p[text()][1]//text()", verdict_xpath = "//*[contains(.,'Verdict')or contains(.,'Conclusion')]/following-sibling::p[text()][1]//text()", author_xpath = "//a[@rel='author']/text()", title_xpath = "//*[contains(@class,'post-title')]/text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%y-%m-%dT%H:%M:%S%z", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/laptopical_en.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

