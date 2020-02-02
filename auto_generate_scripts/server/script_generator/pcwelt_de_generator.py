# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Pcwelt_deSpider", spider_type = "AlaSpider", allowed_domains = "'pcwelt.de'", start_urls = "'http://www.pcwelt.de/computer-technik/tests'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.scroll(wait_for_xpath = "", wait_type = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@class='holder']/a[1]/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//div[@class='breadcrumb']/span[last()]//span[@property='name']/text()", category_path_xpath = "//span[@property='name']/text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "//link[@rel='amphtml']/@href", pname_xpath = "//article/descendant::div[contains(@class,'table-holder') and contains(@class,'linkdb-marker')][1]/table//tr/th[2]/p/text()", ocn_xpath = "//div[@class='breadcrumb']/span[last()]//span[@property='name']/text()", pic_xpath = "//link[@rel='image_src']/@href", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "source_internal_id", regex = "(\d.*\d)", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "//link[@rel='amphtml']/@href", pname_xpath = "//article/descendant::div[contains(@class,'table-holder') and contains(@class,'linkdb-marker')][1]/table//tr/th[2]/p/text()", rating_xpath = "", date_xpath = "//meta[@name='pubdate']/@content", pros_xpath = "//p[contains(.,'Contra')]/preceding-sibling::p//descendant-or-self::*[starts-with(normalize-space(),'+')]//text()", cons_xpath = "//p[contains(.,'Contra')]/following-sibling::p//descendant-or-self::*[starts-with(normalize-space(),'-')]//text()", summary_xpath = "//div[@class='add-box']//strong/text()", verdict_xpath = "//*[contains(.,'Fazit')]/descendant-or-self::*[contains(.,'Fazit')][last()]/following-sibling::p[1]/descendant-or-self::*[text()][1]//text()[1]", author_xpath = "//meta[@name='author']/@content", title_xpath = "//h1[@class='headline']/text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "source_internal_id", regex = "(\d.*\d)", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_productname_from_title(replace_words = ['Test'])
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "ProductName", regex = "((?<=\:\s)\w.*\b|\w.*(?=\sim))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "ProductName", regex = "((?<=\:\s)\w.*\b|\w.*(?=\sim))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/pcwelt_de.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

