# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Videomaker_enSpider", spider_type = "AlaSpider", allowed_domains = "'videomaker.com'", start_urls = "'https://www.videomaker.com/reviews'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//ul/li//a[img][not (contains(@href,'video'))]/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//a[contains(text(),'next')]/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//h1[contains(@class,'title')]/text()", ocn_xpath = "video", pic_xpath = "//meta[@property='og:image']/@content", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "//h1[contains(@class,'title')]/text()", rating_xpath = "", date_xpath = "//article[@role='article']/span[@property='dc:date dc:created']/@content", pros_xpath = "//h2[strong[contains(text(),'STRENGTHS')or contains(text(),'Strengths')]]/following-sibling::*[1]//text() | //h2[contains(text(),'STRENGTHS')or contains(text(),'Strengths')]/following-sibling::*[1]//text()", cons_xpath = "//h2[strong[contains(text(),'WEAKNESSES')or contains(text(),'Weaknesses')]]/following-sibling::*[1]//text() | //h2[contains(text(),'WEAKNESSES')or contains(text(),'Weaknesses')]/following-sibling::*[1]//text()", summary_xpath = "//meta[@property='og:description']/@content", verdict_xpath = "//h2[contains(text(),'Summary') or contains(text(),'Thoughts') or contains(text(),'BOTTOM LINE') or contains(text(),'Overall') or contains(text(),'Conclusion') or contains(text(),'Bottom Line')]/following-sibling::*[1]/text() ", author_xpath = "//div[contains(@class,'author')]/div/div/text()", title_xpath = "//h1[contains(@class,'title')]/text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "ProductName", regex = "(.*)Review", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%Y-%m-%dT%I:%M:%S-%p", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/videomaker_en.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

