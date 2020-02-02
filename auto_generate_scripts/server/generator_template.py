# -*- coding: utf8 -*-
import jinja2
from conf import source_json


generator_import_template = '''# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()

'''

def generator_import():
    tp = jinja2.Template(generator_import_template)
    generator_import_code = tp.render()
    return generator_import_code

gen_init = '''return_code = spa.gen_init(spider_name = "%s", spider_type = "%s", allowed_domains = "%s", start_urls = "%s")
'''

gen_level = '''return_code = spa.gen_level(level_index = "%s", need_parse_javascript = "%s")
'''

request_single_url = '''return_code = spa.gen_request_single_url(url_xpath = u"%s", level_index = "%s", url_regex = "%s", product_fields = [%s])
'''


request_urls = '''return_code = spa.gen_request_urls(urls_xpath = u"%s", level_index = "%s", url_regex = "%s", include_original_url = "%s", params_xpath = {%s}, params_regex = {%s})
'''

request_containers_urls = '''return_code = spa.gen_request_containers_urls(containers_xpath = u"%s", url_xpath = u"%s", level_index = "%s", params_xpath = {%s}, params_regex = {%s})
'''

gen_product = '''return_code = spa.gen_product(sii_xpath = u"%s", pname_xpath = u"%s", ocn_xpath = u"%s", pic_xpath = u"%s", manuf_xpath = u"%s")
'''

gen_review = '''return_code = spa.gen_review(sii_xpath = u"%s", pname_xpath = u"%s", rating_xpath = u"%s", date_xpath = u"%s", pros_xpath = u"%s", cons_xpath = u"%s", summary_xpath = u"%s", verdict_xpath = u"%s", author_xpath = u"%s", title_xpath = u"%s", award_xpath = u"%s", awpic_xpath = u"%s")
'''

gen_containers_review = '''return_code = spa.gen_containers_review(containers_xpath = u"%s", button_next_javascript = "%s", button_next_xpath = u"%s", sii_xpath = u"%s", pname_xpath = u"%s", rating_xpath = u"%s", date_xpath = u"%s", pros_xpath = u"%s", cons_xpath = u"%s", summary_xpath = u"%s", verdict_xpath = u"%s", author_xpath = u"%s", title_xpath = u"%s", award_xpath = u"%s", awpic_xpath = u"%s")

'''

get_productname_from_title = '''return_code = spa.get_productname_from_title(replace_words = [%s])
'''

get_dbasecategoryname = '''return_code = spa.get_dbasecategoryname(dbcn = "%s")
'''

get_sourcetestscale = '''return_code = spa.get_sourcetestscale(scale = "%s", review_type = "%s")
'''

clean_field = '''return_code = spa.clean_field(type = "%s", field = "%s", regex = "%s", review_type = "%s")
'''

get_fields = '''return_code = spa.get_fields_supplement(in_another_page_xpath = u"%s", test_verdict_xpaths = [%s], pros_xpath = u"%s", cons_xpath = u"%s", rating_xpath = u"%s", award_xpath = u"%s", award_pic_xpath = u"%s")
'''

get_product_id = '''return_code = spa.get_product_id(id_value_xpath = u"%s", id_kind = "%s")
'''

get_category = '''return_code = spa.get_category(category_leaf_xpath = u"%s", category_path_xpath = u"%s")
'''

click = '''return_code = spa.click(target_xpath = u"%s", wait_for_xpath = u"%s", wait_type = "%s")
'''

click_continuous = '''return_code = spa.click_continuous(target_xpath = u"%s", wait_for_xpath = u"%s", wait_type = "%s")
'''

scroll = '''return_code = spa.scroll(wait_for_xpath = u"%s", wait_type = "%s")
'''

generator_append = '''code_fragments.append(return_code)

'''

save_product = '''return_code = spa.save_product()

'''

get_testdatetext = '''return_code = spa.get_testdatetext(replace_words = [%s], format_string = "%s", languages = "%s", review_type = "%s")

'''

save_review = '''return_code = spa.save_review(review_type = "%s")
'''

generator_loop_template = '''script_name = "{{script_name}}"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code.encode('utf-8'))
    fh.write("")
fh.close()


'''

def generator_loop(script_name):
    tp = jinja2.Template(generator_loop_template)
    generator_loop_code = tp.render(script_name = script_name)
    return generator_loop_code

def save_source_json(source_id, source_conf_name, use_proxy = "true"):
    fh = open(source_conf_name, 'w+')
    sjson = source_json % (source_id, use_proxy)
    fh.write(sjson)
    fh.write("")
    fh.close()



