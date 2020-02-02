# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Techwarelabs_comSpider", spider_type = "AlaSpider", allowed_domains = "'techwarelabs.com'", start_urls = "'http://www.techwarelabs.com/reviews/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[contains(@class,'entry-content')]//ul/li/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "'techwarelabs.com'", category_path_xpath = "'techwarelabs.com'")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "", ocn_xpath = "'techwarelabs.com'", pic_xpath = "//ul[@class='meta']/following::img[1]/@src", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "", rating_xpath = "", date_xpath = "//ul[@class='meta']//span[contains(@class,'updated')]//text()", pros_xpath = "", cons_xpath = "", summary_xpath = "(//ul[@class='meta']/following::p[string-length(.//text())>12][1] | //ul[@class='meta']/following::td[string-length(.//text())>12][1])[1]//text()", verdict_xpath = "//*[starts-with(text(),'Conclusion')]/following::p[string-length(text())>5][1][1]//text()", author_xpath = "//ul[@class='meta']//cite[contains(@class,'author')]//text()", title_xpath = "//div[@id='primary']//h1[@class='entry-title']//text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_productname_from_title(replace_words = ['Review'])
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%B. %d, %Y", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.get_fields_supplement(in_another_page_xpath = "//form[@name='content_jump']/select[@class='contentjumpddl']/option[last()-1]/@value", test_verdict_xpaths = ['//*[starts-with(text(),"Conclusion")]/following::p[string-length(text())>5][1][1]//text()'], pros_xpath = "", cons_xpath = "", rating_xpath = "", award_xpath = "", award_pic_xpath = "")
code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/techwarelabs_com.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

