# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Tecnologia21_comSpider", spider_type = "AlaSpider", allowed_domains = "'tecnologia21.com'", start_urls = "'http://tecnologia21.com/resenas'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = u"//div[@class='navigation']/div[contains(@class,'left')]//a/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = u"//section//article//a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = u"//input[@name='comment_post_ID']/@value", pname_xpath = u"//h1//text()", ocn_xpath = u"//a[contains(@rel,'category')]//text()", pic_xpath = u"//article/descendant-or-self::img[1]/@src", manuf_xpath = u"")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = u"//input[@name='comment_post_ID']/@value", pname_xpath = u"//h1//text()", rating_xpath = u"", date_xpath = u"//p[contains(.,'Fecha:')]//text()", pros_xpath = u"", cons_xpath = u"", summary_xpath = u"normalize-space(//div[@id='noticia' or @name='noticia']/p[string-length(normalize-space())>1][1])", verdict_xpath = u"", author_xpath = u"//p[contains(.,'Autor:')]//text()", title_xpath = u"//h1//text()", award_xpath = u"", awpic_xpath = u"")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "TestDateText", regex = "(\d{2}\/\d{2}\/\d{4})", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "Author", regex = "((?<=Autor\:\s)\w.*\w(?=\s\-))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%d/%m/%y", languages = "es", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/tecnologia21_com.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code.encode('utf-8'))
    fh.write("")
fh.close()

