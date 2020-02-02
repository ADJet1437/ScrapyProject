# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Pclab_plSpider", spider_type = "AlaSpider", allowed_domains = "'pclab.pl'", start_urls = "'http://pclab.pl/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@id='categories']//tr/th/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//div[contains(@class,'last')]/div[@class='offset']/a[@class='active']/following-sibling::a[1]/@href", level_index = "2", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@class='list']/div[starts-with(@class,'element')]/div[@class='title']/a/@href", level_index = "3", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "3", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//div[contains(@class,'breadcrumb')]/a[last()]//text()", category_path_xpath = "//div[contains(@class,'breadcrumb')]/a//text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "//meta[@property='og:url']/@content", pname_xpath = "//h1//text()", ocn_xpath = "", pic_xpath = "//meta[@property='og:image']/@content", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "//meta[@property='og:url']/@content", pname_xpath = "//h1//text()", rating_xpath = "", date_xpath = "//div[@id='text']/div[@class='info']/text()", pros_xpath = "//div[@class='data']/descendant-or-self::div[@class='ps_pros'][1]/ul/li/text() | //tr[./descendant::node()[normalize-space()='Zalety']]/following-sibling::tr[1]/td[1]//li/text()", cons_xpath = "//div[@class='data']/descendant-or-self::div[@class='ps_cons'][1]/ul/li/text() | //tr[./descendant::node()[normalize-space()='Wady']]/following-sibling::tr[1]/td[2]//li/text()", summary_xpath = "//meta[@property='og:description']/@content", verdict_xpath = "", author_xpath = "//div[@id='text']/div[@class='info']/span/text()", title_xpath = "//h1//text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "source_internal_id", regex = "((?<=art)\d*\d)", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "source_internal_id", regex = "((?<=art)\d*\d)", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "TestDateText", regex = "((?<=\,\s)\d.*\d{4}(?=\,\s))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%d %B %Y", languages = "pl", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.get_fields_supplement(in_another_page_xpath = "//div[@class='chapters']//tr/td[./descendant::*/@href][last()]/a/@href", test_verdict_xpaths = ['//div[@class="data"]/descendant-or-self::*[name()="h2" or name()="h3" or name()="h4"][last()]/following::p[string-length(normalize-space())>1][1]//text() | //*[(name()="b" or name()="strong") and (contains(.,"Podsumowanie") or contains(.,"Ocena"))][last()]/following::node()[not(name()) and string-length(normalize-space())>1 and (contains(.,".") or contains(.," ") or contains(.,","))][1] | //p[starts-with(normalize-space(),"Podsumowanie") or contains(.,"Ocena")]/following-sibling::p[string-length(normalize-space())>1][1]//text()'], pros_xpath = "//div[@class='data']/descendant-or-self::div[@class='ps_pros'][1]/ul/li/text() | //tr[./descendant::node()[normalize-space()='Zalety']]/following-sibling::tr[1]/td[1]//li/text()", cons_xpath = "//div[@class='data']/descendant-or-self::div[@class='ps_cons'][1]/ul/li/text() | //tr[./descendant::node()[normalize-space()='Wady']]/following-sibling::tr[1]/td[2]//li/text()", rating_xpath = "", award_xpath = "", award_pic_xpath = "")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/pclab_pl.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

