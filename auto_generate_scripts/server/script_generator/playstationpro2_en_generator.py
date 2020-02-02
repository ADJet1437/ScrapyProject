# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Playstationpro2_enSpider", spider_type = "AlaSpider", allowed_domains = "'playstationpro2.com'", start_urls = "'http://www.playstationpro2.com/reviews2.html'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//tr/td[div[@align='center']]//tr//a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//title/text()", ocn_xpath = "game", pic_xpath = "", manuf_xpath = "//p[contains(.,'Publisher')]/text()")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "//title/text()", rating_xpath = "//b[text()='Overall Score']/following-sibling::font[1]/text()", date_xpath = "//td[@id='updates']/a/following-sibling::text()[1]", pros_xpath = "//td[@id='updates']//table//tr/following-sibling::tr/td[1]/text()", cons_xpath = "//td[@id='updates']//table//tr/following-sibling::tr/td[last()]/text()", summary_xpath = "//*[@id='updates']//p[text()][1]/text()", verdict_xpath = "//*[@id='updates']/p[text()][last()-1]/text()", author_xpath = "//td[@id='updates']/a/text()", title_xpath = "//title/text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "TestDateText", regex = " on (.*)", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "SourceTestRating", regex = "(%d\.%d).*", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "10", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%B %d, %Y", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "SourceTestRating", regex = "(\d.?\d?)", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/playstationpro2_en.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

