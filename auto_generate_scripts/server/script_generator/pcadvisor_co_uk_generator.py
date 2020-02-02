# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Pcadvisor_co_ukSpider", spider_type = "AlaSpider", allowed_domains = "'pcadvisor.co.uk'", start_urls = "'http://www.pcadvisor.co.uk/review/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//a[starts-with(.,'>>')]/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@class='bd']/h2/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//ul[contains(@class,'crumb')]/li[last()-1]/a//text()", category_path_xpath = "//ul[contains(@class,'crumb')]/li[position()<last()]/a//text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "//meta[@property='og:url']/@content", pname_xpath = "//ul[contains(@class,'crumb')]/li[last()]/a//text()", ocn_xpath = "//ul[contains(@class,'crumb')]/li[last()-1]/a//text()", pic_xpath = "//meta[@property='og:image']/@content", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "//meta[@property='og:url']/@content", pname_xpath = "//ul[contains(@class,'crumb')]/li[last()]/a//text()", rating_xpath = "translate(string(number(count(//img[@class='ratings' and contains(@src,'whitestarfilled')])+0.5*count(//img[@class='ratings' and contains(@src,'whiteHalfStar')]))),'0','')", date_xpath = "//time/@datetime", pros_xpath = "", cons_xpath = "", summary_xpath = "//meta[@property='og:description']/@content", verdict_xpath = "//*[contains(.,'VERDICT')]/following-sibling::p[1]/text()", author_xpath = "//meta[@name='author']/@content", title_xpath = "//meta[@property='og:title']/@content", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "5", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "source_internal_id", regex = "((?<=\-)\d{7}(?=\/))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "source_internal_id", regex = "((?<=\-)\d{7}(?=\/))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "ProductName", regex = "(\w.*(?=\sreview))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "ProductName", regex = "(\w.*(?=\sreview))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "TestDateText", regex = "(\d[^/s]*(?=T))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/techadvisor_co_uk.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

