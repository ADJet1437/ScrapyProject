# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Pinoytechblog_comSpider", spider_type = "AlaSpider", allowed_domains = "'pinoytechblog.com'", start_urls = "'http://www.pinoytechblog.com/archives/category/reviews'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@class='awr']/h2[@class='entry-title']/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//div[contains(@class,'pgn')]/a[contains(@class,'next')]/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//div[contains(@class,'meta')]/descendant::div[contains(@class,'cat_b')][last()-1]//text()", category_path_xpath = "//div[contains(@class,'meta')]/descendant::div[contains(@class,'cat_b')]//text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//div[@class='wrp']/h1[contains(@class,'title')]//text()", ocn_xpath = "//div[contains(@class,'meta')]/descendant::div[contains(@class,'cat_b')]//text()", pic_xpath = "//p[img][1]/img/@src", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "//div[@class='wrp']/h1[contains(@class,'title')]//text()", rating_xpath = "", date_xpath = "//div[contains(@class,'cat_b')]/../span/text()[last()]", pros_xpath = "//p/strong[text()='Pros']/../text()", cons_xpath = "//p/strong[text()='Cons']/../text()", summary_xpath = "//article/div[@class='awr']/p[not(*)][1]//text()", verdict_xpath = "//p/strong[contains(text(),'Verdict') or contains(text(),'Conclusion')]/../following::p[text()][1]//text()", author_xpath = "//div[contains(@class,'cat_b')]/../span/a//text()", title_xpath = "//div[@class='wrp']/h1[contains(@class,'title')]//text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "/ %B %d, %Y", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/carter/alaScrapy/alascrapy/spiders/pinoytechblog_com.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

