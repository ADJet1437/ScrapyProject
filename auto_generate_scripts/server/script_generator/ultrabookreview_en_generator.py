# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Ultrabookreview_enSpider", spider_type = "AlaSpider", allowed_domains = "'ultrabookreview.com'", start_urls = "'http://www.ultrabookreview.com/reviews/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//ul[@class='archive-list']//a[img]/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@class='pagination']/a/@href", level_index = "1", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//h1[contains(@class,'headline')]/text()", ocn_xpath = "UltraBook", pic_xpath = "//meta[@property='og:image'][2]/@content", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "//h1[contains(@class,'headline')]/text()", rating_xpath = "//span[@class='rating']/text()", date_xpath = "(//span[@class='updated']/abbr/@title | //span[@class='updated']/text())[1]", pros_xpath = "//p[contains(text(),'GOOD')]/following-sibling::p/text()", cons_xpath = "//p[contains(text(),'BAD')]/following-sibling::p/text()", summary_xpath = "(//span[@class='description']/span/text() | //div[@id='content-area']/p[1]/text())[1] | //h2[text()='Summary']/following-sibling::p[1]/text()", verdict_xpath = "(//h2[contains(text(),'Wrap') or contains(text(),'thoughts')]/following-sibling::p[1]/text()[1] | //h2[@id='a9']/following-sibling::p[1]/text())[1]", author_xpath = "(//span[@class='reviewer']//a/text() | //span[contains(@class,'author')]//a/text())[1]", title_xpath = "//h1[contains(@class,'headline')]/text() ", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "5", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "ProductName", regex = "(.*)review.*", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%b %d, %Y", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/ultrabookreview_en.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

