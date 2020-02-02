# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Smarthouse_com_auSpider", spider_type = "AlaSpider", allowed_domains = "'smarthouse.com.au'", start_urls = "'http://www.smarthouse.com.au/reviews.aspx'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.scroll(wait_for_xpath = "", wait_type = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[contains(@class, 'row rowid')]/h5/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.scroll(wait_for_xpath = "", wait_type = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//li[contains(@class,'rowid')]/h4/a/@href", level_index = "3", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "3", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "//form[@method='post']/@action", pname_xpath = "", ocn_xpath = "//p[@class='smallcaption']/a[last()]//text()", pic_xpath = "//p[@class='smallcaption']/following::img[1]/@src", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "//form[@method='post']/@action", pname_xpath = "", rating_xpath = "//ul[@class='ratingrow']/li[@class='second']//text()", date_xpath = "//p[@class='smallcaption']/text()[last()-1]", pros_xpath = "((//*[starts-with(text(),'Pros:')]/following::*[.//text()][1]//text() | //*[starts-with(text(),'Pros:')]/following::text()[1]) | //p[starts-with(.//text(),'Pros:')]/following-sibling::p[1]//text())", cons_xpath = "((//*[starts-with(text(),'Cons:')]/following::text()[1] | //*[starts-with(text(),'Cons:')]/following::span[1]//text()) | //p[starts-with(.//text(),'Cons:')]/following-sibling::p[1]//text())", summary_xpath = "//div[@class='outerParagraph']//text()", verdict_xpath = "(//*[starts-with(text(),'Conclusion:')]/following::p[1]//text() | //*[starts-with(text(),'Conclusion:')]/following::text()[1] | //*[starts-with(text(),'Verdict')]/following::p[1]//text())[1]", author_xpath = "//p[@class='smallcaption']/strong//text()", title_xpath = "//h1/text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "source_internal_id", regex = "(([A-Z]|\d)*)", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "source_internal_id", regex = "(([A-Z]|\d)*)", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_productname_from_title(replace_words = ['Review:'])
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "SourceTestRating", regex = "((?<=rating ).+(?=/))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "TestDateText", regex = "(\d{2}/\d{2}/\d{4})", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "TestPros", regex = "((?<=Cons:)|(.*(?=Cons:)))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "5", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%d/%b/%Y", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/smarthouse_com_au.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

