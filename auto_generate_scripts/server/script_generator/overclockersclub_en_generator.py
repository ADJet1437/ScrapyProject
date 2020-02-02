# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Overclockersclub_enSpider", spider_type = "AlaSpider", allowed_domains = "'overclockersclub.com'", start_urls = "'http://www.overclockersclub.com/reviews/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//a[@class='small'][contains(@href,'/reviews/')]/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//strong/following-sibling::*[1]/text()", category_path_xpath = "//strong/following-sibling::*[1]/text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//h1/text()", ocn_xpath = "//strong/following-sibling::*[1]/text()", pic_xpath = "(//p[@align='center'][1]/a/img/@src | //div[@id='body']//a/img/@src )[1]", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "//h1/text()", rating_xpath = "", date_xpath = "//time/text()", pros_xpath = "", cons_xpath = "", summary_xpath = "//div[@id='body']//p[1]/text() | //div[@id='body']//font[strong[u[contains(text(),'Introduction')]]]/text() | //div[@id='body']/h2[contains(text(),'Introduction')]/following-sibling::text()[1]", verdict_xpath = "", author_xpath = "//span[@itemprop='name']/text()", title_xpath = "//h1/text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%B %d, %Y", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.get_fields_supplement(in_another_page_xpath = "//ol//li[last()]//a/@href", test_verdict_xpaths = ['//h2[contains(text(),"Conclusion")]/following-sibling::text()[1] | //h2[contains(text(),"Conclusion")]/following-sibling::p[1]/text() | //font[strong[u[contains(text(),"Conclusion")]]]/text()'], pros_xpath = "//h2[contains(text(),'Pros')]/following-sibling::ul[1]/li/text()", cons_xpath = "(//h2[contains(text(),'Cons')]/following-sibling::text() | //h2[contains(text(),'Cons')]/following-sibling::ul[1]/li/text())[last()]", rating_xpath = "", award_xpath = "", award_pic_xpath = "")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/overclockersclub_en.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

