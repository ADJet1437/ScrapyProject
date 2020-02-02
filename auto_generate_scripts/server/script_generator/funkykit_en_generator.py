# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Funkykit_enSpider", spider_type = "AlaSpider", allowed_domains = "'funkykit.com'", start_urls = "'http://www.funkykit.com/reviews/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@id='main-content']//a[img]/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//a[contains(@class,'next')]/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//meta[@property='og:title']/@content", ocn_xpath = "", pic_xpath = "//meta[@property='og:image']/@content", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "//meta[@property='og:title']/@content", rating_xpath = "", date_xpath = "//span[contains(@class,'date')]//a/text()", pros_xpath = "", cons_xpath = "", summary_xpath = "//div[contains(@class,'content')]/p[not(img)][text()][1]//text()", verdict_xpath = "", author_xpath = "//a[contains(@href,'author')]/text()", title_xpath = "//meta[@property='og:title']/@content", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%B %d, %Y", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.get_fields_supplement(in_another_page_xpath = "//div[contains(@class,'pagination')]/a[last()]/@href", test_verdict_xpaths = ['//*[contains(.,"Verdict") or contains(.,"Conclusion")]/following-sibling::p[text()][1]//text()' , '//*[contains(.,"Final Words")]/following-sibling::p[text()][1]//text()'], pros_xpath = "//p[contains(.,'Pros')]/following-sibling::ul[1]/li/text() | //td[contains(.,'Pros')]//li/text()", cons_xpath = "//p[contains(.,'Cons')]/following-sibling::ul[1]/li/text() | //td[contains(.,'Cons')]//li/text()", rating_xpath = "", award_xpath = "", award_pic_xpath = "")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/funkykit_en.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

