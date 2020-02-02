# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Mobile_review_ruSpider", spider_type = "AlaSpider", allowed_domains = "'mobile-review.com'", start_urls = "'http://www.mobile-review.com/review.shtml'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@class='phonelist']//a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//h1/text()", ocn_xpath = "smartphone", pic_xpath = "//div[@class='article']/img[1]/@src", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "ProductManufacturer", regex = "image//(.+)//.*", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "", rating_xpath = "", date_xpath = "//p[@class='date']/text()", pros_xpath = "", cons_xpath = "", summary_xpath = "//meta[@name='Description']/@content", verdict_xpath = "//h3[contains(@id, 's')][last()]/following-sibling::*[1]/text()", author_xpath = "//p[@align='right']/strong/text()", title_xpath = "//meta[@name='Keywords']/@content", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "TestDateText", regex = ".+ (\d{1,2} .+ \d{4}).+", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%d %b %Y", languages = "ru", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/carter/alaScrapy/alascrapy/spiders/mobile_review_ru.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

