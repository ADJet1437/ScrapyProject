# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Liliputing_enSpider", spider_type = "AlaSpider", allowed_domains = "'liliputing.com'", start_urls = "'http://liliputing.com/category/reviews'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//h2[@itemprop='headline']/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//a[contains(text(),'Next')]/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//h1[@itemprop='headline']/text()", ocn_xpath = "liliputing.com", pic_xpath = "//meta[@property='og:image'][1]/@content", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "//h1[@itemprop='headline']/text()", rating_xpath = "", date_xpath = "//time[1]/text()", pros_xpath = "", cons_xpath = "", summary_xpath = "//div[@itemprop='text']/p[1]/text()", verdict_xpath = "(//h3[contains(text(),'Verdict')]/following-sibling::p[1]/text() | //div[@itemprop='text']/p[last()-1]/text())[1]", author_xpath = "//a[@rel='author']/span[@itemprop='name']/text()", title_xpath = "//h1[@itemprop='headline']/text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%m/%d/%Y", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/liliputing_en.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

