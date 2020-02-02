# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Mobiflip_deSpider", spider_type = "AlaSpider", allowed_domains = "'mobiflip.de'", start_urls = "'https://www.mobiflip.de/thema/testberichte/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "(//li[@class='infinite-post'] | //div[contains(@class,'feat-top2-left') or contains(@class,'feat-top2-right')])/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//div[@class='pagination']/span[@class='current']/following-sibling::a[1]/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//div[@class='breadcrumbbox']/span[last()]//span[@itemprop='title']//text()", category_path_xpath = "//div[@class='breadcrumbbox']//span[@itemprop='title']//text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "translate(//link[@rel='canonical']/@href,'-',' ')", ocn_xpath = "//div[@class='breadcrumbbox']//span[@itemprop='title']//text()", pic_xpath = "//span[@class='post-date']/following::img[1]/@src", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "translate(//link[@rel='canonical']/@href,'-',' ')", rating_xpath = "//span[@class='rating']//text()", date_xpath = "//time[contains(@class,'post-date')]//text()", pros_xpath = "", cons_xpath = "", summary_xpath = "//span[@class='post-date']/following::p[string-length(.//text())>2][1]//text()", verdict_xpath = "//h2[contains(.//text(),'Fazit')]/following::p[string-length(.//text())>2][1]//text()", author_xpath = "//span[contains(@class,'author-name')]//text()", title_xpath = "//h1[contains(@class,'entry-title')]//text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "5", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "ProductName", regex = "((?<=mobiflip.de/).*(?=/))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "ProductName", regex = "((?<=mobiflip.de/).*(?=/))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "ProductName", regex = "(.*(?= test))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "ProductName", regex = "(.*(?= test))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%d. %B %Y", languages = "de", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/mobiflip_de.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

