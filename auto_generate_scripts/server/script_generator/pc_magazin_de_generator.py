# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Pc_magazin_deSpider", spider_type = "AlaSpider", allowed_domains = "'pc-magazin.de'", start_urls = "'http://www.pc-magazin.de/testbericht/alle'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//h5/a[contains(@class,'link') and @itemprop='url']/@href", level_index = "1", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//h3/a[contains(@class,'link') and @itemprop='url']/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//div[@itemscope][last()]//span/text()", category_path_xpath = "//div[@itemscope]//span/text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "//meta[@property='og:url']/@content", pname_xpath = "//div[@class='active']/*/text()", ocn_xpath = "", pic_xpath = "//div[contains(@class,'main')]/*[.//figure[@itemprop='image']][1]//figure[@itemprop='image']/img/@src", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "//meta[@property='og:url']/@content", pname_xpath = "//div[@class='active']/*/text()", rating_xpath = "translate(string(count(//div[div[contains(@class,'homepagelink')] and @class='row']/preceding::span[contains(@class,'star')][1]/../span[not(contains(@class,'inactive'))])),'0','')", date_xpath = "//span[contains(@class,'date')]/@content", pros_xpath = "//*[starts-with(normalize-space(),'Pro')]/following-sibling::ul/li/text()", cons_xpath = "//*[starts-with(normalize-space(),'Contra')]/following-sibling::ul/li/text()", summary_xpath = "//p[contains(@class,'lead')]/text()", verdict_xpath = "", author_xpath = "//span[@itemprop='author']//span[@itemprop='name']/text()", title_xpath = "//*[contains(@itemprop,'headline')]/text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "5", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "source_internal_id", regex = "((?<=\-)\d*(?=\.html))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "ProductName", regex = "(\w.*(?=\sim))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "source_internal_id", regex = "((?<=\-)\d*(?=\.html))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "ProductName", regex = "(\w.*(?=\sim))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_fields_supplement(in_another_page_xpath = "//div[contains(@class,'pagination') and not(ancestor::div[starts-with(@class,'main')]//*[starts-with(normalize-space(),'Fazit') or starts-with(normalize-space(),'FAZIT') or contains(.,'fazit')])]/a[last()-1]/@href", test_verdict_xpaths = ['string(//*[text()=(//*[starts-with(normalize-space(),"Fazit") or starts-with(normalize-space(),"FAZIT") or contains(.,"fazit")]/../*[(name()="span" and ./preceding-sibling::*[position()=1 and starts-with(.,"Fazit")] and not(//*[name()="p" or name()="h2"][starts-with(.,"Fazit") or starts-with(.,"FAZIT") or contains(.,"fazit")])) or (name()="p" and (starts-with(.,"Fazit") or starts-with(.,"FAZIT") or contains(.,"fazit") or preceding-sibling::h2[starts-with(.,"Fazit") or starts-with(.,"FAZIT") or contains(.,"fazit")]) and not(preceding-sibling::p[preceding-sibling::h2[starts-with(.,"Fazit") or starts-with(.,"FAZIT") or contains(.,"fazit")]]))]//text())])'], pros_xpath = "", cons_xpath = "", rating_xpath = "", award_xpath = "", award_pic_xpath = "")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/pc_magazin_de.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

