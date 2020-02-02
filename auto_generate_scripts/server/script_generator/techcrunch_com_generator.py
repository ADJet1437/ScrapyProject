# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Techcrunch_comSpider", spider_type = "AlaSpider", allowed_domains = "'techcrunch.com'", start_urls = "'https://techcrunch.com/reviews/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//li[@class='next']/a/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//h2[@class='post-title']/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "//body/@class", pname_xpath = "", ocn_xpath = "//meta[@property='og:site']/following-sibling::meta[@name='category'][1]/@content", pic_xpath = "//meta[@property='og:image']/@content", manuf_xpath = "//*/*[1]/*[starts-with(@class,'card-title')]/*[not(contains(@href,'/product/'))]/text()")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "//body/@class", pname_xpath = "", rating_xpath = "", date_xpath = "//meta[@data-type='date']/@content", pros_xpath = "//*[normalize-space()='Pros']/following-sibling::*[text()][1]//text()", cons_xpath = "//*[normalize-space()='Cons']/following-sibling::*[text()][1]//text()", summary_xpath = "//meta[@name='excerpt']/@content", verdict_xpath = "//div[starts-with(@class,'article-entry')]/h2[last()]/following-sibling::p[text()][1]/text()", author_xpath = "//a[@rel='author']/text()", title_xpath = "//h1/text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_productname_from_title(replace_words = [])
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "source_internal_id", regex = "((?<=postid-)\d*(?=\s))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "source_internal_id", regex = "((?<=postid-)\d*(?=\s))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "TestSummary", regex = "(\w.*(?=\.))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "TestDateText", regex = "(\d[^\s]*(?=\s))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/techcrunch_com.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

