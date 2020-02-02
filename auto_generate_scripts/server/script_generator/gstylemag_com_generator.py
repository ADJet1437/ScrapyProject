# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Gstylemag_comSpider", spider_type = "AlaSpider", allowed_domains = "'gstylemag.com'", start_urls = "'http://gstylemag.com/category/review/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@class='td-main-content-wrap' or @class='td-category-grid']//h3[@itemprop='name']/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//div[contains(@class,'page-nav')]//i[contains(@class,'menu-right')]/../@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "'gstylemag.com'", category_path_xpath = "'gstylemag.com'")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "", ocn_xpath = "'gstylemag.com'", pic_xpath = "//div[@class='td-post-content']//p[img or */img][1]//img/@src", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "", rating_xpath = "", date_xpath = "//div[@class='td-module-meta-info']/text()[last()]", pros_xpath = "", cons_xpath = "", summary_xpath = "//div[@class='td-post-content']/p[string-length(text())>5][1]//text()", verdict_xpath = "//*[text()='Verdict']/following::p[string-length(text())>5][1]//text()", author_xpath = "//div[@class='td-module-meta-info']/a[@rel='author']//text()", title_xpath = "//header[@class='td-post-title']/h1[@itemprop='name']//text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_productname_from_title(replace_words = [[]])
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%B %Y", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/gstylemag_com.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

