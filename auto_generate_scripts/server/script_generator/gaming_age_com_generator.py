# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Gaming_age_comSpider", spider_type = "AlaSpider", allowed_domains = "'gaming-age.com'", start_urls = "'http://www.gaming-age.com/reviews/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@class='entries-wrapper']//div[contains(@class,'clearfix')]//h2/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//div[contains(@class,'post-nav')]/p[@class='previous']/a/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "", ocn_xpath = "game", pic_xpath = "(//div[contains(@class,'entry-content')]/p[*/img or img][1] | //div[contains(@class,'entry-content')]//a[*/img or img][1])[1]//img/@src", manuf_xpath = "//span[@class='amazon-manufacturer']/text()")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "", rating_xpath = "//div[@class='review_grade']/*//text()", date_xpath = "//p[contains(@class,'post-date-inline')]/abbr[@class='published']//text()", pros_xpath = "", cons_xpath = "", summary_xpath = "//div[contains(@class,'entry-content')]/p[string-length(text())>5][1]//text()", verdict_xpath = "", author_xpath = "//p[contains(@class,'post-author')]/span[contains(@class,'nickname')]//text()", title_xpath = "//h1[contains(@class,'entry-title')]//text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_productname_from_title(replace_words = ['review'])
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "13", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%B %d, %Y", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/gaming_age_com.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

