# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Canadahifi_comSpider", spider_type = "AlaSpider", allowed_domains = "'canadahifi.com'", start_urls = "'http://www.canadahifi.com/reviews/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@class='wpb_wrapper']/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//h3[@class='entry-title']/a/@href", level_index = "3", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//div[@class='page-nav']/a[contains(text(),'Next')]/@href", level_index = "2", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "3", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//ul[@class='td-category']/li[last()]//text()", category_path_xpath = "//ul[@class='td-category']/li//text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//header/h1[@class='entry-title']//text()", ocn_xpath = "//ul[@class='td-category']/li//text()", pic_xpath = "//div[contains(@class,'text-content')]//*[//img][1]//img/@src", manuf_xpath = "//strong[contains(text(),'Manufacturer:')]/following-sibling::text()[1]")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "//header/h1[@class='entry-title']//text()", rating_xpath = "", date_xpath = "//ul[@class='td-category']/../time[contains(@class,'entry-date')]//text()", pros_xpath = "", cons_xpath = "", summary_xpath = "//div[contains(@class,'text-content')]/p[not(*)][text()][1]//text()", verdict_xpath = "", author_xpath = "//meta[@name='author']/@content", title_xpath = "//header/h1[@class='entry-title']//text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%b %d, %Y", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/canadahifi_com.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

