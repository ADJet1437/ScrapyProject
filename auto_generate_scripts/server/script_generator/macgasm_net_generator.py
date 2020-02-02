# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Macgasm_netSpider", spider_type = "AlaSpider", allowed_domains = "'macgasm.net'", start_urls = "'http://www.macgasm.net/category/reviews/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@class='mg-post-title']//h2/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//div[contains(@class,'read-more')]//a/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "'macgasm.net'", category_path_xpath = "'macgasm.net'")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "", ocn_xpath = "'macgasm.net'", pic_xpath = "//div[contains(@class,'mg-post-title-inner')]/following::img[1]/@src", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "", rating_xpath = "translate(//img[contains(@src,'rating')]/@src,'point','.')", date_xpath = "//div[contains(@class,'mg-post-title-inner')]/text() | //div[@class='mg-post-meta']/p//text()", pros_xpath = "(//strong[contains(text(),'good:') or (contains(text(),'What') and contains(text(),'Good'))]/following::text()[1] | //p[contains(text(),'What') and contains(text(),'Good')]//text())[1]", cons_xpath = "(//strong[contains(text(),'sucks:') or (contains(text(),'What') and contains(text(),'Sucks'))]/following::text()[1] | //p[contains(text(),'What') and contains(text(),'Sucks')]//text())[1]", summary_xpath = "//div[contains(@class,'mg-post-title-inner')]/following::p[string-length(text())>5][1]//text()", verdict_xpath = "//p[strong[contains(text(),'Buy it?:')] or contains(text(),'Buy It?:')][1]//text()", author_xpath = "//a[@rel='author']//text()", title_xpath = "//div[contains(@class,'mg-post-title-inner')]/h1//text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_productname_from_title(replace_words = ['Review'])
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "SourceTestRating", regex = "((?<=-)\d.*(?=-))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "5", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%B %d, %Y", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/macgasm_net.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

