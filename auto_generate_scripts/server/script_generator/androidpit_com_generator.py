# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Androidpit_comSpider", spider_type = "AlaSpider", allowed_domains = "'androidpit.com'", start_urls = "'https://www.androidpit.com/hardware-reviews'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//div[@class='pages']/a[last()]/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//section[@class='mainContent']/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//h1[contains(@class,'title')]//text()", ocn_xpath = "string(concat(//li[starts-with(.,'Type')]/following-sibling::li//text(),//header/div[1]/span[starts-with(@class,'allLabel')]//text()))", pic_xpath = "//head/meta[contains(@property,'image')][1]/@content", manuf_xpath = "//li[starts-with(.,'Manufacturer')]/following-sibling::li//text()")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "//h1[contains(@class,'title')]//text()", rating_xpath = "//meta[@itemprop='rating']/@content", date_xpath = "substring-before(//time[@itemprop='dtreviewed']/@datetime,'T')", pros_xpath = "//ul[@class='goodList']/li/span[last()]/text()", cons_xpath = "//ul[@class='badList']/li/span[last()]/text()", summary_xpath = "//div[contains(@class,'Intro') and contains(@class,'Content')]/p//text()", verdict_xpath = "//div[contains(@class,'Verdict')]/following-sibling::div/p[1]//text()", author_xpath = "//span[@itemprop='reviewer']//text()", title_xpath = "//h1[contains(@class,'title')]//text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "5", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "ProductName", regex = "(\w.*(?=\shands\s*-*on))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "ProductName", regex = "(\w.*(?=\shands\s*-*on))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "ProductName", regex = "(\w.*(?=\s(r|R)eview))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "ProductName", regex = "(\w.*(?=\s(r|R)eview))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "ProductName", regex = "((?<=Hands.on.)\s?\w.*\w)", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "ProductName", regex = "((?<=Hands.on.)\s?\w.*\w)", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "ProductName", regex = "(\w.*\w(?=:\s))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "ProductName", regex = "(\w.*\w(?=:\s))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "ProductName", regex = "(\w.*\w(?=\s(t|T)est))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "ProductName", regex = "(\w.*\w(?=\s(t|T)est))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/androidpit_com.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

