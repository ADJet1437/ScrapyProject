# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Mobilesyrup_comSpider", spider_type = "AlaSpider", allowed_domains = "'mobilesyrup.com'", start_urls = "'http://mobilesyrup.com/category/reviews/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@class='overview-content']//h2[@class='entry-title']/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "(//ul[@class='page-numbers'])[last()]//a[contains(@class,'next')]/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "", ocn_xpath = "'mobilesyrup.com'", pic_xpath = "//h1[contains(@class,'entry-title')]/following::img[1]/@src", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "", rating_xpath = "//div[contains(@class,'rhs-score')]//text()", date_xpath = "//div[@class='eh-content']/p[last()]//text()", pros_xpath = "//*[name()='h1' or name()='h2' or name()='h3' or name()='h4'][starts-with(.//text(),'Pros')]/following::*[name()='ul'][1]/li//text()", cons_xpath = "//*[name()='h1' or name()='h2' or name()='h3' or name()='h4'][starts-with(.//text(),'Cons')]/following::*[name()='ul'][1]/li//text()", summary_xpath = "//div[@class='eh-content']/following::p[string-length(.//text())>2][1]//text()", verdict_xpath = "//*[starts-with(.//text(),'Conclusion')]/following::p[string-length(.//text())>2][1]//text()", author_xpath = "//div[@class='eh-content']/p[1]//text()", title_xpath = "//h1[contains(@class,'entry-title')]//text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "10", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_productname_from_title(replace_words = ['review'])
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "ProductName", regex = "(.*(?=:))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "ProductName", regex = "(.*(?=:))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%B %d, %Y", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/mobilesyrup_com.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

