# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Knowyourmobile_comSpider", spider_type = "AlaSpider", allowed_domains = "'knowyourmobile.com'", start_urls = "'http://www.knowyourmobile.com/reviews'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@id='content']//div[@class='view-content']//h2/span/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//ul[@class='pager']/li[contains(@class,'pager-next')]/a/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//div[@id='breadcrumbs-inner']/a[last()]//text()", category_path_xpath = "//div[@id='breadcrumbs-inner']/a//text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "//link[@rel='canonical']/@href", pname_xpath = "", ocn_xpath = "//div[@id='breadcrumbs-inner']/a//text()", pic_xpath = "//span[@class='date-display-single']/following::img[1]/@src", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "//link[@rel='canonical']/@href", pname_xpath = "", rating_xpath = "//div[@class='group_details']//div[contains(@class,'star-first')]/span[@class='on']//text()", date_xpath = "//span[@class='date-display-single']/@content", pros_xpath = "//div[@class='field-label'][starts-with(.//text(),'Pros')]/following::div[contains(@class,'field-item')][1]//text()", cons_xpath = "//div[@class='field-label'][starts-with(.//text(),'Cons')]/following::div[contains(@class,'field-item')][1]//text()", summary_xpath = "//div[contains(@class, 'premium')]/p[1]/text()", verdict_xpath = "//div[@class='field-label'][starts-with(.//text(),'Verdict')]/following::div[contains(@class,'field-item')][1]//text()", author_xpath = "//span[contains(@class,'field-name-field-author')]//a//text()", title_xpath = "//h1[@class='title']//text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "source_internal_id", regex = "((?<=/)\d{4,10}(?=/))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "source_internal_id", regex = "((?<=/)\d{4,10}(?=/))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "TestDateText", regex = "(\d{4}-\d{2}-\d{2})", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "5", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_productname_from_title(replace_words = [])
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/knowyourmobile_com.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

